"""define all actions during collect or pick the order."""
import datetime

from processors import nlp_keys
from processors.make_db import MakeDB
from processors.make_racks import MakeRacks


class PickAndCollect:
    """Define structure of pick and collet the order."""

    db_object = MakeDB()
    rack_object = MakeRacks()

    def __init__(self: object) -> None:
        """Init."""

    def pick_order_ability(self: object, order_id: int) -> str:
        """Give information if client can pick his order.

        Args:
            order_id: Take id from Order.

        Returns:
            Return state about order that has this id_number.
        """
        order_place = self.rack_object.find_order_place(order_id)
        if order_place != 'not found':
            rack_number = order_place[0]
            corridor_number = order_place[1]
            status = self.order_status(rack_number, corridor_number)
            if status[0] == 'not picked' and status[1] == 'collected':
                return 'ready to pick'
            elif status[1] == 'not collected':
                return status[1]
        return 'not found'

    def pick_order_info(self: object, order_id: int) -> dict:
        """Give information by picking order with order_id.

        Args:
            order_id: Take id from Order.

        Returns:
            Return informations about order to pick.
        """
        if self.pick_order_ability(order_id) == 'ready to pick':
            order_place = self.rack_object.find_order_place(order_id)
            rack_number = order_place[0]
            corridor_number = order_place[1]
            json_order = self.rack_object.read_jason_file(corridor_number)
            _m = rack_number
            _n = corridor_number
            pick_info = [json_order[rack_number]['name'], _n, _m + 1]
            _l = ['name', 'corridor_number', 'rack_number']
            return dict(zip(_l, pick_info))
        return self.pick_order_ability(order_id)

    def order_status(self: object, _m: int, _n: int) -> list:
        """Give general state of order.

        Args:
            _m: Rack_number.
            _n: Corridor_number.

        Returns:
            Return informations about order to pick.
        """
        rack_number = _m
        corridor_number = _n
        order_picked = 'not picked'
        order_collected = 'not collected'
        if self.check_collected(rack_number, corridor_number):
            order_collected = 'collected'
        if self.check_picked(rack_number, corridor_number):
            order_picked = 'picked'
        return [order_picked, order_collected]

    def check_picked(self: object, _m: int, _n: int) -> bool:
        """Give information about picke state.

        Args:
            _m: Rack_number.
            _n: Corridor_number.

        Returns:
            Return state from order.
        """
        rack_number = _m
        corridor_number = _n
        json_order = self.rack_object.read_jason_file(corridor_number)
        if json_order[rack_number]['rack_number'] == -1:
            return True
        return False

    def check_collected(self: object, _m: int, _n: int) -> bool:
        """Give information about collect state.

        Args:
            _m: Rack_number.
            _n: Corridor_number.

        Returns:
            Return state from order.

        """
        rack_number = _m
        corridor_number = _n
        if _m >= 0:
            json_order = self.rack_object.read_jason_file(corridor_number)
            if json_order[rack_number]['corridor_number'] == -1:
                return True
        return False

    def collect_order_with_id(self: object, order_id: int) -> dict:
        """Give information about order to collect it.

        Args:
            order_id: Take id from Order.

        Returns:
            Return informations about order to collect.
        """
        if self.pick_order_ability(order_id) == 'not collected':
            order_place = self.rack_object.find_order_place(order_id)
            rack_number = order_place[0]
            corridor_number = order_place[1]
            order_place = self.db_object.find_order_place(order_id)
            object_name = order_place[1]
            object_amount = order_place[2]
            _m = rack_number
            _n = corridor_number
            _l = ['object', 'amount', 'corridor_number', 'rack_number']
            collect_info = [object_name, object_amount, _n, _m + 1]
            return dict(zip(_l, collect_info))
        return self.pick_order_ability(order_id)

    def creat_collect_task(self: object) -> dict:
        """Give order to collect.

        Returns:
            Return informations about order to collect.
        """
        try:
            corridor_number = 1
            json_order = self.rack_object.read_jason_file(corridor_number)
            _a = 0
            while _a != 7:
                for to_pick_order in json_order:
                    _m = to_pick_order['rack_number']
                    _n = corridor_number
                    status = self.order_status(_m - 1, _n)
                    if status == ['not picked', 'not collected']:
                        _l = to_pick_order['order_id']
                        collect_info = self.collect_order_with_id(_l)
                        if isinstance(collect_info, dict):
                            _a = 7
                            return dict(collect_info, order_id=_l)
                corridor_number = corridor_number + 1
                json_order = self.rack_object.read_jason_file(corridor_number)
        except FileNotFoundError:
            return -1

    def creat_pick_task(self: object) -> dict:
        """Give all order to remove from racks.

        Returns:
            Return informations about order to remove.
        """
        try:
            time_now = datetime.datetime.now()
            time_now = nlp_keys.order_id_generate(time_now)
            corridor_number = 1
            json_order = self.rack_object.read_jason_file(corridor_number)
            while True:
                for to_pick_order in json_order:
                    _l = to_pick_order['order_id']
                    _m = to_pick_order['rack_number']
                    _n = corridor_number
                    status = self.order_status(_m - 1, _n)
                    pick_time = self.db_object.find_order_place(_l)
                    if pick_time[4] < time_now:
                        if status[1] == 'not collected':
                            self.rack_object.delete_order_racks(_l)
                        elif status[1] == 'collected':
                            pick_info = self.pick_order_info(_l)
                            return dict(pick_info, order_id=_l)
                corridor_number = corridor_number + 1
                json_order = self.rack_object.read_jason_file(corridor_number)
        except FileNotFoundError:
            return -1
