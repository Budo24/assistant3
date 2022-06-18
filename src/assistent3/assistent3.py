"""assistent3 entry"""
import argparse
import sounddevice as sd
import vosk
import queue
import os
import sys
from processors import DatePlugin, NetworkPlugin, SpacyDatePlugin, TriggerPlugin
import common
from plugins_watcher import PluginWatcher


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
    # entrypoint to our program, at this level [Speech Recognition Part] we transform 
    # audio to text throug 'VOSK' library, briefly: it's an infinite loop (until user interrupts)
    # the Program Ctrl+C, where we poll a queue for audio chunks, feed them to vosk library 
    # and vosk will check with "rec.AcceptWaveform(data):" if the chunks of audio
    # recorded can be accepted as a complete sentence, if yes transforms it to text.
    # otherwise if the sentence is not yet complete it shows it as partial result

    # plugin object
    sdp = SpacyDatePlugin()
    # trigger plugin object
    trigger = TriggerPlugin()
    # the pw object
    pw = PluginWatcher([sdp])
    # optionaly adding a trigger Plugin ("hey assistant")
    pw.add_trigger_plugin(trigger)
    sdp.add_keywords()
    print("-->")
    sdp.list_activation_docs()
    trigger.list_activation_docs()
    print("<--")
    pw.list_plugins_by_uid()
    

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
                trigger_result = None
                end_result = None
                while True:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = '%s' % rec.Result()
                        text = res.replace('\n', '')
                        text = text.replace('{  "text" : "', '').replace('"}', '')
                        print(text)
                        res_list = pw.run(text, True)
                        '''
                        # check if pw has a trigger plugin 
                        if pw.is_trigger_plugin_enabled():
                            if trigger_result:
                                # if there is already a result from the trigger
                                # run pw.run and specify True from triggered_now_plugins
                                # to tell it that the trigger was activated and can now 
                                # run the plugins
                                res_list = pw.run(text, True)
                            else:
                                # not yet triggered, pass False, and should run the trigger
                                # plugin first
                                res_list = pw.run(text, False)
                        else:
                            # if trigger not even enabled, run and feed to plugins directely
                            res_list = pw.run(text, False)
                        '''

                        '''
                        
                        for result in res_list:
                            # if one result contains a trigger type we check it first
                            # and set it in trigger_result
                            if result["plugin_type"] == common.PluginType.TRIGGER_PLUGIN:
                                trigger_result = result
                                break
                            else:
                                trigger_result = None
                        '''
                        for result in res_list:
                            if result["plugin_type"] == common.PluginType.SYSTEM_PLUGIN:
                                end_result = result
                                break
                            else:
                                end_result = None
                        '''
                        if trigger_result:
                            print(trigger_result)
                            trigger_result["result_speech_func"]()
                            #trigger_result = None
                        '''
                            
                        if end_result:
                            print(trigger_result)
                            end_result["result_speech_func"]()
                            end_result = None
                            
                        
                        #res = pw.pop_result()
                        #print(res)
                        #res["result_speech_func"]()
                        #exit()
                    else:
                        print(rec.PartialResult())
                    if dump_fn is not None:
                        dump_fn.write(data)
                    #
                    #end_result = None

    except KeyboardInterrupt:
        print('\nDone')
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))

if __name__ == "__main__":
    main()