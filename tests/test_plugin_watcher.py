"""Plugin Watcher Test."""

import datetime
import queue

import processors
from common.plugins import PluginResultType
from plugins_watcher import PluginWatcher

q: queue.Queue[bytes] = queue.Queue()
# plugin object
sdp = processors.base_processor.SpacyDatePlugin()
# trigger plugin object
trigger = processors.base_processor.TriggerPlugin()
# the plugin_watcher object
plugin_watcher = PluginWatcher([sdp])
# optionaly adding a trigger Plugin ("hey assistant")
plugin_watcher.add_trigger_plugin(trigger)


def test_activation_trigger() -> None:
    """Test activation can only be triggered with exactly 'hey assistant'."""
    text = 'hey assistant'
    res_list = plugin_watcher.run(text)
    print(res_list[0]['result'])
    assert res_list[0]['result'] == 'activated'


def test_other_activation_trigger() -> None:
    """Test activation can only be triggered with exactly 'hey assistant'."""
    activation_words = ['hi assistant', 'hei assistant', 'start programm']
    for word in activation_words:
        res_list = plugin_watcher.run(word)
        assert res_list[0]['type'] == PluginResultType.ERROR


def test_activation_already_triggered() -> None:
    """Test to make sure 'hey assistant' can only be said once."""
    text = 'hey assistant'
    text2 = 'hey assistant'
    res_list = plugin_watcher.run(text)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    assert res_list[0]['type'] == PluginResultType.ERROR


def test_date_plugin() -> None:
    """Test date plugin."""
    text1 = 'hey assistant'
    text2 = 'what date is today'
    res_list = plugin_watcher.run(text1)
    print(res_list[0]['result'])
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    assert res_list[0]['result'] == datetime.datetime.now()
