"""Plugins."""
import queue
import time
import typing

import pyjokes
import spacy
import wikipedia

from assistant3.common import plugin_help
from assistant3.common.plugins import PluginResultType, PluginType
from assistant3.processors.base_processor import BasePlugin


class SpacyDatePlugin(BasePlugin):
    """SpacyDatePlugin."""

    def __init__(self) -> None:
        """Create new SpacyDatePlugin object."""
        super().__init__('what is the date')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say(time.strftime('%A %-d of %B'))
        self.engine.runAndWait()

    def run_doc(
        self,
        doc: spacy.language.Language,
        _queue: queue.Queue[typing.Any],
        by_uid: bool = False,
    ) -> None:
        """Run plugin.

        Args:
            doc: Text recognized.
            _queue: Queue to push results in.
            by_uid: True if plugin is explicitly called by uid.

        """
        self.queue = _queue
        if self.is_activated(doc) or by_uid:
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = 'date given'
            self.end_result['result_speech_func'] = self.spit
            self.queue.put(self.end_result)
            return
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = ''
        self.end_result['result_speech_func'] = self.error_spit
        return


class Wikipedia(BasePlugin):
    """Plugin for searching something in wikipedia."""

    def __init__(self) -> None:
        """Create new Wikipedia object."""
        super().__init__('wiki')
        self.activation_dict['general_tts_error_message'] = 'wiki error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99
        self.search_result: list[str] = []
        self.flow: list[str] = []

    def choose_summary(self, word: str) -> None:
        """Choose summary and pass it on end_result."""
        if word == 'first':
            final = wikipedia.summary(self.search_result[1], sentences=2)
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = final
            self.end_result['result_speech_func'] = super().spit_text
            self.search_result.clear()
            self.flow.clear()
            self.queue.put(self.end_result)
            return
        if word == 'second':
            final = wikipedia.summary(self.search_result[2], sentences=2)
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = final
            self.end_result['result_speech_func'] = super().spit_text
            self.search_result.clear()
            self.flow.clear()
            self.queue.put(self.end_result)
            return
        if word == 'third':
            final = wikipedia.summary(self.search_result[3], sentences=2)
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = final
            self.end_result['result_speech_func'] = super().spit_text
            self.search_result.clear()
            self.flow.clear()
            self.queue.put(self.end_result)
            return

        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = 'Result not clear please search again'
        self.end_result['result_speech_func'] = super().spit_text
        self.search_result.clear()
        self.flow.clear()
        self.queue.put(self.end_result)
        return

    def run_doc(
        self,
        doc: object | typing.Any,
        _queue: queue.Queue[typing.Any],
        by_uid: bool = False,
    ) -> None:
        """Run plugin.

        Args:
            doc: Text recognized.
            _queue: Queue to push results in.
            by_uid: True if plugin is explicitly called by uid.

        """
        self.queue = _queue

        if self.is_activated(doc) or by_uid:
            if not self.search_result and not self.flow:
                self.end_result['type'] = PluginResultType.KEEP_ALIVE
                self.end_result['result'] = 'what do you want to search in wikipedia'
                self.end_result['result_speech_func'] = super().spit_text
                self.queue.put(self.end_result)
                self.flow.append('one')
                return
            if self.search_result and self.flow:
                self.choose_summary(doc[0].text)
            if not self.search_result and self.flow:
                self.search_result = wikipedia.search(doc.text, results=4)

                if len(self.search_result) == 0 and self.flow:
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = 'no result found'
                    self.end_result['result_speech_func'] = super().spit_text
                    self.search_result.clear()
                    self.flow.clear()
                    self.queue.put(self.end_result)
                    return
                self.search_result = [elem + '.' for elem in self.search_result]
                first_res = f'here are the results: first is {self.search_result[1]} \
                , second is {self.search_result[2]}, third is {self.search_result[3]} \
                . which one do you want to chose? tell me first second or third'

                self.end_result['type'] = PluginResultType.KEEP_ALIVE
                self.end_result['result'] = first_res
                self.end_result['result_speech_func'] = super().spit_text
                self.queue.put(self.end_result)
                return


class Location(BasePlugin):
    """Location Plugin."""

    def __init__(self) -> None:
        """Create new Location object."""
        super().__init__('location')
        self.add_activation_doc('location')
        self.activation_dict['general_tts_error_message'] = 'location error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)

    def run_doc(
        self,
        doc: spacy.language.Language,
        _queue: queue.Queue[typing.Any],
        by_uid: bool = False,
    ) -> None:
        """Run plugin.

        Args:
            doc: Text recognized.
            _queue: Queue to push results in.
            by_uid: True if plugin is explicitly called by uid.

        """
        if self.is_activated(doc) or by_uid:
            self.queue = _queue
            loc = plugin_help.locator()
            final_loc = f'your are in {loc}'
            # here we set some informations in the result dict
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = final_loc
            self.end_result['result_speech_func'] = super().spit_text
            # here we push it to the results queue passed by pw
            self.queue.put(self.end_result)


class Jokes(BasePlugin):
    """Gives a random Joke Plugin."""

    def __init__(self) -> None:
        """Create new Jokes object."""
        super().__init__('i need a joke')
        self.activation_dict['general_tts_error_message'] = 'joke error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.95

    def run_doc(
        self,
        doc: spacy.language.Language,
        _queue: queue.Queue[typing.Any],
        by_uid: bool = False,
    ) -> None:
        """Run plugin.

        Args:
            doc: Text recognized.
            _queue: Queue to push results in.
            by_uid: True if plugin is explicitly called by uid.

        """
        self.queue = _queue
        # check if plugin is activted
        activated = self.is_activated(doc) or by_uid
        if activated:
            joke = pyjokes.get_joke(language='en', category='neutral')
            # here we set some informations in the result dict
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = joke
            self.end_result['result_speech_func'] = super().spit_text
            # here we push it to the results queue passed by pw
            self.queue.put(self.end_result)


class Calculator(BasePlugin):
    """Calculator Plugin."""

    def __init__(self) -> None:
        """Create new Jokes object."""
        super().__init__('calculator')
        self.activation_dict['general_tts_error_message'] = 'calc error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.stack: list[typing.Any] = []
        self.activation: list[typing.Any] = []
        self.min_similarity = 0.99

    def run_doc(
        self,
        doc: spacy.language.Language,
        _queue: queue.Queue[typing.Any],
        by_uid: bool = False,
    ) -> None:
        """Run plugin.

        Args:
            doc: Text recognized.
            _queue: Queue to push results in.
            by_uid: True if plugin is explicitly called by uid.

        """
        self.queue = _queue
        if self.is_activated(doc) or by_uid:
            if len(self.stack) == 0 and not self.activation:
                start_text = 'This is calculator plugin, we start by initializing two numbers \
                                and then we intialize the operator. please say the first number'
                self.end_result['type'] = PluginResultType.KEEP_ALIVE
                self.end_result['result'] = start_text
                self.end_result['result_speech_func'] = super().spit_text
                self.activation.append('activate')
                self.queue.put(self.end_result)
                return
            if len(self.stack) == 0 and self.activation:
                value = plugin_help.word_conv(doc.text)
                self.stack.append(value)
                self.end_result['type'] = PluginResultType.KEEP_ALIVE
                self.end_result['result'] = 'please say the second number'
                self.end_result['result_speech_func'] = super().spit_text
                self.queue.put(self.end_result)
                return
            if len(self.stack) == 1 and self.activation:
                value = plugin_help.word_conv(doc.text)
                self.stack.append(value)
                text = f'first number is {self.stack[0]}, and second number is {self.stack[1]} \
                    which operator do you want?'
                self.end_result['type'] = PluginResultType.KEEP_ALIVE
                self.end_result['result'] = text
                self.end_result['result_speech_func'] = super().spit_text
                self.queue.put(self.end_result)
                return
            if len(self.stack) == 2 and self.activation:
                res = plugin_help.run(doc.text, self.stack[0], self.stack[1])
                if isinstance(res, float):
                    text = f'calculation result is {res}'
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = text
                    self.end_result['result_speech_func'] = super().spit_text
                    self.stack.clear()
                    self.activation.clear()
                    self.queue.put(self.end_result)
                    return

                self.end_result['type'] = PluginResultType.TEXT
                self.end_result['result'] = res
                self.end_result['result_speech_func'] = super().spit_text
                self.stack.clear()
                self.activation.clear()
                self.queue.put(self.end_result)
                return


class Internet(BasePlugin):
    """Internet Plugin."""

    def __init__(self) -> None:
        """Create new Internet object."""
        super().__init__('internet')
        self.add_activation_doc('internet')
        self.activation_dict['general_tts_error_message'] = 'internet error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)

    def run_doc(
        self,
        doc: spacy.language.Language,
        _queue: queue.Queue[typing.Any],
        by_uid: bool = False,
    ) -> None:
        """Run plugin.

        Args:
            doc: Text recognized.
            _queue: Queue to push results in.
            by_uid: True if plugin is explicitly called by uid.

        """
        if self.is_activated(doc) or by_uid:
            self.queue = _queue
            if plugin_help.connect():
                # here we set some informations in the result dict
                self.end_result['type'] = PluginResultType.TEXT
                self.end_result['result'] = 'you have internet. Internet plugins are activated'
                self.end_result['result_speech_func'] = super().spit_text
                # here we push it to the results queue passed by pw
                self.queue.put(self.end_result)
                return
            # here we set some informations in the result dict
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = 'you dont have internet'
            self.end_result['result_speech_func'] = super().spit_text
            # here we push it to the results queue passed by pw
            self.queue.put(self.end_result)
            return


class Volume(BasePlugin):
    """Volume Plugin."""

    def __init__(self) -> None:
        """Create new Internet object."""
        super().__init__('volume')
        self.activation_dict['general_tts_error_message'] = 'volume error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.activation: list[str] = []
        self.min_similarity = 0.99

    def run_doc(
        self,
        doc: spacy.language.Language | object,
        _queue: queue.Queue[typing.Any],
        by_uid: bool = False,
    ) -> None:
        """Run plugin.

        Args:
            doc: Text recognized.
            _queue: Queue to push results in.
            by_uid: True if plugin is explicitly called by uid.

        """
        self.queue = _queue
        if self.is_activated(doc) or by_uid:
            if not self.activation:
                start_text = 'Do you want to increase or decrease your volume?'
                self.end_result['type'] = PluginResultType.KEEP_ALIVE
                self.end_result['result'] = start_text
                self.end_result['result_speech_func'] = super().spit_text
                self.activation.append('activate')
                self.queue.put(self.end_result)
                return
            if self.activation:
                if doc[0].text == 'increase':
                    plugin_help.increase_volume()
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = 'increased volume'
                    self.end_result['result_speech_func'] = super().spit_text
                    self.activation.clear()
                    self.queue.put(self.end_result)
                elif doc[0].text == 'decrease':
                    plugin_help.decrease_volume()
                    self.end_result['type'] = PluginResultType.KEEP_ALIVE
                    self.end_result['result'] = 'decreased volume'
                    self.end_result['result_speech_func'] = super().spit_text
                    self.activation.clear()
                    self.queue.put(self.end_result)
                return


class Weather(BasePlugin):
    """Weather Plugin."""

    def __init__(self) -> None:
        """Create new Internet object."""
        super().__init__('Current weather in a city')
        self.activation_dict['general_tts_error_message'] = 'weather error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.75

    def run_doc(
        self,
        doc: spacy.language.Language,
        _queue: queue.Queue[typing.Any],
        by_uid: bool = False,
    ) -> None:
        """Run plugin.

        Args:
            doc: Text recognized.
            _queue: Queue to push results in.
            by_uid: True if plugin is explicitly called by uid.

        """
        self.queue = _queue
        if self.is_activated(doc) or by_uid:
            for ent in doc.ents:
                if ent.label_ == 'GPE':  # GeoPolitical Entity
                    city = ent.text
                else:
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = 'you need to give me a city'
                    self.end_result['result_speech_func'] = super().spit_text
                    self.queue.put(self.end_result)
                    return

            city_weather = str(plugin_help.WeatherMan(city).weather)
            city_temp = str(plugin_help.WeatherMan(city).temperature)
            if city_weather is not None:
                text = f'In {city} the current weather is {city_weather}\
                    , with {city_temp} degrees celcius'
                self.end_result['type'] = PluginResultType.TEXT
                self.end_result['result'] = text
                self.end_result['result_speech_func'] = super().spit_text
                self.queue.put(self.end_result)
                return
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = 'Something went wrong. City name might be wrong'
            self.end_result['result_speech_func'] = super().spit_text
            self.queue.put(self.end_result)
            return
