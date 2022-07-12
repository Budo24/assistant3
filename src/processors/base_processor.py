"""BasePlugin."""
import datetime
import queue
import time
import typing

import pyttsx3
import spacy

from common.exceptions import UidNotAssignedError
from common.plugins import PluginResultType, PluginType
from bestellung_management import OrderManager


class BasePlugin():
    """Base Class from which all plugins need to inherit."""

    def __init__(self, match: str):
        """Contain the reference initial doc passed later from each plugin."""
        #this is hamza benkhayi
        self.order_manager = OrderManager()
        """self.doc_add = '0'
        self.db_object = MakeDB()
        self.rack_object = MakeRacks()
        self.db_object.make_db_plugin()
        self.db_object.make_db()"""
        #en of hamza benkhayi
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

    ##hamza benkhayi

    ##end of hamza

    def spit(self) -> None:
        """Play response audio."""
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

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
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


class BaseInitializationErrorPlugin(BasePlugin):
    """BaseInitializationErrorPlugin."""

    def __init__(self, error_details: dict[str, typing.Any]):
        """Init."""
        self.error_details = error_details
        super().__init__(match='')

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
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


class AddOrderPlugin(BasePlugin):

    def __init__(self) -> None:
        super().__init__('add new order')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99
        self.add_activation_doc('stop')
        #self.order_manager.db_object.insert_db_plugin(['activ', '0', '0', 0])

    def spit(self) -> None:
        """Play response audio."""
        self.get_next_item()

    def get_next_item(self):
        """Say what i should do for the next step in the filling from plug.db"""
        task = self.order_manager.db_object.read_db_plugin()
        for key in task:
            if task[key] == 'activ':
                self.engine.say('please say' + key)
                self.engine.runAndWait()
                break
        else:
            self.interrupt_task('stop for dont save')

    def interrupt_task(self, set_control: str):
        self.order_manager.set_interrupt_control(2)
        self.order_manager.update_db(self.order_manager.get_order_list())
        self.engine.say(set_control)
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        task = self.order_manager.db_object.read_db_plugin()
        if self.order_manager.get_interrupt_control() == 2:
            activated = True
            self.order_manager.update_db(['activ', '0', '0', 1])
        elif self.order_manager.get_interrupt_control() == 0:
            activated = self.is_activated(doc)
            if activated:
                self.order_manager.update_db(['activ', '0', '0', 1])
        elif self.order_manager.get_interrupt_control() == 1:
            for key in task:
                if task[key] == '0':
                    task[key] = 'activ'
                    break
            self.order_manager.update_db(self.order_manager.creat_list_order(task))
            activated = True
        print('****', activated)
        if not activated:
            self.end_result['type'] = PluginResultType.ERROR
            self.end_result['result'] = ''
            self.end_result['result_speech_func'] = self.error_spit
            # here we push it to the results queue passed by pw
            self.queue.put(self.end_result)
            return
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = ''
        self.end_result['plugin_type'] = PluginType.SYSTEM_PLUGIN
        self.end_result['result_speech_func'] = self.spit
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
        if self.order_manager.get_interrupt_control() == 0:
            self.engine.say('how can i help')
            self.engine.runAndWait()
        elif self.order_manager.get_interrupt_control() == 1:
            self.engine.say('you gave me' + str(self.order_manager.doc_add))
            self.engine.runAndWait()
        elif self.order_manager.get_interrupt_control() == 2:
            self.engine.say('new order')
            self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        print("HEEEERRR", doc)
        self.queue = _queue
        task = self.order_manager.db_object.read_db_plugin()
        get_status = self.order_manager.check_add_order_triger(task, doc)
        if get_status == 'task empty':
            activated = self.is_activated(doc)
            if activated:
                self.order_manager.db_object.insert_db_plugin(['activ', '0', '0', 0])
        else:
            if get_status == 'stop is activated. remove the actually order':
                activated = self.is_activated(doc)
            elif get_status == 'we will add new order':
                activated = self.order_manager.stor_task_in_racks()
            else:
                if get_status == 'interrupt plugin AddOrder':
                    activated = self.is_activated(doc)
                elif get_status == 'we will continue with this order':
                    activated = True
                elif get_status == 'we had an order not continued with state not activ. remove it':
                    activated = self.is_activated(doc)
                    if activated:
                        self.order_manager.db_object.insert_db_plugin(['activ', '0', '0', 0])

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
