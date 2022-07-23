"""BasePlugin."""
import queue
import typing

import pyttsx3
import spacy
from word2number import w2n

from ..common.exceptions import UidNotAssignedError
from ..common.plugins import PluginResultType, PluginType
from .bestellung_management import OrderManager
from .manager_tools import ManagerTools


class BasePlugin():
    """Base Class from which all plugins need to inherit."""

    def __init__(self, match: str):
        """Contain the reference initial doc passed later from each plugin.

        Args:
            match: speech text.
    
        """
        # self.order_manager = OrderManager()
        self.order_manager = OrderManager()
        self.manager_tools = ManagerTools()
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
        """Search after similar words.

        Check if input keyword is similar to any of keywords
        and return keyword.

        """
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
        """Find exact keyword.

        Check if given keyword is the same compared to known known keywords.

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
        """Say answer.

        This function sends response to command given by speaker

        """
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

        list length is the same as how many reference phrases there is.

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
        """Set spacy model.

        Args:
            modell: give model.

        """
        self.spacy_model = model1
        self.init_activation_doc()

    def set_uid(self, uid: object) -> None:
        """Set UID.

        Args:
            uid: id from plugin.

        """
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
        super().__init__('')

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
    """Create new order and store it in racks."""

    def __init__(self) -> None:
        """Pass the initial reference phrase to the parent Object (BasePlugin).

        and it will take care of adding it as described
        above.

        """
        super().__init__('add new order')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99

    def spit(self) -> None:
        """Play response audio."""
        self.get_next_item()

    def get_next_item(self) -> None:
        """Say what to do for next step by filling of plug.db."""
        _mtask = self.order_manager.db_object.read_db_plugin()
        if isinstance(_mtask, dict):
            task = _mtask
            for key in task:
                if isinstance(task[key], int | str) and task[key] == 'activ':
                    self.engine.say('please say' + key)
                    self.engine.runAndWait()
                    break
            else:
                self.interrupt_task('stop for dont save')

    def interrupt_task(self, set_control: str) -> None:
        """Set interrupt in plug.db after adding order.

        Args:
            set_control: Sentence to say when add order is done.

        """
        self.manager_tools.set_interrupt_control(2)
        m_list = self.manager_tools.get_order_list()
        self.manager_tools.update_db(m_list)
        self.engine.say(set_control)
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc.

        Args:
            doc: Text from speech recognition.
            _queue: Endresult.

        """
        self.queue = _queue
        _mtask = self.order_manager.db_object.read_db_plugin()
        if isinstance(_mtask, dict):
            task = _mtask
            o_int = self.manager_tools.get_interrupt_control()
            if o_int == 3:
                activated = True
                self.manager_tools.update_db(['activ', '0', '0', 1])
            elif o_int == 0:
                activated = self.is_activated(doc)
                if activated:
                    self.manager_tools.update_db(['activ', '0', '0', 1])
            elif o_int == 1:
                for key in task:
                    if task[key] == '0' and isinstance(task[key], int | str):
                        task[key] = 'activ'
                        break
                _l = self.order_manager.manager_tools.creat_list_order(task)
                self.order_manager.manager_tools.update_db(_l)
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
    """Collect all orders that should be collected.

    If there is no order to collect plugin will stay not activated.

    """

    def __init__(self) -> None:
        """Init."""
        super().__init__('begin collect')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say(self.order_manager.next_object())
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc.

        Args:
            doc: Text from speech recognition.
            _queue: Endresult.
        """
        self.queue = _queue
        next_task = self.order_manager.collect_object.creat_collect_task()
        if isinstance(next_task, int) and next_task == -1:
            activated = False
        else:
            int_o = self.order_manager.manager_tools.get_interrupt_control()
            if int_o == 0:
                activated = self.is_activated(doc)
                if activated:
                    self.order_manager.manager_tools.creat_next_task()
            elif int_o == 4:
                if str(doc) == 'stop':
                    self.order_manager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    activated = True
            elif int_o == 5:
                if str(doc) == 'stop':
                    self.order_manager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    self.order_manager.manager_tools.set_interrupt_control(6)
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


class PickPlugin(BasePlugin):
    """Remove all orders that have not been picked up by the client.

    If workes  has pushed the order already in racks
    than we will recieve informations about the place
    of this order to take it back to wearhous.

    """

    def __init__(self) -> None:
        """Init."""
        super().__init__('begin pick up')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say(self.order_manager.next_pick_object())
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc.

        Args:
            doc: speechText.
            queue: to put some rasults.

        """
        self.queue = _queue
        next_task = self.order_manager.collect_object.creat_pick_task()
        if isinstance(next_task, int) and next_task == -1:
            activated = False
        else:
            k_int = self.manager_tools.get_interrupt_control()
            if k_int == 0:
                activated = self.is_activated(doc)
                if activated:
                    self.manager_tools.creat_pick_task()
            elif self.manager_tools.get_interrupt_control() == 7:
                if str(doc) == 'stop':
                    self.order_manager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    activated = True
            elif self.manager_tools.get_interrupt_control() == 8:
                if str(doc) == 'stop':
                    self.order_manager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    self.manager_tools.set_interrupt_control(9)
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


class MeetClient(BasePlugin):
    """Take id of order from client when he is come to take his order.

    Watch if the workers pushed that order already in racks.
    If yes than we will recieve information about place of order.
    If not the worker will recieve infromation to collect that order. 

    """

    def __init__(self) -> None:
        """Inint."""
        super().__init__('welcome client')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99

    def spit(self) -> None:
        """Play response audio."""
        if self.manager_tools.get_interrupt_control() == 10:
            self.get_next_item()
        elif self.manager_tools.get_interrupt_control() in (11, 13):
            if self.order_manager.client_spit == 'stop':
                self.order_manager.db_object.remove_db_plugin()
            else:
                self.engine.say(self.order_manager.next_client_object())
                self.engine.runAndWait()
        elif self.manager_tools.get_interrupt_control() in (14, 16):
            if self.order_manager.client_spit == 'stop':
                self.order_manager.db_object.remove_db_plugin()
            else:
                self.engine.say(self.order_manager.next_client_collect())
                self.engine.runAndWait()

    def get_next_item(self) -> None:
        """Say what to do for next step in the filling from plug.db."""
        _mtask = self.order_manager.db_object.read_db_plugin()
        if isinstance(_mtask, dict):
            task = _mtask
        for key in task:
            if isinstance(task[key], int | str) and task[key] == 'activ':
                self.engine.say('please say' + 'identification number')
                self.engine.runAndWait()
                break
        else:
            self.interrupt_task()

    def interrupt_task(self) -> None:
        """Say what to do for next step in the filling from plug.db."""
        pick_order = self.check_pick_ability()
        order_id_pick = self.set_order_id()
        _po = order_id_pick
        _lo = self.order_manager.collect_object.pick_order_info(_po)
        _k = self.order_manager.collect_object.collect_order_with_id(_po)
        if pick_order == 'not found':
            self.order_manager.db_object.remove_db_plugin()
            self.engine.say('sorry there is no order with this id')
            self.engine.runAndWait()
        elif isinstance(pick_order, list) and isinstance(_lo, list):
            _lo.append(order_id_pick)
            _lo.append(11)
            order_to_pick = _lo
            self.manager_tools.update_db(order_to_pick)
            self.engine.say('your order ready to pick')
            self.engine.runAndWait()
        elif pick_order == 'not collected' and isinstance(_k, list):
            _k.append(order_id_pick)
            _k.append(14)
            collect_task = _k
            self.manager_tools.update_db(collect_task)
            self.engine.say('sorry we should collect your order')
            self.engine.runAndWait()

    def check_pick_ability(self) -> list[str | int] | str:
        """Give informations about order to pick.

        Returns:
            Return list about order.
        """
        order_id = self.set_order_id()
        _c = order_id
        return self.order_manager.collect_object.pick_order_info(_c)

    def set_order_id(self) -> int:
        """Give order id.

        Returns:
            Return order_id.
        """
        order_id = self.manager_tools.get_order_list()
        for i in range(3):
            order_id[i] = w2n.word_to_num(order_id[i])
        _v = str(order_id[0]) + str(order_id[1]) + str(order_id[2])
        return int(_v)

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc.
        Args:
            doc: speechText.
            queue: to put some rasults.

        """

        self.queue = _queue
        self.order_manager.client_spit = str(doc)
        _mtask = self.order_manager.db_object.read_db_plugin()
        if isinstance(_mtask, dict):
            task = _mtask
        _m = self.manager_tools.get_interrupt_control() == 11
        _n = self.manager_tools.get_interrupt_control() == 14
        if _m or _n:
            activated = True
        elif self.manager_tools.get_interrupt_control() == 12:
            self.manager_tools.set_interrupt_control(13)
            activated = True
        elif self.manager_tools.get_interrupt_control() == 15:
            self.manager_tools.set_interrupt_control(16)
            activated = True
        elif self.manager_tools.get_interrupt_control() == 0:
            activated = self.is_activated(doc)
            if activated:
                self.manager_tools.update_db(['activ', '0', '0', -1, 10])
        elif self.manager_tools.get_interrupt_control() == 10:
            for key in task:
                if task[key] == '0' and isinstance(task[key], int | str):
                    task[key] = 'activ'
                    break
            _f = self.manager_tools.creat_list_order(task)
            self.manager_tools.update_db(_f)
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
        get_status = self.order_manager.get_spit_response_triger()
        # if not get_status:
        if not get_status:
            self.engine.say('how can i help')
            self.engine.runAndWait()
        elif get_status:
            self.engine.say(self.order_manager.order_spit)
            self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        get_status = self.order_manager.check_order_triger(str(doc))
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
