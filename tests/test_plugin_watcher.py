"""Plugin Watcher Test."""

import processors
import queue
from plugins_watcher import Debug, PluginWatcher

debug = Debug(2, 5)
print(debug.run())

q: queue.Queue[bytes] = queue.Queue()
# plugin object
sdp = processors.base_processor.SpacyDatePlugin()
# trigger plugin object
trigger = processors.base_processor.TriggerPlugin()
# the plugin_watcher object
plugin_watcher = PluginWatcher([sdp])
# optionaly adding a trigger Plugin ("hey assistant")
plugin_watcher.add_trigger_plugin(trigger)

text = 'hey assistant'

res_list = plugin_watcher.run(text)
# res_list[0]['result_speech_func']()

plugin_watcher.add_entry_to_flow_record(res_list[0])

# ret_str = ''
# ret_str += 'returned res_list\n'
# ret_str += str(res_list)
# ret_str += '\n'
# print(ret_str)

print(res_list)
print()
print(res_list[0]['uid'])
print()
print(res_list[0]['type'])

def test_uid() -> None:
    """Test uid for plugins."""
     