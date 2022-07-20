"""Control all order plugins that inherit from BasePlugin."""
from word2number import w2n  # type: ignore

from assistant3.processors.collect_pick import PickAndCollect
from assistant3.processors.make_db import MakeDB
from assistant3.processors.make_racks import MakeRacks
from assistant3.processors.manager_tools import ManagerTools


class OrderManager:
    """Control plugins for order by values set in dictionary from plug.db."""

    def __init__(self) -> None:
        """Create different databases that are needed."""
        self.doc_add = '0'
        self.order_spit = 'nothing'
        self.client_spit = 'nothing'
        self.db_object = MakeDB()
        self.rack_object = MakeRacks()
        self.db_object.make_db_plugin()
        self.db_object.make_db()
        self.collect_object = PickAndCollect()
        self.manager_tools = ManagerTools()

    def check_order_triger(self, doc: str) -> bool:
        """Control the Trigger Plugin to begin conversation.

        We use the value of interrupt_controll from plug.db
        to determinate which plugin will be activated.

        Args:
            doc: Speech text that we recieve from speech recognition.

        Returns:
            Return to trigger plugin True to stay active and False
            to check its similarity sentense.

        """
        task = self.db_object.read_db_plugin()
        self.doc_add = doc
        if len(task) == 0:
            self.db_object.insert_db_plugin(['activ', '0', '0', '0', '0', 0])
            return False
        if len(task) != 0:
            if self.manager_tools.get_interrupt_control() in (1, 2):
                return self.check_add_order_triger(task)
            if self.manager_tools.get_interrupt_control() in (4, 6, 5):
                return self.check_collect_plugin(task)
            if self.manager_tools.get_interrupt_control() in (7, 8, 9):
                return self.check_pick_plugin(task)
            _o = (10, 11, 12, 13, 14, 15, 16)
            if self.manager_tools.get_interrupt_control() in _o:
                return self.check_client_triger(task)
        return False

    def check_add_order_triger(self, task: dict) -> bool:
        """Add new order in Database expl.db and store it in the appropriate place.

        We use Value from interrupt_controll in plug.db
        to determinate which state our plugin have.

        Args:
            task: Dictionary in plug.db.

        Returns:
            Return to trigger plugin True to stay active and false
            to check its similarity sentense.

        """
        if self.manager_tools.get_interrupt_control() == 2:
            if str(self.doc_add) == 'stop':
                self.db_object.remove_db_plugin()
                return False
            return self.manager_tools.store_task_in_racks()
        for key in task:
            _l = self.manager_tools.get_interrupt_control()
            if task[key] == 'activ' and _l == 1:
                if str(self.doc_add) == 'stop':
                    self.db_object.remove_db_plugin()
                    return False
                task[key] = str(self.doc_add)
                _z = self.manager_tools.creat_list_order(task)
                self.manager_tools.update_db(_z)
                return True
        return False

    def check_collect_plugin(self, task: dict) -> bool:
        """Give the employees the orders that still need to be done.

        We use value from interrupt_controll in plug.db
        to determinate which state our plugin have.

        Args:
            task: Dictionary in plug.db.

        Returns:
            Return to trigger plugin True to stay active and false
            to check its similarity sentense.

        """
        int_k = self.manager_tools.get_interrupt_control()
        if int_k == 5:
            if str(self.doc_add) == 'stop':
                self.db_object.remove_db_plugin()
                return False
            self.manager_tools.mark_corridor()
            self.manager_tools.set_interrupt_control(6)
            return True
        for key in task:
            _s = task[key] != 'collected'
            if _s and int_k == 4 and key != 'order_id' and key != 'interrupt':
                if str(self.doc_add) == 'stop':
                    self.db_object.remove_db_plugin()
                    return False
                return True
            if self.manager_tools.get_interrupt_control() == 6:
                bool_value = bool()
                if self.collect_object.creat_collect_task() == -1:
                    bool_value = False
                else:
                    bool_value = True
                return bool_value
        self.interrupt_task()
        return True

    def check_pick_plugin(self, task: dict) -> bool:
        """Take order in racks back to storeroom if client dont come and remove it.

        We use value from interrupt_controll in plug.db
        to determine which state our plugin have.

        Args:
            task: Speech text that we recieve from speech recognition.

        Returns:
            Return to trigger plugin True to stay active and false
            to check its similarity sentense.

        """
        f_interrupt = self.manager_tools.get_interrupt_control()
        if f_interrupt == 8:
            if str(self.doc_add) == 'stop':
                self.db_object.remove_db_plugin()
                return False
            self.manager_tools.mark_pick_corridor()
            self.manager_tools.set_interrupt_control(9)
            return True
        for key in task:
            ignor_item = task[key] != 'collected' and key != 'order_id'
            z_int = self.manager_tools.get_interrupt_control()
            if ignor_item and z_int == 7 and key != 'interrupt':
                if str(self.doc_add) == 'stop':
                    self.db_object.remove_db_plugin()
                    return False
                return True
            if z_int == 9:
                self.collect_object.creat_pick_task()
                return True
        self.interrupt_pick_task()
        return True

    def check_client_triger(self, task: dict) -> bool:
        """Take from Client id and Give him his order.

        We use Value from interrupt_controll in plug.db
        to determinate which state our plugin have.

        Args:
            task: Dictionary in plug.db.

        Returns:
            Return to trigger plugin True to stay active and false
            to check its similarity sentense.

        """
        interrupt_control = self.manager_tools.get_interrupt_control()
        if interrupt_control in (13, 16):
            if str(self.doc_add) == 'stop':
                self.db_object.remove_db_plugin()
                return False
            self.manager_tools.update_db(['0', '0', '0', -1, 10])
            return True
        if interrupt_control == 10:
            return self.check_id_in_conversation(task)
        if interrupt_control in (11, 14):
            return self.check_pick_collect(task)
        return False

    def check_id_in_conversation(self, task: dict) -> bool:
        """Take order_id that we recieve frome speech recognition.

        Put id in doc_add and check it.

        Args:
            task: Dictionary in plug.db.

        Returns:
            Return to trigger plugin True to stay active and False
            to check its similarity sentense if we done with input from id or
            if user says stop.

        """
        try:
            for key in task:
                if task[key] == 'activ':
                    if str(self.doc_add) == 'stop':
                        self.db_object.remove_db_plugin()
                        return False
                    task[key] = str(self.doc_add)
                    test_value = w2n.word_to_num(task[key])
                    test_value = test_value + 1
                    z_list = self.manager_tools.creat_list_order(task)
                    self.manager_tools.update_db(z_list)
                    return True
        except ValueError:
            self.db_object.remove_db_plugin()
            return False
        return True

    def check_pick_collect(self, task: dict) -> bool:
        """Make converstaion for pick if order is collected else collect it.

        We use Value from interrupt_controll in plug.db
        to determinate if we need pick- or collect-plugin.

        Args:
            task: Dictionary in plug.db.

        Returns:
            Return to trigger plugin True to stay active and False
            to check its similarity sentense.

        """
        for key in task:
            ignore_value = key not in ('order_id', 'interrupt')
            if task[key] != 'collected' and ignore_value:
                if str(self.doc_add) == 'stop':
                    self.db_object.remove_db_plugin()
                    return False
                return True
        return True

    def next_object(self) -> str:
        """Specify what collect order should say in conversation.

        Returns:
            Return sentence that speech recognition must say.

        """
        task = self.db_object.read_db_plugin()
        if self.manager_tools.get_interrupt_control() == 6:
            self.manager_tools.mark_corridor()
            if self.collect_object.creat_collect_task() == -1:
                self.db_object.remove_db_plugin()
                return 'no order more'
            self.manager_tools.creat_next_task()
            return 'save completed. next order'
        for key in task:
            ignore_value = key not in ('order_id', 'interrupt')
            state_value = task['interrupt'] == 4
            key_value = str(task[key]) not in 'collected'
            if state_value and key_value and ignore_value:
                order = str(task[key])
                task[key] = 'collected'
                list_c = self.manager_tools.creat_list_order(task)
                self.manager_tools.update_db(list_c)
                return self.manager_tools.creat_sentence(key) + order
        self.interrupt_task()
        return 'stop for dont save'

    def next_element(self) -> str:
        """Specify what collect order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say.

        """
        task = self.db_object.read_db_plugin()
        for key in task:
            ignore_value = key not in ('order_id', 'interrupt')
            state_value = task['interrupt'] == 4
            key_value = str(task[key]) not in 'collected'
            if state_value and key_value and ignore_value:
                return 'next'
        return 'stop for dont save'

    def interrupt_task(self) -> None:
        """Set interrupt in dictionary from plug.db when collect is done."""
        self.manager_tools.set_interrupt_control(5)

    def next_pick_object(self) -> str:
        """Specify what pick order should say in conversation.

        Returns:
            Return sentence that speech recognition must say.

        """
        task = self.db_object.read_db_plugin()
        interrupt_v = self.manager_tools.get_interrupt_control()
        if interrupt_v == 9:
            if self.collect_object.creat_pick_task() == -1:
                self.db_object.remove_db_plugin()
                return 'no order more'
            if self.manager_tools.creat_pick_task() != -1:
                self.manager_tools.mark_pick_corridor()
                self.manager_tools.creat_pick_task()
                return 'save completed. next order'
        for key in task:
            ignore_value = key not in ('order_id', 'interrupt')
            state_value = task['interrupt'] == 7
            key_value = str(task[key]) not in 'collected'
            if state_value and key_value and ignore_value:
                order = str(task[key])
                task[key] = 'collected'
                list_task = self.manager_tools.creat_list_order(task)
                self.manager_tools.update_db(list_task)
                return self.manager_tools.creat_sentence(key) + order
        return 'stop for dont save'

    def next_pick_element(self) -> str:
        """Specify what pick order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say.

        """
        task = self.db_object.read_db_plugin()
        for key in task:
            ignore_value = key not in ('order_id', 'interrupt')
            state_value = task['interrupt'] == 7
            key_value = str(task[key]) not in 'collected'
            if state_value and key_value and ignore_value:
                return 'next'
        self.interrupt_pick_task()
        return 'stop for dont save'

    def interrupt_pick_task(self) -> None:
        """Set interrupt in dictionary from plug.db when pick is done."""
        self.manager_tools.set_interrupt_control(8)

    def next_client_object(self) -> str:
        """Specify what client order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say
            in case of collecting order.

        """
        task = self.db_object.read_db_plugin()
        interrupt_u = self.manager_tools.get_interrupt_control()
        if interrupt_u == 13:
            if str(self.client_spit) == 'stop':
                self.db_object.remove_db_plugin()
                return 'stop'
            self.manager_tools.mark_pick_corridor()
            return 'save completed. next order'

        if interrupt_u == 11:
            for key in task:
                ignore_value = key not in ('order_id', 'interrupt')
                key_value = str(task[key]) not in 'collected'
                if key_value and ignore_value:
                    order = str(task[key])
                    task[key] = 'collected'
                    list_l = self.manager_tools.creat_list_order(task)
                    self.manager_tools.update_db(list_l)
                    return self.manager_tools.creat_sentence(key) + order
            return 'stop for dont save'
        return 'stop for dont save'

    def next_client_element(self) -> str:
        """Specify what client order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say
            in case of pick order.

        """
        task = self.db_object.read_db_plugin()
        for key in task:
            ignore_value = key not in ('order_id', 'interrupt')
            state_value = task['interrupt'] == 11
            key_value = str(task[key]) not in 'collected'
            if state_value and key_value and ignore_value:
                return 'next'
        self.interrupt_client_task()
        return 'stop for dont save'

    def interrupt_client_task(self) -> None:
        """Set interrupt in dictionary from plug.db when pick is done."""
        self.manager_tools.set_interrupt_control(12)

    def next_client_collect(self) -> str:
        """Specify what client order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say
            in case of Taking id order.

        """
        task = self.db_object.read_db_plugin()
        interrupt_n = self.manager_tools.get_interrupt_control()
        if interrupt_n == 16:
            if str(self.client_spit) == 'stop':
                self.db_object.remove_db_plugin()
                return 'stop'
            self.manager_tools.mark_corridor()
            return 'save completed. next order'
        for key in task:
            ignore_value = key not in 'order_id' and key != 'interrupt'
            key_value = str(task[key]) not in 'collected'
            if key_value and ignore_value and interrupt_n == 14:
                order = str(task[key])
                task[key] = 'collected'
                list_g = self.manager_tools.creat_list_order(task)
                self.manager_tools.update_db(list_g)
                return self.manager_tools.creat_sentence(key) + order
        return 'stop for dont save'

    def next_collect_client(self) -> str:
        """Specify what collect order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say
            in case of collecting.

        """
        task = self.db_object.read_db_plugin()
        for key in task:
            ignore_value = key not in ('order_id', 'interrupt')
            state_value = task['interrupt'] == 14
            key_value = str(task[key]) not in 'collected'
            if state_value and key_value and ignore_value:
                return 'next'
        self.interrupt_client_collect()
        return 'stop for dont save'

    def interrupt_client_collect(self) -> None:
        """Set interrupt in dictionary from plug.db when collecting is done."""
        self.manager_tools.set_interrupt_control(15)

    def get_spit_response_triger(self) -> bool:
        """Take Results from other functions and give it to trigger spit.

        Returns:
            Return what trigger should say in all conversations.

        """
        interrup_int = self.manager_tools.get_interrupt_control()
        if interrup_int in (1, 3, 10):
            if interrup_int in (1, 10):
                self.order_spit = 'you gave me' + str(self.doc_add)
            elif interrup_int == 3:
                self.order_spit = 'new order'
        elif interrup_int in list(range(3, 17)) and interrup_int != 10:
            k_str = 'stop for dont save'
            pick_str = self.next_pick_element() in k_str
            element_str = self.next_element() in k_str
            client_1 = self.next_client_element() in k_str
            client_collect = self.next_collect_client() in k_str
            if element_str or pick_str or client_1 or client_collect:
                self.order_spit = k_str
            else:
                self.order_spit = 'next'
        if interrup_int in list(range(1, 17)) and interrup_int != 2:
            return True
        return False
