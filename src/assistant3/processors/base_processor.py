"""BasePlugin."""
import datetime
import queue
import time
import typing

import pyjokes
import pyttsx3
import spacy
import wikipedia

from assistant3.common import plugin_help
from assistant3.common.exceptions import UidNotAssignedError
from assistant3.common.plugins import PluginResultType, PluginType


class BasePlugin():
    """BasePlugin type."""

    def __init__(self, match: str = ''):
        """Create new BasePlugin object.

        Args:
            match: Text to process.

        Returns:
            New BasePlugin instance.

        """
        self.init_doc = match
        self.spacy_model = spacy.blank('en')
        # pyttsx3 object for voice response
        self.engine = pyttsx3.init()
        # this will hold the activation/reference sentence or sentences
        self.activation_dict: dict[str, typing.Any] = {
            'docs': [],
            'general_tts_error_message': 'please try again',
            'flow': [{
                'doc_no': 1,
                'tts_error_message': 'please try again',
            }],
        }
        # unique id

        self.uid: object = None
        # this is the result dict with several informations like
        # - uid
        # - type of the response
        # - suggestion-message
        # ...

        # this is the dict that will be pushed to the results queue
        # when a plugin is activated and finished with processing
        self.end_result: dict[str, typing.Any] = {
            'uid': None,
            'type': PluginResultType.UNDEFINED,
            'plugin_type': PluginType.SYSTEM_PLUGIN,
            'result': None,
            'error_message': '',
            'suggestion_message': '',
            'resession_message': '',
            'result_speech_func': None,
        }

        # default minimum similarity, for a plugin to be activated,
        # this is used by SpaCy and can also be changed in each plugin
        self.min_similarity = 0.75

    def similar_keyword_activated(self, target: object) -> str:
        """Return similar keyword from activation_dict."""
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return 'False'
        activation_similarities = self.get_activation_similarities(target)
        for index, similarity in enumerate(activation_similarities):
            # the logic maybe changed later !
            if similarity > self.min_similarity:
                return str(self.activation_dict['docs'][index])
        return 'False'

    def exact_keyword_activated(self, target: object) -> str:
        """Return exact keyword from activation_dict."""
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return 'False'
        activation_similarities = self.get_activation_similarities(target)
        for index, similarity in enumerate(activation_similarities):
            # the logic maybe changed later !
            if similarity == self.min_similarity:
                print('To return: ', self.activation_dict['docs'][index])
                return str(self.activation_dict['docs'][index])
        return 'False'

    def spit_text(self) -> None:
        """Transform text to speech."""
        self.engine.say(self.end_result['result'])
        self.engine.runAndWait()

    def spit(self) -> None:
        """Play response audio."""
        if self:
            pass
        print('SPIT')

    def get_general_tts_error_message(self) -> object:
        """Empty."""
        return self.activation_dict['general_tts_error_message']

    def error_spit(self) -> None:
        """Play error response audio."""
        self.engine.say(self.get_general_tts_error_message())
        self.engine.runAndWait()

    def get_activation_similarities(self, target: object) -> list[typing.Any]:
        """Return a similarity between 0 and 1.

        list length is the same as how many reference phrases there is
        """
        for doc in self.activation_dict['docs']:
            print('doc: ', doc)
        return [doc.similarity(target) for doc in self.activation_dict['docs']]

    def is_activated(self, target: object) -> bool:
        """Check if a plugin is activated."""
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False
        activation_similarities = self.get_activation_similarities(target)
        print(activation_similarities)
        return any(similarity > self.min_similarity for similarity in activation_similarities)

    def init_activation_doc(self) -> None:
        """Add a SpaCy Object to the reference phrases.

        but only the initial one, to add another one the next function
        'add_activation_doc is used'
        """
        if self.spacy_model:
            init_doc_obj = self.spacy_model(self.init_doc)
            self.activation_dict['docs'].append(init_doc_obj)

    def add_activation_doc(self, text: str) -> None:
        """Add doc from text."""
        if not self.spacy_model:
            return
        self.activation_dict['docs'].append(self.spacy_model(text))

    def list_activation_docs(self) -> None:
        """Print the activation phrases in a plugin."""
        if len(self.activation_dict['docs']) == 0:
            print('[EMPTY]')
        else:
            for doc in self.activation_dict['docs']:
                print(' [DOC TEXT]  ', end='')
                print(doc.text)

    def set_spacy_model(self, model1: spacy.language.Language) -> None:
        """Set spacy model."""
        self.spacy_model = model1
        self.init_activation_doc()

    def set_uid(self, uid: object) -> None:
        """Set UID."""
        if not self.uid:
            self.uid = uid
            self.end_result['uid'] = uid

    def get_uid(self) -> object:
        """Get UID."""
        if self.uid:
            return self.uid
        raise UidNotAssignedError

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid: bool= False) -> None:
        """Run_doc."""
        if self:
            pass

        ret_str = ''
        ret_str += 'Not implemented, [todo] should raise exception instead\n'
        ret_str += 'doc: '
        ret_str += str(doc.__class__)
        ret_str += '\n'
        ret_str += 'queue: '
        ret_str += str(_queue.__class__)
        ret_str += '\n'
        print(ret_str)


class BaseInitializationErrorPlugin(BasePlugin):
    """BaseInitializationErrorPlugin."""

    def __init__(self) -> None:
        """Init."""
        super().__init__()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid: bool= False) -> None:
        """Run_doc."""
        ret_str = ''
        ret_str += 'Not implemented, [todo] should raise exception instead\n'
        ret_str += 'doc: '
        ret_str += str(doc.__class__)
        ret_str += '\n'
        ret_str += 'queue: '
        ret_str += str(_queue.__class__)
        ret_str += '\n'
        print(ret_str)


class SpacyDatePlugin(BasePlugin):
    """SpacyDatePlugin."""

    def __init__(self) -> None:
        """Pass the initial reference phrase to the parent Object (BasePlugin).

        and it will take care of adding it as described
        above
        """
        super().__init__('what is the date')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say(time.strftime('%A %-d of %B'))
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid: bool=False) -> None:
        """Run_doc."""
        self.queue = _queue
        # check if plugin is activted
        activated = self.is_activated(doc)
        if not activated:
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = ''
            self.end_result['result_speech_func'] = self.error_spit
            # here we push it to the results queue passed by pw
            # self.queue.put(self.end_result)
            return
        output_result_value = datetime.datetime.now()
        # here we set some informations in the result dict
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = output_result_value
        self.end_result['result_speech_func'] = self.spit
        # here we push it to the results queue passed by pw
        self.queue.put(self.end_result)
        return


class TriggerPlugin(BasePlugin):
    """TriggerPlugin."""

    def __init__(self) -> None:
        """Init."""
        super().__init__('hey assistant')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99
        self.activation_dict['general_tts_error_message'] = 'did not match hey assistant'

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say('how can i help')
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid: bool=False) -> None:
        """Run_doc."""
        self.queue = _queue
        activated = self.is_activated(doc)
        print('****', activated)
        if not activated:
            self.end_result['type'] = PluginResultType.ERROR
            self.end_result['result'] = ''
            self.end_result['plugin_type'] = PluginType.TRIGGER_PLUGIN
            self.end_result['result_speech_func'] = self.error_spit
            # here we push it to the results queue passed by pw
            self.queue.put(self.end_result)
            return
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = ''
        self.end_result['plugin_type'] = PluginType.TRIGGER_PLUGIN
        self.end_result['result_speech_func'] = self.spit
        self.queue.put(self.end_result)
        return


class Wikipedia(BasePlugin):
    """Plugin for searching something in wikipedia."""

    def __init__(self) -> None:
        """Initialize values."""
        super().__init__('wiki')
        self.activation_dict['general_tts_error_message'] = 'wiki error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99
        self.search_result: list[str] = []
        self.flow: list[str] = []

    def run_doc(self, doc: object, queue_: queue.Queue[typing.Any], by_uid: bool= False) -> None:
        """Run doc."""
        self.queue = queue_

        if self.is_activated(doc) or by_uid:
            if not self.search_result and not self.flow:
                self.end_result['type'] = PluginResultType.KEEP_ALIVE
                self.end_result['result'] = 'what do you want to search in wikipedia'
                self.end_result['result_speech_func'] = super().spit_text
                self.queue.put(self.end_result)
                self.flow.append('one')
                return
            if self.search_result and self.flow:
                if doc[0].text == 'first':
                    print(self.search_result[1])
                    final = wikipedia.summary(self.search_result[1], sentences=2)
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = final
                    self.end_result['result_speech_func'] = super().spit_text
                    self.search_result.clear()
                    self.flow.clear()
                    self.queue.put(self.end_result)
                    return
                elif doc[0].text == 'second':
                    final = wikipedia.summary(self.search_result[2], sentences=2)
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = final
                    self.end_result['result_speech_func'] = super().spit_text
                    self.search_result.clear()
                    self.flow.clear()
                    self.queue.put(self.end_result)
                    return
                elif doc[0].text == 'third':
                    final = wikipedia.summary(self.search_result[3], sentences=2)
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = final
                    self.end_result['result_speech_func'] = super().spit_text
                    self.search_result.clear()
                    self.flow.clear()
                    self.queue.put(self.end_result)
                    return

                else:
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = 'Result not clear please search again'
                    self.end_result['result_speech_func'] = super().spit_text
                    self.search_result.clear()
                    self.flow.clear()
                    self.queue.put(self.end_result)
                    return
            if not self.search_result and self.flow:
                self.search_result = wikipedia.search(doc.text, results=4)
                if len(self.search_result) == 0:
                    self.end_result['type'] = PluginResultType.TEXT
                    self.end_result['result'] = 'no result found'
                    self.end_result['result_speech_func'] = super().spit_text
                    self.search_result.clear()
                    self.flow.clear()
                    self.queue.put(self.end_result)
                    return
                else:
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
        """Pass the initial reference phrase to the parent Object (BasePlugin).

        and it will take care of adding it as described
        above
        """
        super().__init__('location')
        self.add_activation_doc('location')
        self.activation_dict['general_tts_error_message'] = 'location error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid=False) -> None:
        """Run_doc."""
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
        """Pass the initial reference phrase to the parent Object (BasePlugin).

        and it will take care of adding it as described
        above
        """
        super().__init__('i need a joke')
        self.activation_dict['general_tts_error_message'] = 'joke error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.95

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid=False) -> None:
        """Run_doc."""
        self.queue = _queue
        # check if plugin is activted
        activated = self.is_activated(doc) or by_uid
        if activated:
            joke = pyjokes.get_joke(language="en", category="neutral")
            # here we set some informations in the result dict
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = joke
            self.end_result['result_speech_func'] = super().spit_text
            # here we push it to the results queue passed by pw
            self.queue.put(self.end_result)


class Calculator(BasePlugin):
    """Calculator Plugin."""

    def __init__(self) -> None:
        """Pass the initial reference phrase to the parent Object (BasePlugin).

        and it will take care of adding it as described
        above
        """
        super().__init__('calculator')
        self.activation_dict['general_tts_error_message'] = 'calc error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.stack = []
        self.activation = []
        self.min_similarity = 0.99

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid: bool=False) -> None:
        """Run_doc."""
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
                text = f'calculation result is {res}'
                self.stack.clear()
                self.end_result['type'] = PluginResultType.TEXT
                self.end_result['result'] = text
                self.end_result['result_speech_func'] = super().spit_text
                self.activation.clear()
                self.queue.put(self.end_result)
                return


class Internet(BasePlugin):
    """Internet Plugin."""

    def __init__(self) -> None:
        """Pass the initial reference phrase to the parent Object (BasePlugin).

        and it will take care of adding it as described
        above
        """
        super().__init__('internet')
        self.add_activation_doc('internet')
        self.activation_dict['general_tts_error_message'] = 'internet error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid=False) -> None:
        """Run_doc."""
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
            else:
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
        """Pass the initial reference phrase to the parent Object (BasePlugin).

        and it will take care of adding it as described
        above
        """
        super().__init__('volume')
        self.activation_dict['general_tts_error_message'] = 'volume error'
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.activation = []
        self.min_similarity = 0.99

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any], by_uid: bool=False) -> None:
        """Run_doc."""
        self.queue = _queue
        if self.is_activated(doc) or by_uid:
            if not self.activation:
                start_text = 'Do you want to increase or decrease your volume?'
                self.end_result['type'] = PluginResultType.TEXT
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
                    return
                elif doc[0].text == 'decrease':
                    plugin_help.decrease_volume()
                    self.end_result['type'] = PluginResultType.KEEP_ALIVE
                    self.end_result['result'] = 'decreased volume'
                    self.end_result['result_speech_func'] = super().spit_text
                    self.activation.clear()
                    self.queue.put(self.end_result)
                    return
