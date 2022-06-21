"""assistent3 entry."""
import argparse
import os
import queue

import sounddevice as sd
import vosk
import common
from plugins_watcher import PluginWatcher
from processors import SpacyDatePlugin, TriggerPlugin

q = queue.Queue()


def callback(indata: str, status: str) -> str:
    """
    Call (from a separate thread) for each audio block.

    Args :
        indata: also something
        status: ledig oder verheiratet

    """
    if status:
        pass
    q.put(bytes(indata))


def int_or_str(text: str) -> str:
    """
    Help function for argument parsing.

    Args:
        text: something to test

    Returns:
        Integer or String
    """
    try:
        return int(text)
    except ValueError:
        return text


def main() -> None:
    """
    Entrypoint to our program, at this level [Speech Recognition Part].

    we transform
    audio to text throug 'VOSK' library,
    briefly:
    it's an infinite loop (until user interrupts)
    the Program Ctrl+C, where we poll a queue for audio chunks,
    feed them to vosk library
    and vosk will check
    with "rec.AcceptWaveform(data):" if the chunks of audio
    recorded can be accepted as a complete sentence,
    if yes transforms it to text.
    otherwise if the sentence is not yet complete it shows it as partial
    result.
    """
    # plugin object
    sdp = SpacyDatePlugin()
    # trigger plugin object
    trigger = TriggerPlugin()
    # the p_w object
    p_w = PluginWatcher([sdp])
    # optionaly adding a trigger Plugin ("hey assistant")
    p_w.add_trigger_plugin(trigger)
    sdp.list_activation_docs()
    trigger.list_activation_docs()
    p_w.list_plugins_by_uid()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        '-f', '--filename', type=str, metavar='FILENAME',
        help='audio file to store recording to')
    parser.add_argument(
        '-d', '--device', type=int_or_str,
        help='input device (numeric ID or substring)')
    args = parser.parse_args(remaining)

    try:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])
        path = os.getcwd() + r'/models/vosk-model-small-en-us-0.15'
        model = vosk.Model(path)

        dump_fn_exist = args.filename is True

        with sd.RawInputStream(samplerate=args.samplerate,
                               blocksize=8000,
                               device=args.device, dtype='int16',
                               channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            trigger_result = None
            end_result = None
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    text = res.replace('\n', '')
                    text = text.replace('{  "text" : "', '').replace('"}', '')
                    print(text)

                    # check if p_w has a trigger plugin
                    if p_w.is_trigger_plugin_enabled():
                        if trigger_result:
                            # if there is already a result
                            # from the trigger
                            # run p_w.run and specify True
                            # from triggered_now_plugins
                            # to tell it that the trigger
                            # was activated and can now
                            # run the plugins
                            res_list = p_w.run(text, True)
                        else:
                            # not yet triggered, pass False,
                            # and should run the trigger
                            # plugin first
                            res_list = p_w.run(text, False)

                    else:
                        # if trigger not even enabled,
                        # run and feed to plugins directely
                        res_list = p_w.run(text, False)

                    trigger_result = None
                    for result in res_list:
                        # if one result contains a trigger type we check it
                        # first and set it in trigger_result
                        if result['plugin_type'] == common.PluginType.TRIGGER_PLUGIN:
                            trigger_result = result
                            break

                    end_result = None
                    for result in res_list:
                        if result['plugin_type'] == common.PluginType.SYSTEM_PLUGIN:
                            end_result = result
                            break

                    if trigger_result:
                        print(trigger_result)
                        trigger_result['result_speech_func']()
                        # trigger_result = None

                    if end_result:
                        print(trigger_result)
                        end_result['result_speech_func']()
                        end_result = None

                    # res = p_w.pop_result()
                    # print(res)
                    # res["result_speech_func"]()
                    # exit()
                else:
                    print(rec.PartialResult())
                if dump_fn_exist:
                    with open(args.filename, 'wb') as dump_file:
                        dump_file.write(data)

                # end_result = None

    except KeyboardInterrupt:
        print('\nDone')
        parser.exit(0)
    # except Exception as ex:
    #    parser.exit(type(ex).__name__ + ': ' + str(ex))


if __name__ == '__main__':
    main()
