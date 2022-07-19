"""BasePlugin."""
import datetime
import queue
import time
import typing

import pyttsx3
import spacy

from ..common.exceptions import UidNotAssignedError
from ..common.plugins import PluginResultType, PluginType
from processors.bestellung_management import OrderManager
from word2number import w2n


class BasePlugin():
    """BasePlugin type."""

    def __init__(self, match: str = ''):
        """Create new BasePlugin object.

        Args:
            match: Text to process.

        Returns:
            New BasePlugin instance
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

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
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

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        # check if plugin is activted
        activated = self.is_activated(doc)
        if not activated:
            self.end_result['type'] = PluginResultType.TEXT
            self.end_result['result'] = ''
            self.end_result['result_speech_func'] = self.error_spit
            # here we push it to the results queue passed by pw
            #self.queue.put(self.end_result)
            return
        output_result_value = datetime.datetime.now()
        # here we set some informations in the result dict
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = output_result_value
        self.end_result['result_speech_func'] = self.spit
        # here we push it to the results queue passed by pw
        self.queue.put(self.end_result)
        return


class AddOrderPlugin(BasePlugin):

    def __init__(self) -> None:
        super().__init__('add new order')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99
        #OrderManager.db_object.insert_db_plugin(['activ', '0', '0', 0])

    def spit(self) -> None:
        """Play response audio."""
        self.get_next_item()

    def get_next_item(self):
        """Say what i should do for the next step in the filling from plug.db"""
        task = OrderManager.db_object.read_db_plugin()
        for key in task:
            if task[key] == 'activ':
                self.engine.say('please say' + key)
                self.engine.runAndWait()
                break
        else:
            self.interrupt_task('stop for dont save')

    def interrupt_task(self, set_control: str):
        OrderManager.set_interrupt_control(2)
        OrderManager.update_db(OrderManager.get_order_list())
        self.engine.say(set_control)
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        task = OrderManager.db_object.read_db_plugin()
        if OrderManager.get_interrupt_control() == 3:
            activated = True
            OrderManager.update_db(['activ', '0', '0', 1])
        elif OrderManager.get_interrupt_control() == 0:
            activated = self.is_activated(doc)
            if activated:
                OrderManager.update_db(['activ', '0', '0', 1])
        elif OrderManager.get_interrupt_control() == 1:
            for key in task:
                if task[key] == '0':
                    task[key] = 'activ'
                    break
            OrderManager.update_db(OrderManager.creat_list_order(task))
            activated = True
        else:
            activated = self.is_activated(doc)
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


class CollectOrder(BasePlugin):

    def __init__(self) -> None:
        super().__init__('begin collect')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say(OrderManager.next_object())
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        next_task = OrderManager.collect_object.creat_collect_task()
        if next_task == -1:
            activated = False
        else:
            if OrderManager.get_interrupt_control() == 0:
                activated = self.is_activated(doc)
                if activated:
                    OrderManager.creat_next_task()
            elif OrderManager.get_interrupt_control() == 4:
                if str(doc) == 'stop':
                    OrderManager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    activated = True
            elif OrderManager.get_interrupt_control() == 5:
                if str(doc) == 'stop':
                    OrderManager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    OrderManager.set_interrupt_control(6)
                    activated = True
            else:
                activated = activated = self.is_activated(doc)

        #activated = self.is_activated(doc)
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


class PickPlugin(BasePlugin):

    def __init__(self) -> None:
        super().__init__('begin pick up')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say(OrderManager.next_pick_object())
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        next_task = OrderManager.collect_object.creat_pick_task()
        if next_task == -1:
            activated = False
        else:
            if OrderManager.get_interrupt_control() == 0:
                activated = self.is_activated(doc)
                if activated:
                    OrderManager.creat_pick_task()
            elif OrderManager.get_interrupt_control() == 7:
                if str(doc) == 'stop':
                    OrderManager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    activated = True
            elif OrderManager.get_interrupt_control() == 8:
                if str(doc) == 'stop':
                    OrderManager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    OrderManager.set_interrupt_control(9)
                    activated = True
            else:
                activated = activated = self.is_activated(doc)

        #activated = self.is_activated(doc)
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


class MeetClient(BasePlugin):

    def __init__(self) -> None:
        super().__init__('welcome client')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99
        #OrderManager.db_object.insert_db_plugin(['activ', '0', '0', 0])

    def spit(self) -> None:
        """Play response audio."""
        if OrderManager.get_interrupt_control() == 10:
            self.get_next_item()
        elif OrderManager.get_interrupt_control() in (11, 13):
            if OrderManager.client_spit == 'stop':
                OrderManager.db_object.remove_db_plugin()
            else:
                self.engine.say(OrderManager.next_client_object())
                self.engine.runAndWait()
        elif OrderManager.get_interrupt_control() in (14, 16):
            if OrderManager.client_spit == 'stop':
                OrderManager.db_object.remove_db_plugin()
            else:
                self.engine.say(OrderManager.next_client_collect())
                self.engine.runAndWait()

    def get_next_item(self):
        """Say what i should do for the next step in the filling from plug.db"""
        task = OrderManager.db_object.read_db_plugin()
        for key in task:
            if task[key] == 'activ':
                self.engine.say('please say' + 'identification number')
                self.engine.runAndWait()
                break
        else:
            self.interrupt_task()

    def interrupt_task(self):
        pick_order = self.check_pick_ability()
        order_id_pick = self.set_order_id()
        if pick_order == 'not found':
            OrderManager.db_object.remove_db_plugin()
            self.engine.say('sorry there is no order with this id')
            self.engine.runAndWait()
        elif type(pick_order) == dict:
            order_to_pick = OrderManager.collect_object.pick_order_info(order_id_pick[3])
            #setze interupt auf 11 um mit pick anzufangen
            order_to_pick = dict(order_to_pick, order_id=order_id_pick[3], interrupt=11)
            OrderManager.update_db(OrderManager.creat_list_order(order_to_pick))
            self.engine.say('your order ready to pick')
            self.engine.runAndWait()
        elif pick_order == 'not collected':
            collect_task = OrderManager.collect_object.collect_order_with_id(order_id_pick[3])
            collect_task = dict(collect_task, order_id=order_id_pick[3], interrupt=14)
            OrderManager.update_db(OrderManager.creat_list_order(collect_task))
            self.engine.say('sorry we should collect your order')
            self.engine.runAndWait()

    def check_pick_ability(self):
        order_id = self.set_order_id()
        pick_ability = OrderManager.collect_object.pick_order_info(order_id[3])
        print("check_pick_ability", pick_ability)
        return pick_ability

    def set_order_id(self):
        order_id = OrderManager.get_order_list()
        for i in range(3):
            order_id[i] = w2n.word_to_num(order_id[i])
            print("set_order_id", order_id[i])
        order_id[3] = int(str(order_id[0]) + str(order_id[1]) + str(order_id[2]))
        print("set_order_id", order_id)
        return order_id

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        OrderManager.client_spit = doc
        task = OrderManager.db_object.read_db_plugin()
        if OrderManager.get_interrupt_control() == 11:
            activated = True
        elif OrderManager.get_interrupt_control() == 14:
            activated = True
        elif OrderManager.get_interrupt_control() == 12:
            OrderManager.set_interrupt_control(13)
            activated = True
        elif OrderManager.get_interrupt_control() == 15:
            OrderManager.set_interrupt_control(16)
            activated = True
        elif OrderManager.get_interrupt_control() == 0:
            activated = self.is_activated(doc)
            if activated:
                OrderManager.update_db(['activ', '0', '0', -1, 10])
        elif OrderManager.get_interrupt_control() == 10:
            for key in task:
                if task[key] == '0':
                    task[key] = 'activ'
                    break
            OrderManager.update_db(OrderManager.creat_list_order(task))
            activated = True
        else:
            activated = self.is_activated(doc)
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
        get_status = OrderManager.get_spit_response_triger()
        #if not get_status:
        if not get_status:
            self.engine.say('how can i help')
            self.engine.runAndWait()
        elif get_status:
            self.engine.say(OrderManager.order_spit)
            self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        print(type(doc))
        print('doc: ')
        print(doc)
        get_status = OrderManager.check_order_triger(doc)
        if not get_status:
            activated = self.is_activated(doc)
        elif get_status:
            activated = True

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