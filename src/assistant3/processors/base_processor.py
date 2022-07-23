"""BasePlugin."""
import queue
import typing

import pyttsx3
import spacy

from assistant3.common.exceptions import UidNotAssignedError
from assistant3.common.plugins import PluginResultType, PluginType


class BasePlugin():
    """BasePlugin type."""

    def __init__(self, match: str = '') -> None:
        """Create new BasePlugin object.

        Args:
            match: Text to process.

        """
        self.init_doc = match
        self.spacy_model = spacy.blank('en')
        self.engine = pyttsx3.init()
        self.activation_dict: dict[str, typing.Any] = {
            'docs': [],
            'general_tts_error_message': 'please try again',
            'flow': [{
                'doc_no': 1,
                'tts_error_message': 'please try again',
            }],
        }
        self.uid: object = None
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
        self.min_similarity = 0.75

    def similar_keyword_activated(self, target: object) -> str:
        """Return similar keyword from activation_dict.

        Args:
            target: Text to check similarity against.

        Returns:
            Activation value.

        """
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return 'False'
        activation_similarities = self.get_activation_similarities(target)
        for index, similarity in enumerate(activation_similarities):
            if similarity > self.min_similarity:
                return str(self.activation_dict['docs'][index])
        return 'False'

    def exact_keyword_activated(self, target: object) -> str:
        """Return exact keyword from activation_dict.

        Args:
            target: Text.

        Returns:
            Exact keyword.

        """
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
        """Get text to speech error message.

        Returns:
            Text to speech error message.

        """
        return self.activation_dict['general_tts_error_message']

    def error_spit(self) -> None:
        """Play error response audio."""
        self.engine.say(self.get_general_tts_error_message())
        self.engine.runAndWait()

    def get_activation_similarities(self, target: object) -> list[typing.Any]:
        """Return similarities against activation entries.

        Args:
            target: Text.

        Returns:
            List of similarities.

        """
        for doc in self.activation_dict['docs']:
            print('doc: ', doc)
        return [doc.similarity(target) for doc in self.activation_dict['docs']]

    def is_activated(self, target: object) -> bool:
        """Check if plugin is activated.

        Args:
            target: Text.

        Returns:
            True if plugin is activated.

        """
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False
        activation_similarities = self.get_activation_similarities(target)
        print(activation_similarities)
        return any(
            similarity > self.min_similarity for similarity in activation_similarities
        )

    def init_activation_doc(self) -> None:
        """Add a SpaCy Object to the reference phrases."""
        if self.spacy_model:
            init_doc_obj = self.spacy_model(self.init_doc)
            self.activation_dict['docs'].append(init_doc_obj)

    def add_activation_doc(self, text: str) -> None:
        """Add Activation phrase.

        Args:
            text: Text.

        """
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
        """Set spacy Language model.

        Args:
            model1: SpaCy Language model object.

        """
        self.spacy_model = model1
        self.init_activation_doc()

    def set_uid(self, uid: object) -> None:
        """Set Unique id for plugin.

        Args:
            uid: Unique id.

        """
        if not self.uid:
            self.uid = uid
            self.end_result['uid'] = uid

    def get_uid(self) -> object:
        """Get plugin's unique id.

        Returns:
            Plugin's unique id.

        Raises:
            UidNotAssignedError: not assigned exception.

        """
        if self.uid:
            return self.uid
        raise UidNotAssignedError

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
        if self or by_uid:
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
        """Create new BaseInitializationErrorPlugin object."""
        super().__init__()

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
        ret_str = ''
        ret_str += 'Not implemented, [todo] should raise exception instead\n'
        ret_str += 'doc: '
        ret_str += str(doc.__class__)
        ret_str += '\n'
        ret_str += 'queue: '
        ret_str += str(_queue.__class__)
        ret_str += '\n'
        print(ret_str)


class TriggerPlugin(BasePlugin):
    """TriggerPlugin."""

    def __init__(self) -> None:
        """Create new TriggerPlugin object."""
        super().__init__('hey assistant')
        self.add_activation_doc('he assistant')
        self.add_activation_doc('assistant')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.89
        self.activation_dict[
            'general_tts_error_message'
        ] = 'did not match hey assistant'

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say('how can i help')
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
        activated = self.is_activated(doc)
        print('****', activated)
        if not activated:
            self.end_result['type'] = PluginResultType.ERROR
            self.end_result['result'] = ''
            self.end_result['plugin_type'] = PluginType.TRIGGER_PLUGIN
            self.end_result['result_speech_func'] = self.error_spit
            self.queue.put(self.end_result)
            return
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = 'activated'
        self.end_result['plugin_type'] = PluginType.TRIGGER_PLUGIN
        self.end_result['result_speech_func'] = self.spit
        self.queue.put(self.end_result)
        return
