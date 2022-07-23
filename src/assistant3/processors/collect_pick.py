"""define all actions during collect or pick the order."""
import datetime

from assistant3.processors.make_db import MakeDB
from assistant3.processors.make_racks import MakeRacks
from assistant3.processors.nlp_keys import order_id_generate


class PickAndCollect:
    """Define structure of pick and collet the order."""

    db_object = MakeDB()
    rack_object = MakeRacks()

    def __init__(self) -> None:
        """Init."""

    def pick_order_ability(self, order_id: int) -> str:
        """Give all information about order.

        With this informations will be the system able to determine
        what it should do in any situation.

        Args:
            order_id: Take id from Order.

        Returns:
            Return state about order that has this id_number.

        """
        order_place = self.rack_object.find_order_place(order_id)
        if isinstance(order_place, list):
            pl_iter = iter(order_place)
            rack_number = next(pl_iter)
            corridor_number = next(pl_iter)
            status = self.order_status(rack_number, corridor_number)
            if status[0] == 'not picked' and status[1] == 'collected':
                return 'ready to pick'
            if status[1] == 'not collected':
                return 'not collected'
        return 'not found'

    def pick_order_info(self, _kl: int) -> list[str | int] | str:
        """Give information by picking order with order_id.

        That means when client comes to pick his order
        he will give the worker _kl = id from order.
        than the system must be able to determine if the
        order able to pick or not. all state of order you can
        finde in function pick order ability.

        Args:
            _kl: Take id from Order.

        Returns:
            Return informations about order to pick.

        """
        order_id = _kl
        if self.pick_order_ability(order_id) == 'ready to pick':
            order_place = self.rack_object.find_order_place(order_id)
            if isinstance(order_place, list):
                iter_lk = iter(order_place)
                rack_number = next(iter_lk)
                corridor_number = next(iter_lk)
                json_order = self.rack_object.read_jason_file(corridor_number)
                _m = rack_number
                _n = corridor_number
                if isinstance(json_order[rack_number]['name'], str):
                    return [json_order[rack_number]['name'], _n, _m + 1]
        return self.pick_order_ability(order_id)

    def order_status(self, _m: int, _n: int) -> list[str]:
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

    def check_picked(self, _m: int, _n: int) -> bool:
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

    def check_collected(self, _m: int, _n: int) -> bool:
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

    def collect_order_with_id(self, _n: int) -> list[int | str] | str:
        """Give information about order to collect it.

        Args:
            _n: Take id from Order.

        Returns:
            Return informations about order to collect.

        """
        order_id = _n
        if self.pick_order_ability(order_id) == 'not collected':
            order_place = self.rack_object.find_order_place(order_id)
            order_info = self.db_object.find_order_place(order_id)
            if isinstance(order_place, list) and isinstance(order_info, tuple):
                pl_iter = iter(order_place)
                rack_number = next(pl_iter)
                corridor_number = next(pl_iter)
                kl_iter = iter(order_info)
                object_name = next(kl_iter)
                object_name = next(kl_iter)
                object_amount = next(kl_iter)
                _m = rack_number
                _kl = corridor_number
                return [object_name, object_amount, _kl, _m + 1, _n]
        return self.pick_order_ability(order_id)

    def creat_collect_task(self) -> list[int | str] | int:
        """Give order to collect.

        When order not collected, that system will giv it to Workers
        to collect it.

        Returns:
            Return informations about order to collect.

        """
        try:
            corridor_number = 1
            json_order = self.rack_object.read_jason_file(corridor_number)
            while True:
                for to_pick_order in json_order:
                    _m = to_pick_order['rack_number']
                    _l = to_pick_order['order_id']
                    _n = corridor_number
                    collect_info = self.collect_order_with_id(int(_l))
                    status = self.order_status(int(_m) - 1, _n)
                    l_isinst = isinstance(_l, int)
                    state = status == ['not picked', 'not collected']
                    if state and isinstance(collect_info, list) and l_isinst:
                        return collect_info
                corridor_number = corridor_number + 1
                json_order = self.rack_object.read_jason_file(corridor_number)
        except FileNotFoundError:
            return -1

    def creat_pick_task(self) -> list[int | str] | int:
        """Give all order to remove from racks.

        When client dont come to pick his order after one day.
        And when his order is from workers already pushed in racks.
        than must the worker remove from racks all this order
        with plugin bigin pick up and take it back to wearhous.

        Returns:
            Return informations about order to remove.

        """
        try:
            corridor_number = 1
            json_order = self.rack_object.read_jason_file(corridor_number)
            _t = order_id_generate(datetime.datetime.now())
            while True:
                for to_pick_order in json_order:
                    _l = to_pick_order['order_id']
                    _m = to_pick_order['rack_number']
                    status = self.order_status(int(_m) - 1, corridor_number)
                    pick_time = self.db_object.find_order_place(int(_l))
                    if isinstance(pick_time, tuple):
                        iter_lk = iter(pick_time)
                        _f = 0
                        for _f in range(3):
                            _lkl = next(iter_lk)
                            _f = _f + 0
                        _lkl = next(iter_lk)
                        pick_info = self.pick_order_info(int(_l))
                        _fy = status[1] in 'collected'
                        _lkl = int(_lkl) < _t
                        if int(_lkl) < _t and status[1] in 'not collected':
                            self.rack_object.delete_order_racks(int(_l))
                        elif isinstance(pick_info, list) and _lkl and _fy:
                            pick_info.append(int(_l))
                            return pick_info
                corridor_number = corridor_number + 1
                json_order = self.rack_object.read_jason_file(corridor_number)
        except FileNotFoundError:
            return -1
