"""assistent3 entry"""
import argparse
import sounddevice as sd
import vosk
import queue
import os
import sys
from processors import Plugin, DatePlugin, NetworkPlugin
import re

q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def main() -> None:
    plugin = NetworkPlugin()
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
    parser.add_argument(
        '-r', '--samplerate', type=int, help='sampling rate')
    args = parser.parse_args(remaining)

    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])

        model = vosk.Model(r"%s"%(os.getcwd())+r"/models/vosk-model-small-en-us-0.15")

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None

        with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                                channels=1, callback=callback):
                print('#' * 80)
                print('Press Ctrl+C to stop the recording')
                print('#' * 80)

                rec = vosk.KaldiRecognizer(model, args.samplerate)
                while True:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        print("\n")
                        print("\n")
                        print("\n")
                        res = '%s' % rec.Result()
                        text = res.replace('\n', '')
                        text = text.replace('{  "text" : "', '').replace('"}', '')
                        #text = text.replace("{\\n"text" : "")
                        
                        print("\n")
                        print("\n")
                        print("\n")
                        print("__CALL__")
                        print(text.split(' '))
                        o = plugin.run(text.split(' '))
                        print(o)
                        exit()
                    else:
                        print(rec.PartialResult())
                    if dump_fn is not None:
                        dump_fn.write(data)

    except KeyboardInterrupt:
        print('\nDone')
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))

if __name__ == "__main__":
    main()