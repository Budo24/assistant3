"""assistant3 entry."""
import argparse
import importlib.resources as resourcesapi
import os
import queue
import socket
import sys
import typing

import sounddevice as sd
import vosk

import assistant3.data

from .. import processors
from ..processors import monthly_plan_plugin
from .plugins_watcher import PluginWatcher


def int_or_str(text: str | int) -> int:
    """Return integer value from string.

    Args:
        text: Number in text format.

    Returns:
        Integer equivalent.

    """
    try:
        return int(text)
    except ValueError:
        return 0


class Assistant3():
    """Main assistant3 application object."""
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 65445

    def __init__(self) -> None:
        """Create Assistant3 object."""
        self.feedback_ignore_obj = False
        self.primary_audio_buffer: queue.Queue[bytes] = queue.Queue()
        # plugin object
        self.sdp = processors.base_processor.SpacyDatePlugin()
        self.mpp = monthly_plan_plugin.MonthlyPlanPlugin()
        self.wik = processors.base_processor.Wikipedia()
        self.loc = processors.base_processor.Location()
        self.jok = processors.base_processor.Jokes()
        self.cal = processors.base_processor.Calculator()
        self.int = processors.base_processor.Internet()
        self.vol = processors.base_processor.Volume()
        self.wet = processors.base_processor.Weather()


        # trigger plugin object
        self.trigger = processors.base_processor.TriggerPlugin()
        # the plugin_watcher object
        self.plugin_watcher = PluginWatcher(
            [self.wik, self.jok, self.loc, self.cal, self.mpp, self.vol, self.wet, self.int]
            )
        # optionaly adding a trigger Plugin ("hey assistant")
        self.plugin_watcher.add_trigger_plugin(self.trigger)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((Assistant3.HOST, Assistant3.PORT))
        self.socket.listen(1)
        conn, addr = self.socket.accept()
        self.conn = conn
        self.addr = addr
            

    def callback(self, *args: typing.Iterable[typing.SupportsIndex]) -> None:
        """Feed audio buffer in sounddevice audio stream.

        Args:
            args: Args specified from sounddevice package.

        """
        if args[3]:
            print(args[3], file=sys.stderr)
        if not self.feedback_ignore_obj:
            self.primary_audio_buffer.put(bytes(args[0]))
        else:
            self.primary_audio_buffer.put(bytes(0))

    def record(self, args: argparse.Namespace) -> None:
        """Assistant3 application main loop.

        Args:
            args: Program parsed cli arguments.

        Raises:
            KeyboardInterrupt: If Ctrl+c is pressed.

        """
        try:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])
            vosk_model_path = resourcesapi.path(
                assistant3.data, 'vosk-model-small-en-us-0.15')
            model = vosk.Model(str(vosk_model_path))

            dump_file_exist = bool(args.filename)

            with sd.RawInputStream(
                samplerate=args.samplerate,
                blocksize=8000,
                device=args.device,
                dtype='int16',
                channels=1,
                callback=self.callback,
            ):
                print('#' * 80)
                print('Press Ctrl+C to stop the recording')
                print('#' * 80)

                rec = vosk.KaldiRecognizer(model, args.samplerate)
                while True:
                    data = self.primary_audio_buffer.get()
                    if rec.AcceptWaveform(data):
                        res = rec.Result()
                        text = res.replace('\n', '')
                        text = text.replace(
                            '{  "text" : "', '').replace('"}', '')
                        print(text)
                        wav_file_path = resourcesapi.path(assistant3.data, 'inter_results.txt')
                        with open(str(wav_file_path), 'w', encoding='utf-8') as w_f:
                            w_f.write(text)
                        self.conn.sendall(b'0000')

                        res_list = self.plugin_watcher.run(text)
                        self.feedback_ignore_obj = True
                        if len(res_list) > 0:
                            res_list[0]['result_speech_func']()
                        self.feedback_ignore_obj = False
                        if len(res_list) > 0:
                            self.plugin_watcher.add_entry_to_flow_record(
                                res_list[0])
                        ret_str = ''
                        ret_str += 'returned res_list\n'
                        ret_str += str(res_list)
                        ret_str += '\n'
                        print(ret_str)

                    else:
                        print(rec.PartialResult())
                        self.conn.sendall(b'0001')
                    if dump_file_exist:
                        with open(args.filename, 'wb') as dump_fn:
                            dump_fn.write(data)
                    # end_result = None
        except KeyboardInterrupt as exc:
            wav_file_path = resourcesapi.path(assistant3.data, 'inter_results.txt')
            with open(str(wav_file_path), 'w', encoding='utf-8') as w_f:
                w_f.write('')
            raise KeyboardInterrupt from exc
        except BrokenPipeError as brkn:
            print('brkn')
            wav_file_path = resourcesapi.path(assistant3.data, 'inter_results.txt')
            with open(str(wav_file_path), 'w', encoding='utf-8') as w_f:
                w_f.write('')
            raise KeyboardInterrupt from brkn
