"""assistant3 entry."""
import argparse
import os
import queue
import sys
import typing

import sounddevice as sd
import vosk

import common
import processors
from plugins_watcher import PluginWatcher

feedback_ignore: bool = False
q: queue.Queue[bytes] = queue.Queue()
# plugin object
sdp = processors.base_processor.SpacyDatePlugin()
# trigger plugin object
trigger = processors.base_processor.TriggerPlugin()
# the plugin_watcher object
plugin_watcher = PluginWatcher([sdp])
# optionaly adding a trigger Plugin ("hey assistant")
plugin_watcher.add_trigger_plugin(trigger)


def callback(*args: typing.Iterable[typing.SupportsIndex]) -> None:
    """Push audio data to queue."""
    if args[3]:
        print(args[3], file=sys.stderr)
    if not feedback_ignore:
        q.put(bytes(args[0]))
    else:
        q.put(bytes(0))


def int_or_str(text: str | int) -> str | int:
    """Return integer value from string."""
    try:
        return int(text)
    except ValueError:
        return text


def record(args: argparse.Namespace) -> None:
    """Program loop."""
    global feedback_ignore
    
    try:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])
        vosk_model_path = os.getcwd() + r'/models/vosk-model-small-en-us-0.15'
        model = vosk.Model(vosk_model_path)

        dump_file_exist = bool(args.filename)

        with sd.RawInputStream(
            samplerate=args.samplerate,
            blocksize=8000,
            device=args.device,
            dtype='int16',
            channels=1,
            callback=callback,
        ):
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

                    res_list = plugin_watcher.run(text)
                    print("---->", res_list)
                    feedback_ignore = True
                    res_list[0]['result_speech_func']()
                    feedback_ignore = False

                    plugin_watcher.add_entry_to_flow_record(res_list[0])

                    ret_str = ''
                    ret_str += 'returned res_list\n'
                    ret_str += str(res_list)
                    ret_str += '\n'
                    print(ret_str)

                    """if plugin_watcher.is_trigger_plugin_enabled():
                        if trigger_result:
                            # if there is already a result from the trigger
                            # run plugin_watcher.run and specify True from triggered_now_plugins
                            # to tell it that the trigger was activated and can now
                            # run the plugins
                            res_list = plugin_watcher.run(text, True)
                        else:
                            # not yet triggered, pass False, and should run the trigger
                            # plugin first
                            res_list = plugin_watcher.run(text, False)
                    else:
                        # if trigger not even enabled, run and feed to plugins directely
                        res_list = plugin_watcher.run(text, False)
                    trigger_result = None
                    for result in res_list:
                        # if one result contains a trigger type we check it first
                        # and set it in trigger_result
                        if result['plugin_type'] == common.plugins.PluginType.TRIGGER_PLUGIN:
                            trigger_result = result
                            break

                    end_result = None
                    for result in res_list:
                        if result['plugin_type'] == common.plugins.PluginType.SYSTEM_PLUGIN:
                            end_result = result
                            break

                    if trigger_result:
                        print(trigger_result)
                        feedback_ignore = True
                        trigger_result['result_speech_func']()
                        feedback_ignore = False
                        plugin_watcher.add_entry_to_flow_record(trigger_result)
                        # trigger_result = None
                    if end_result:
                        print(trigger_result)
                        feedback_ignore = True
                        end_result['result_speech_func']()
                        feedback_ignore = False
                        end_result = None
                        plugin_watcher.add_entry_to_flow_record(end_result)"""
                    

                    
                else:
                    print(rec.PartialResult())
                if dump_file_exist:
                    with open(args.filename, 'wb') as dump_fn:
                        dump_fn.write(data)
                # end_result = None
    except KeyboardInterrupt as exc:
        raise KeyboardInterrupt from exc


def main() -> None:
    """Entrypoint to our program, at this level [Speech Recognition Part] we transform.

    audio to text throug 'VOSK' library, briefly: it's an infinite loop (until user interrupts)
    the Program Ctrl+C, where we poll a queue for audio chunks, feed them to vosk library
    and vosk will check with "rec.AcceptWaveform(data):" if the chunks of audio
    recorded can be accepted as a complete sentence, if yes transforms it to text.
    otherwise if the sentence is not yet complete it shows it as partial result
    """
    print('-->')
    sdp.list_activation_docs()
    trigger.list_activation_docs()
    print('<--')
    plugin_watcher.list_plugins_by_uid()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l',
        '--list-devices',
        action='store_true',
        help='show list of audio devices and exit',
    )
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser],
    )
    parser.add_argument(
        '-f',
        '--filename',
        type=str,
        metavar='FILENAME',
        help='audio file to store recording to',
    )
    parser.add_argument(
        '-d',
        '--device',
        type=int_or_str,
        help='input device (numeric ID or substring)',
    )
    args = parser.parse_args(remaining)

    try:
        record(args)
    except KeyboardInterrupt:
        print('\nDone')
        parser.exit(0)


if __name__ == '__main__':
    main()
