"""Tests plugins of assistant3."""

import wikipedia

from assistant3 import processors
from assistant3.common import plugin_help
from assistant3.common.plugins import PluginResultType
from assistant3.main_assistant.plugins_watcher import PluginWatcher
from assistant3.processors import plugins


def test_activation_trigger() -> None:
    """Test activation can only be triggered with exactly 'hey assistant'."""
    sdp = plugins.SpacyDatePlugin()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([sdp])
    plugin_watcher.add_trigger_plugin(trigger)
    text = 'hey assistant'
    res_list = plugin_watcher.run(text)
    assert res_list[0]['result'] == 'activated'


def test_other_activation_trigger() -> None:
    """Test activation can only be triggered with exactly 'hey assistant'."""
    sdp = plugins.SpacyDatePlugin()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([sdp])
    plugin_watcher.add_trigger_plugin(trigger)
    activation_words = ['hi assistant', 'hei assistant', 'start programm']
    for word in activation_words:
        res_list = plugin_watcher.run(word)
        assert res_list[0]['type'] == PluginResultType.ERROR


def test_date_plugin() -> None:
    """Test date plugin."""
    sdp = plugins.SpacyDatePlugin()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([sdp])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'what date is today'
    res_list = plugin_watcher.run(text1)
    print(res_list[0]['result'])
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    assert res_list[0]['result'] == 'date given'


def test_joke_plugin() -> None:
    """Test joke plugin."""
    jok = plugins.Jokes()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([jok])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'i need a joke'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    # just make sure that it result is not empty
    assert res_list[0]['result'] is not None


def test_internet_plugin() -> None:
    """Test internet plugin."""
    ite = plugins.Internet()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([ite])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'internet'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)

    if plugin_help.connect():
        assert res_list[0]['result'] == 'you have internet. Internet plugins are activated'
    else:
        assert res_list[0]['result'] == 'you dont have internet'


def test_weather_plugin() -> None:
    """Test weather plugin.

    we'll use münchen in this example and see if it would return the weather in munich
    """
    wet = plugins.Weather()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([wet])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'give me the weather in munich'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    # we set that the desired city is munich
    city = 'munich'
    city_weather = str(plugin_help.WeatherMan(city).weather)
    city_temp = str(plugin_help.WeatherMan(city).temperature)
    text = f'In {city} the current weather is {city_weather}\
                    , with {city_temp} degrees celcius'

    assert res_list[0]['result'] is not None
    assert res_list[0]['result'] == text


def test_spacy_weather_plugin() -> None:
    """Test spacy weather plugin.

    here we check that with help of spacy this plugin could be triggered with different sentences
    """
    wet = plugins.Weather()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([wet])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    # we set that the desired city is munich
    city = 'london'
    city_weather = str(plugin_help.WeatherMan(city).weather)
    city_temp = str(plugin_help.WeatherMan(city).temperature)
    text = f'In {city} the current weather is {city_weather}\
                    , with {city_temp} degrees celcius'

    activation_words = [
        'give me the weather in london',
        'is it going to rain in london',
        'what the weather in london',
    ]
    for word in activation_words:
        res_list = plugin_watcher.run(word)
        assert res_list[0]['result'] is not None
        assert res_list[0]['result'] == text


def test_increase_volume_plugin() -> None:
    """Test volume plugin especially for increasing volume."""
    vol = plugins.Volume()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([vol])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'volume'
    text3 = 'increase'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text3)
    assert res_list[0]['result'] == 'increased volume'


def test_decrease_volume_plugin() -> None:
    """Test volume plugin especially for decreasing volume."""
    vol = plugins.Volume()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([vol])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'volume'
    text3 = 'decrease'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text3)
    assert res_list[0]['result'] == 'decreased volume'


def test_location_plugin() -> None:
    """Test location plugin."""
    loc = plugins.Location()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([loc])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'location'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    # just make sure that it result is not empty
    assert res_list[0]['result'] is not None


def test_wikipedia_plugin_first() -> None:
    """Test wikipedia plugin.

    here we try searching for london and try to see if it could return a summary of
    the desired wikipedia page for the first result
    """
    wik = plugins.Wikipedia()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([wik])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'wiki'
    text3 = 'football'
    decision_word = 'first'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text3)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    search_result = wikipedia.search(text3, results=4)
    res_list = plugin_watcher.run(decision_word)
    final = wikipedia.summary(search_result[1], sentences=2)
    assert res_list[0]['result'] is not None
    assert res_list[0]['result'] == final


def test_wikipedia_plugin_second() -> None:
    """Test wikipedia plugin.

    here we try searching for london and try to see if it could return a summary of
    the desired wikipedia page for the second result
    """
    wik = plugins.Wikipedia()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([wik])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'wiki'
    text3 = 'football'
    decision_word = 'second'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text3)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    search_result = wikipedia.search(text3, results=4)
    res_list = plugin_watcher.run(decision_word)
    final = wikipedia.summary(search_result[2], sentences=2)
    assert res_list[0]['result'] is not None
    assert res_list[0]['result'] == final


def test_wikipedia_plugin_third() -> None:
    """Test wikipedia plugin.

    here we try searching for london and try to see if it could return a summary of
    the desired wikipedia page for the third result
    """
    wik = plugins.Wikipedia()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([wik])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'wiki'
    text3 = 'football'
    decision_word = 'third'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text3)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    search_result = wikipedia.search(text3, results=4)
    res_list = plugin_watcher.run(decision_word)
    final = wikipedia.summary(search_result[3], sentences=2)
    assert res_list[0]['result'] is not None
    assert res_list[0]['result'] == final


def test_break_plugin() -> None:
    """Test breaking plugin with trigger plugin "hey assistant".

    here we try breaking the flow of a plugin by saying "hey assistant" in the middle the process
    we'll use wikipedia plugin to demonstrate this function
    """
    wik = plugins.Wikipedia()
    trigger = processors.base_processor.TriggerPlugin()
    plugin_watcher = PluginWatcher([wik])
    plugin_watcher.add_trigger_plugin(trigger)
    text1 = 'hey assistant'
    text2 = 'wiki'
    text3 = 'hey assistant'
    res_list = plugin_watcher.run(text1)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text2)
    plugin_watcher.add_entry_to_flow_record(res_list[0])
    res_list = plugin_watcher.run(text3)
    assert res_list[0]['result'] is not None
    assert res_list[0]['result'] == 'activated'
