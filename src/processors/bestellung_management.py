"""Control all order plugins that inherit from BasePlugin."""
import typing

from word2number import w2n

from processors.collect_pick import PickAndCollect
from processors.make_db import MakeDB
from processors.make_racks import MakeRacks


class OrderManager:
    """Control plugins for order by values set in dictionary from plug.db."""

    def __init__(self: object) -> None:
        """Create different databases that are needed."""
        self.doc_add = '0'
        self.order_spit = 'nothing'
        self.client_spit = 'nothing'
        self.db_object = MakeDB()
        self.rack_object = MakeRacks()
        self.db_object.make_db_plugin()
        self.db_object.make_db()
        self.collect_object = PickAndCollect()

    def get_order_list(self: object) -> list:
        """Unpack the contents of the dictionary in plug.db.

        Returns:
            List of values from the dictionary in plug.db.
        """
        task = self.db_object.read_db_plugin()
        plug_order = []
        for key in task:
            plug_order.append(task[key])
        return plug_order

    def creat_list_order(self: object, get_task: dict) -> list:
        """Unpack the contents of the dictionary get_task.

        Dictionary get_task comes from plug.db.

        Args:
            get_task: A dictionary will be in plug.db inserted.

        Returns:
            List of Values from the dictionary in plug.db.
        """
        plug_order = []
        for key in get_task:
            plug_order.append(get_task[key])
        return plug_order

    def update_db(self: object, plug_order: list) -> None:
        """Remove the older dictionary in plug.db and Input a new update.

        List plug_order comes from plug.db.

        Args:
            plug_order: A list will be in plug.db inserted.
        """
        self.db_object.remove_db_plugin()
        self.db_object.insert_db_plugin(plug_order)

    def get_interrupt_control(self: object) -> int:
        """Get the Value of interrupt in the dictionary in plug.db.

        Returns:
            Value from interrupt.
        """
        task = self.db_object.read_db_plugin()
        if len(task) == 0:
            return False
        else:
            return task['interrupt']

    def set_interrupt_control(self: object, interrupt_contorl: int) -> None:
        """Set the Value of interrupt in the dictionary in plug.db.

        This integer value comes from plug.db.
        With this value we can determine the states of the conversation.

        Args:
            interrupt_contorl: A integer Value.
        """
        task = self.db_object.read_db_plugin()
        if len(task) != 0:
            task['interrupt'] = interrupt_contorl
            self.update_db(self.creat_list_order(task))

    def check_order_triger(self: object, doc: typing.Any) -> bool:
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
        elif len(task) != 0:
            if self.get_interrupt_control() in (1, 2):
                return self.check_add_order_triger(task)
            elif self.get_interrupt_control() in (4, 6, 5):
                return self.check_collect_plugin(task)
            elif self.get_interrupt_control() in (7, 8, 9):
                return self.check_pick_plugin(task)
            elif self.get_interrupt_control() in (10, 11, 12, 13, 14, 15, 16):
                return self.check_client_triger(task)
        return False

    def check_add_order_triger(self: object, task: dict) -> bool:
        """Add new order in Database expl.db and store it in the appropriate place.

        We use Value from interrupt_controll in plug.db
        to determinate which state our plugin have.

        Args:
            task: Dictionary in plug.db.

        Returns:
            Return to trigger plugin True to stay active and false
            to check its similarity sentense.
        """
        if self.get_interrupt_control() == 2:
            if str(self.doc_add) == 'stop':
                self.db_object.remove_db_plugin()
                return False
            else:
                return self.store_task_in_racks()
        else:
            for key in task:
                if task[key] == 'activ' and self.get_interrupt_control() == 1:
                    if str(self.doc_add) == 'stop':
                        self.db_object.remove_db_plugin()
                        return False
                    else:
                        task[key] = str(self.doc_add)
                        self.update_db(self.creat_list_order(task))
                        return True
        return False

    def store_task_in_racks(self: object) -> bool:
        """Store order in racks.

        Returns:
            Return True after store.
        """
        ready_order = self.get_order_list()
        self.rack_object.creat_racks(ready_order[:3])
        self.set_interrupt_control(3)
        return True

    def check_collect_plugin(self: object, task: dict) -> bool:
        """Give the employees the orders that still need to be done.

        We use value from interrupt_controll in plug.db
        to determinate which state our plugin have.

        Args:
            task: Dictionary in plug.db.

        Returns:
            Return to trigger plugin True to stay active and false
            to check its similarity sentense.
        """
        if self.get_interrupt_control() == 5:
            if str(self.doc_add) == 'stop':
                self.db_object.remove_db_plugin()
                return False
            else:
                self.mark_corridor()
                self.set_interrupt_control(6)
                return True
        else:
            for key in task:
                if task[key] != 'collected' and self.get_interrupt_control(
                ) == 4 and key != 'order_id' and key != 'interrupt':
                    if str(self.doc_add) == 'stop':
                        self.db_object.remove_db_plugin()
                        return False
                    else:
                        return True
                elif self.get_interrupt_control() == 6:
                    bool_value = bool()
                    if self.collect_object.creat_collect_task() == -1:
                        bool_value = False
                    else:
                        bool_value = True
                    return bool_value
            self.interrupt_task()
            return True

    def mark_corridor(self: object) -> None:
        """Mark Order with collected if you finish collect."""
        corridor_info = self.finde_corridor()
        json_order = self.rack_object.read_jason_file(corridor_info[1])
        json_order[corridor_info[0]]['corridor_number'] = -1
        self.rack_object.open_file([json_order, corridor_info[1]])

    def finde_corridor(self: object) -> list:
        """Use this to finde order with id in plug.db.

        Returns:
            Return rack_number and corridor_number from order with
            order_id = id that we get from plug.db.
        """
        task = self.db_object.read_db_plugin()
        corridor_info = self.rack_object.find_order_place(task['order_id'])
        if corridor_info != 'not found':
            return corridor_info
        else:
            self.db_object.remove_db_plugin()
            return -1

    def creat_next_task(self: object) -> int:
        """Create next task for collecting.

        Returns:
            Return -1 if ther is no order more to collect.
        """
        collect_item = self.collect_object.creat_collect_task()
        if isinstance(collect_item, dict):
            collect_item = dict(collect_item, interrupt=4)
            self.update_db(self.creat_list_order(collect_item))
        else:
            return -1
        return 1

    def check_pick_plugin(self: object, task: dict) -> bool:
        """Take order in racks back to storeroom if client dont come and remove it.

        We use value from interrupt_controll in plug.db
        to determine which state our plugin have.

        Args:
            task: Speech text that we recieve from speech recognition.

        Returns:
            Return to trigger plugin True to stay active and false
            to check its similarity sentense.
        """
        if self.get_interrupt_control() == 8:
            if str(self.doc_add) == 'stop':
                self.db_object.remove_db_plugin()
                return False
            else:
                self.mark_pick_corridor()
                self.set_interrupt_control(9)
                return True
        else:
            for key in task:
                if task[key] != 'collected' and self.get_interrupt_control(
                ) == 7 and key != 'order_id' and key != 'interrupt':
                    if str(self.doc_add) == 'stop':
                        self.db_object.remove_db_plugin()
                        return False
                    else:
                        return True
                elif self.get_interrupt_control() == 9:
                    return self.collect_object.creat_pick_task()
            self.interrupt_pick_task()
            return True

    def creat_pick_task(self: object) -> bool:
        """Get the Value from creat_pick_task in class PickAndCollect.

        Update plug.db with this value.

        Returns:
            Bool value to controll the conversation.
        """
        collect_item = self.collect_object.creat_pick_task()
        if collect_item != -1:
            collect_item = dict(collect_item, interrupt=7)
            self.update_db(self.creat_list_order(collect_item))
            return True
        else:
            return False

    def mark_pick_corridor(self: object) -> None:
        """Mark rack if client becomes his order or if order is removed."""
        corridor_info = self.finde_corridor()
        if corridor_info != -1:
            json_order = self.rack_object.read_jason_file(corridor_info[1])
            json_order[corridor_info[0]]['corridor_number'] = corridor_info[1]
            json_order[corridor_info[0]]['rack_number'] = -1
            self.rack_object.open_file([json_order, corridor_info[1]])

    def check_client_triger(self: object, task: dict) -> bool:
        """Take from Client id and Give him his order.

        We use Value from interrupt_controll in plug.db
        to determinate which state our plugin have.

        Args:
            task: Dictionary in plug.db.

        Returns:
            Return to trigger plugin True to stay active and false
            to check its similarity sentense.
        """
        interrupt_control = self.get_interrupt_control()
        if interrupt_control == 13 or interrupt_control == 16:
            if str(self.doc_add) == 'stop':
                self.db_object.remove_db_plugin()
                return False
            else:
                self.update_db(['0', '0', '0', -1, 10])
                return True
        elif self.get_interrupt_control() == 10:
            return self.check_id_in_conversation(task)
        elif interrupt_control == 11 or interrupt_control == 14:
            return self.check_pick_collect(task)
        return False

    def check_id_in_conversation(self: object, task: dict) -> bool:
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
                    else:
                        task[key] = str(self.doc_add)
                        test_value = w2n.word_to_num(task[key])
                        test_value = test_value + 1
                        self.update_db(self.creat_list_order(task))
                        return True
        except ValueError:
            self.db_object.remove_db_plugin()
            return False

    def check_pick_collect(self: object, task: dict) -> bool:
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
            ignore_value = key != 'order_id' and key != 'interrupt'
            if task[key] != 'collected' and ignore_value:
                if str(self.doc_add) == 'stop':
                    self.db_object.remove_db_plugin()
                    return False
                else:
                    return True
        return True

    def creat_sentence(self: object, key: str) -> str:
        """Create sentence to say in some conversations.

        Args:
            key: Key from dictionary in plug.db.

        Returns:
            Return sentence that we can use in conversations.
        """
        if key == 'object' or key == 'amount':
            return 'take the ' + key
        elif key == 'corridor_number' or key == 'rack_number':
            return 'got to ' + key
        elif key == 'name':
            return 'client ' + key
        return 'None'

    def next_object(self: object) -> str:
        """Specify what collect order should say in conversation.

        Returns:
            Return sentence that speech recognition must say.
        """
        task = self.db_object.read_db_plugin()
        if self.get_interrupt_control() == 6:
            self.mark_corridor()
            if self.collect_object.creat_collect_task() == -1:
                self.db_object.remove_db_plugin()
                return 'no order more'
            else:
                self.creat_next_task()
                return 'save completed. next order'
        else:
            for key in task:
                ignore_value = key != 'order_id' and key != 'interrupt'
                state_value = task['interrupt'] == 4
                key_value = str(task[key]) != 'collected'
                if state_value and key_value and ignore_value:
                    order = str(task[key])
                    task[key] = 'collected'
                    self.update_db(self.creat_list_order(task))
                    return self.creat_sentence(key) + order
            self.interrupt_task()
            return 'stop for dont save'

    def next_element(self: object) -> str:
        """Specify what collect order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say.
        """
        task = self.db_object.read_db_plugin()
        for key in task:
            ignore_value = key != 'order_id' and key != 'interrupt'
            state_value = task['interrupt'] == 4
            key_value = str(task[key]) != 'collected'
            if state_value and key_value and ignore_value:
                return 'next'
        return 'stop for dont save'

    def interrupt_task(self: object) -> None:
        """Set interrupt in dictionary from plug.db when collect is done."""
        self.set_interrupt_control(5)

    def next_pick_object(self: object) -> str:
        """Specify what pick order should say in conversation.

        Returns:
            Return sentence that speech recognition must say.
        """
        task = self.db_object.read_db_plugin()
        if self.get_interrupt_control() == 9:
            if self.collect_object.creat_pick_task() == -1:
                self.db_object.remove_db_plugin()
                return 'no order more'
            elif self.creat_pick_task() != -1:
                self.mark_pick_corridor()
                self.creat_pick_task()
                return 'save completed. next order'
        else:
            for key in task:
                ignore_value = key != 'order_id' and key != 'interrupt'
                state_value = task['interrupt'] == 7
                key_value = str(task[key]) != 'collected'
                if state_value and key_value and ignore_value:
                    order = str(task[key])
                    task[key] = 'collected'
                    self.update_db(self.creat_list_order(task))
                    return self.creat_sentence(key) + order
            return 'stop for dont save'
        return 'None'

    def next_pick_element(self: object) -> str:
        """Specify what pick order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say.
        """
        task = self.db_object.read_db_plugin()
        for key in task:
            ignore_value = key != 'order_id' and key != 'interrupt'
            state_value = task['interrupt'] == 7
            key_value = str(task[key]) != 'collected'
            if state_value and key_value and ignore_value:
                return 'next'
        return 'stop for dont save'

    def interrupt_pick_task(self: object) -> None:
        """Set interrupt in dictionary from plug.db when pick is done."""
        self.set_interrupt_control(8)

    def next_client_object(self: object) -> str:
        """Specify what client order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say
            in case of collecting order.
        """
        task = self.db_object.read_db_plugin()
        if self.get_interrupt_control() == 13:
            if str(self.client_spit) == 'stop':
                self.db_object.remove_db_plugin()
                return 'stop'
            else:
                self.mark_pick_corridor()
                return 'save completed. next order'

        elif self.get_interrupt_control() == 11:
            for key in task:
                ignore_value = key != 'order_id' and key != 'interrupt'
                key_value = str(task[key]) != 'collected'
                if key_value and ignore_value:
                    order = str(task[key])
                    task[key] = 'collected'
                    self.update_db(self.creat_list_order(task))
                    return self.creat_sentence(key) + order
            return 'stop for dont save'
        return 'None'

    def next_client_element(self: object) -> str:
        """Specify what client order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say
            in case of pick order.
        """
        task = self.db_object.read_db_plugin()
        for key in task:
            ignore_value = key != 'order_id' and key != 'interrupt'
            state_value = task['interrupt'] == 11
            key_value = str(task[key]) != 'collected'
            if state_value and key_value and ignore_value:
                return 'next'
        return 'stop for dont save'

    def interrupt_client_task(self: object) -> None:
        """Set interrupt in dictionary from plug.db when pick is done."""
        self.set_interrupt_control(12)

    def next_client_collect(self: object) -> str:
        """Specify what client order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say
            in case of Taking id order.
        """
        task = self.db_object.read_db_plugin()
        if self.get_interrupt_control() == 16:
            if str(self.client_spit) == 'stop':
                self.db_object.remove_db_plugin()
                return 'stop'
            else:
                self.mark_corridor()
                return 'save completed. next order'

        elif self.get_interrupt_control() == 14:
            for key in task:
                ignore_value = key != 'order_id' and key != 'interrupt'
                key_value = str(task[key]) != 'collected'
                if key_value and ignore_value:
                    order = str(task[key])
                    task[key] = 'collected'
                    self.update_db(self.creat_list_order(task))
                    return self.creat_sentence(key) + order
            return 'stop for dont save'
        return 'None'

    def next_collect_client(self: object) -> str:
        """Specify what collect order should say in conversation as trigger.

        Returns:
            Return sentence that speech recognition must say
            in case of collecting.
        """
        task = self.db_object.read_db_plugin()
        for key in task:
            ignore_value = key != 'order_id' and key != 'interrupt'
            state_value = task['interrupt'] == 14
            key_value = str(task[key]) != 'collected'
            if state_value and key_value and ignore_value:
                return 'next'
        return 'stop for dont save'

    def interrupt_client_collect(self: object) -> None:
        """Set interrupt in dictionary from plug.db when collecting is done."""
        self.set_interrupt_control(15)

    def get_spit_response_triger(self: object) -> bool:
        """Take Results from other functions and give it to trigger spit.

        Returns:
            Return what trigger should say in all conversations.
        """
        if self.get_interrupt_control() in (1, 3):
            if self.get_interrupt_control() == 1:
                self.order_spit = 'you gave me' + str(self.doc_add)
                return True
            elif self.get_interrupt_control() == 3:
                self.order_spit = 'new order'
                return True
        elif self.get_interrupt_control() in (4, 5, 6):
            if self.next_element() == 'stop for dont save':
                self.order_spit = 'stop for dont save'
                return True
            else:
                self.order_spit = 'next'
                return True
        elif self.get_interrupt_control() in (7, 8, 9):
            if self.next_pick_element() == 'stop for dont save':
                self.order_spit = 'stop for dont save'
                self.interrupt_pick_task()
                return True
            else:
                self.order_spit = 'next'
                return True
        elif self.get_interrupt_control() == 10:
            self.order_spit = 'you gave me' + str(self.doc_add)
            return True
        elif self.get_interrupt_control() in (11, 12, 13):
            if self.next_client_element() == 'stop for dont save':
                self.order_spit = 'stop for dont save'
                self.interrupt_client_task()
                return True
            else:
                self.order_spit = 'next'
                return True
        elif self.get_interrupt_control() in (14, 15, 16):
            if self.next_collect_client() == 'stop for dont save':
                self.order_spit = 'stop for dont save'
                self.interrupt_client_collect()
                return True
            else:
                self.order_spit = 'next'
                return True
        return False
