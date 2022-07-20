"""Give tools for order plugins manager."""

from assistant3.processors.collect_pick import PickAndCollect
from assistant3.processors.make_db import MakeDB
from assistant3.processors.make_racks import MakeRacks


class ManagerTools:
    """Define tools for plugins order manager."""

    def __init__(self: object) -> None:
        """Init."""
        self.db_object = MakeDB()
        self.rack_object = MakeRacks()
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

    def store_task_in_racks(self: object) -> bool:
        """Store order in racks.

        Returns:
            Return True after store.
        """
        ready_order = self.get_order_list()
        self.rack_object.creat_racks(ready_order[:3])
        self.set_interrupt_control(3)
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

    def creat_sentence(self: object, order_key: str) -> str:
        """Create sentence to say in some conversations.

        Args:
            order_key: Order_key from dictionary in plug.db.

        Returns:
            Return sentence that we can use in conversations.

        """
        if order_key in 'object' or order_key in 'amount':
            return 'take the ' + order_key
        if order_key in 'corridor_number' or order_key in 'rack_number':
            return 'got to ' + order_key
        if order_key in 'name':
            return 'client ' + order_key
        return 'None'
