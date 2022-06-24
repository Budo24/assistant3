"""BasePlugin."""
import datetime
import queue
import time
import typing

import pyttsx3

import common


class BasePlugin():
    """Base Class from which all plugins need to inherit."""

    def __init__(self, match: str):
        """Contain the reference initial doc passed later from each plugin."""
        self.init_doc = match
        # pyttsx3 object for voice response
        self.engine = pyttsx3.init()
        # this will hold the activation/reference sentence or sentences
        self.activation_dict: dict[str, list[typing.Any]] = {
            'docs': [],
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
            'type': common.plugins.PluginResultType.UNDEFINED,
            'plugin_type': common.plugins.PluginType.SYSTEM_PLUGIN,
            'result': None,
            'error_message': '',
            'suggestion_message': '',
            'resession_message': '',
            'result_speech_func': None,
        }

        # default minimum similarity, for a plugin to be activated,
        # this is used by SpaCy and can also be changed in each plugin
        self.min_similarity = 0.75

    def spit(self) -> None:
        """Play response audio."""
        print('SPIT')

    def get_activation_similarities(self, target: object) -> list[typing.Any]:
        """Return a similarity between 0 and 1.

        list length is the same as how many reference phrases there is
        """
        return [doc.similarity(target) for doc in self.activation_dict['docs']]

    def is_activated(self, target: object) -> bool:
        """Check if a plugin is activated."""
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False
        activation_similarities = self.get_activation_similarities(target)
        print(activation_similarities)
        return bool(similarity > self.min_similarity for similarity in activation_similarities)

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

    def set_spacy_model(self, model: object) -> None:
        """Set spacy model."""
        self.spacy_model = model
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
        raise common.exceptions.UidNotAssignedError

    def run_doc(self, doc: object, queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        ret_str = ''
        ret_str += 'Not implemented, [todo] should raise exception instead\n'
        ret_str += 'doc: '
        ret_str += str(doc.__class__)
        ret_str += '\n'
        ret_str += 'queue: '
        ret_str += str(queue.__class__)
        ret_str += '\n'
        print(ret_str)


class BaseInitializationErrorPlugin(BasePlugin):
    """BaseInitializationErrorPlugin."""

    def __init__(self, error_details: dict[str, typing.Any]):
        """Init."""
        self.error_details = error_details
        super().__init__(match='')

    def run_doc(self, doc: object, queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        ret_str = ''
        ret_str += 'Not implemented, [todo] should raise exception instead\n'
        ret_str += 'doc: '
        ret_str += str(doc.__class__)
        ret_str += '\n'
        ret_str += 'queue: '
        ret_str += str(queue.__class__)
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
        print(time.strftime('%c'))
        self.engine.say(time.strftime('%c'))
        self.engine.runAndWait()

    def run_doc(self, doc: object, queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = queue
        # check if plugin is activted
        activated = self.is_activated(doc)
        if not activated:
            print('***')
            return
        output_result_value = datetime.datetime.now()
        # here we set some informations in the result dict
        self.end_result['type'] = common.plugins.PluginResultType.TEXT
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

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say('how can i help')
        self.engine.runAndWait()

    def run_doc(self, doc: object, queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = queue
        activated = self.is_activated(doc)
        if not activated:
            print('***')
            return
        self.end_result['type'] = common.plugins.PluginResultType.TEXT
        self.end_result['result'] = datetime.datetime.now()
        self.end_result['plugin_type'] = common.plugins.PluginType.TRIGGER_PLUGIN
        self.end_result['result_speech_func'] = self.spit
        self.queue.put(self.end_result)
        return
