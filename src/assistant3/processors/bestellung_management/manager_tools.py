"""Give tools for order plugins manager."""

from assistant3.processors.bestellung_management.collect_pick import PickAndCollect
from assistant3.processors.bestellung_management.make_db import MakeDB
from assistant3.processors.bestellung_management.make_racks import MakeRacks


class ManagerTools:
    """Define tools for plugins order manager."""

    def __init__(self) -> None:
        """Init."""
        self.db_object = MakeDB()
        self.rack_object = MakeRacks()
        self.collect_object = PickAndCollect()

    def get_order_list(self) -> list[str | int]:
        """Unpack the contents of the dictionary in plug.db.

        Returns:
            List of values from the dictionary in plug.db.

        """
        task = self.db_object.read_db_plugin()
        plug_order = []
        if isinstance(task, dict):
            for key in task:
                plug_order.append(task[key])
        return plug_order

    def creat_list_order(self, _m: dict[str, str | int]) -> list[str | int]:
        """Unpack the contents of the dictionary get_task.

        Dictionary get_task comes from plug.db.

        Args:
            _m: A dictionary will be in plug.db inserted.

        Returns:
            List of Values from the dictionary in plug.db.

        """
        get_task = _m
        plug_order = []
        for key in get_task:
            plug_order.append(get_task[key])
        return plug_order

    def update_db(self, plug_order: list[str | int]) -> None:
        """Remove the older dictionary in plug.db and Input a new update.

        List plug_order comes from plug.db.

        Args:
            plug_order: A list will be in plug.db inserted.

        """
        self.db_object.remove_db_plugin()
        self.db_object.insert_db_plugin(plug_order)

    def get_interrupt_control(self) -> int:
        """Get the Value of interrupt in the dictionary in plug.db.

        Returns:
            Value from interrupt.

        """
        task = self.db_object.read_db_plugin()
        if isinstance(task, int):
            return -1
        if isinstance(task['interrupt'], int):
            return task['interrupt']
        return 1

    def set_interrupt_control(self, interrupt_contorl: int) -> None:
        """Set the Value of interrupt in the dictionary in plug.db.

        This integer value comes from plug.db.
        With this value we can determine the states of the conversation.

        Args:
            interrupt_contorl: A integer Value.

        """
        task = self.db_object.read_db_plugin()
        if isinstance(task, dict) and isinstance(task['interrupt'], int):
            task['interrupt'] = interrupt_contorl
            self.update_db(self.creat_list_order(task))

    def store_task_in_racks(self) -> bool:
        """Store order in racks.

        Returns:
            Return True after store.

        """
        ready_order = self.get_order_list()
        self.rack_object.creat_racks(ready_order[:3])
        self.set_interrupt_control(3)
        return True

    def mark_corridor(self) -> None:
        """Mark Order with collected if you finish collect."""
        corridor_info = self.finde_corridor()
        if isinstance(corridor_info, list):
            _lit = iter(corridor_info)
            _m0 = next(_lit)
            _n1 = next(_lit)
            json_order = self.rack_object.read_jason_file(int(_n1))
            json_order[int(_m0)]['corridor_number'] = -1
            self.rack_object.open_file(_n1)
            self.rack_object.write_json_file(_n1, json_order)

    def finde_corridor(self) -> list[int] | int:
        """Use this to finde order with id in plug.db.

        Returns:
            Return rack_number and corridor_number from order with
            order_id = id that we get from plug.db.

        """
        task = self.db_object.read_db_plugin()
        if isinstance(task, dict):
            _n = task['order_id']
            if isinstance(_n, int):
                corridor_info = self.rack_object.find_order_place(_n)
                if isinstance(corridor_info, list):
                    return corridor_info
        self.db_object.remove_db_plugin()
        return -1

    def creat_next_task(self) -> int:
        """Create next task for collecting.

        Returns:
            Return -1 if ther is no order more to collect.

        """
        collect_info = self.collect_object.creat_collect_task()
        if isinstance(collect_info, list):
            collect_info.append(4)
            self.update_db(collect_info)
            return 1
        return -1

    def creat_pick_task(self) -> bool:
        """Get the Value from creat_pick_task in class PickAndCollect.

        Update plug.db with this value.

        Returns:
            Bool value to controll the conversation.

        """
        pick_info = self.collect_object.creat_pick_task()
        if isinstance(pick_info, list):
            self.update_db(pick_info)
            return True
        return False

    def mark_pick_corridor(self) -> None:
        """Mark rack if client becomes his order or if order is removed."""
        corridor_info = self.finde_corridor()
        if isinstance(corridor_info, list):
            _iter = iter(corridor_info)
            _m = next(_iter)
            _m = next(_iter)
            json_order = self.rack_object.read_jason_file(_m)
            json_order[corridor_info[0]]['corridor_number'] = _m
            json_order[corridor_info[0]]['rack_number'] = -1
            self.rack_object.open_file(_m)
            self.rack_object.write_json_file(_m, json_order)

    def creat_sentence(self, order_key: str) -> str:
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
