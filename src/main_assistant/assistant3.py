"""assistant3 entry."""
import argparse
import importlib.resources as resourcesapi
import queue
import sys
import typing

import sounddevice as sd
import vosk

import data

import processors
import main_assistant


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

    def __init__(self) -> None:
        """Create Assistant3 object."""
        self.feedback_ignore_obj = False
        self.db_object = processors.make_db.MakeDB()
        self.primary_audio_buffer: queue.Queue[bytes] = queue.Queue()
        # plugin object
        self.aop = processors.base_processor.AddOrderPlugin()
        self.cop = processors.base_processor.CollectOrder()
        self.pop = processors.base_processor.PickPlugin()
        self.mcp = processors.base_processor.MeetClient()
        self.sdp = processors.base_processor.SpacyDatePlugin()
        self.mpp = processors.base_processor.MonthlyPlanPlugin()

        # trigger plugin object
        self.trigger = processors.base_processor.TriggerPlugin()
        # the plugin_watcher object
        self.plugin_watcher = main_assistant.plugins_watcher.PluginWatcher([self.mcp])
        # optionaly adding a trigger Plugin ("hey assistant")
        self.plugin_watcher.add_trigger_plugin(self.trigger)

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
            vosk_model_path = resourcesapi.path(assistant3.data, 'vosk-model-small-en-us-0.15')
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
                        text = text.replace('{  "text" : "', '').replace('"}', '')
                        print(text)

                        res_list = self.plugin_watcher.run2(text)
                        self.feedback_ignore_obj = True
                        res_list[0]['result_speech_func']()
                        self.feedback_ignore_obj = False

                        self.plugin_watcher.add_entry_to_flow_record(res_list[0])

                        ret_str = ''
                        ret_str += 'returned res_list\n'
                        ret_str += str(res_list)
                        ret_str += '\n'
                        print(ret_str)

                    else:
                        print(rec.PartialResult())
                    if dump_file_exist:
                        with open(args.filename, 'wb') as dump_fn:
                            dump_fn.write(data)
                    # end_result = None
        except KeyboardInterrupt as exc:
            raise KeyboardInterrupt from exc
