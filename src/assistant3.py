"""assistant3 entry."""
import argparse
import os
import queue
import sys
import typing

import sounddevice as sd
import vosk

import processors
from plugins_watcher import FeedbackIgnore, PluginWatcher

feedback_ignore_obj = FeedbackIgnore()
q: queue.Queue[bytes] = queue.Queue()


def callback(*args: typing.Iterable[typing.SupportsIndex]) -> None:
    """Push audio data to queue."""
    if args[3]:
        print(args[3], file=sys.stderr)
    if not feedback_ignore_obj.get_feedback_ignore():
        q.put(bytes(args[0]))
    else:
        q.put(bytes(0))


def int_or_str(text: str | int) -> str | int:
    """Return integer value from string."""
    try:
        return int(text)
    except ValueError:
        return text


def arg_parser():
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

    return args, parser


def record(args: argparse.Namespace) -> str:
    """Program loop."""
    vosk_model_path = os.getcwd() + r'/models/vosk-model-small-en-us-0.15'
    model = vosk.Model(vosk_model_path)
    dump_file_exist = bool(args.filename)
    rec = vosk.KaldiRecognizer(model, args.samplerate)

    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            res = rec.Result()
            text = res.replace('\n', '')
            text = text.replace('{  "text" : "', '').replace('"}', '')

            return text

        print(rec.PartialResult())
        if dump_file_exist:
            with open(args.filename, 'wb') as dump_fn:
                dump_fn.write(data)


def plugin_runner(text: str, plugin_watcher) -> None:
    """Send text to run plugins."""
    res_list = plugin_watcher.run(text)
    feedback_ignore_obj.toggle_feedback_ignore()
    res_list[0]['result_speech_func']()
    feedback_ignore_obj.toggle_feedback_ignore()

    plugin_watcher.add_entry_to_flow_record(res_list[0])

    ret_str = ''
    ret_str += 'returned res_list\n'
    ret_str += str(res_list)
    ret_str += '\n'
    print(ret_str)


def main() -> None:
    """Entrypoint to our program, at this level [Speech Recognition Part] we transform.

    audio to text throug 'VOSK' library, briefly: it's an infinite loop (until user interrupts)
    the Program Ctrl+C, where we poll a queue for audio chunks, feed them to vosk library
    and vosk will check with "rec.AcceptWaveform(data):" if the chunks of audio
    recorded can be accepted as a complete sentence, if yes transforms it to text.
    otherwise if the sentence is not yet complete it shows it as partial result
    """
    # plugin object
    sdp = processors.base_processor.SpacyDatePlugin()
    # trigger plugin object
    trigger = processors.base_processor.TriggerPlugin()
    # the plugin_watcher object
    plugin_watcher = PluginWatcher([sdp])
    # optionaly adding a trigger Plugin ("hey assistant")
    plugin_watcher.add_trigger_plugin(trigger)

    args, parser = arg_parser()

    while True:

        try:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])
            # vosk_model_path = os.getcwd() + r'/models/vosk-model-small-en-us-0.15'
            # model = vosk.Model(vosk_model_path)

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

                # rec = vosk.KaldiRecognizer(model, args.samplerate)
                text = record(args)
                if text is not None:
                    plugin_runner(text, plugin_watcher)

        except KeyboardInterrupt:
            print('\nDone')
            parser.exit(0)


if __name__ == '__main__':
    main()
