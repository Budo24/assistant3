"""Give all orders in expl.db rack_number and corridor_number."""
import json
import os

from assistant3.processors.make_db import MakeDB


class MakeRacks:
    """Give structure of racks."""

    def __init__(self) -> None:
        """Init."""
        self.db_object = MakeDB()

    def creat_racks(self, new_order: list[str | int]) -> None:
        """Create a racks for the order in database.

        Args:
            new_order: contain name of client, object and amount.

        """
        self.db_object.insert_db(new_order)
        self.add_json_order()

    def add_json_order(self) -> None:
        """Determine how racks are created."""
        try:
            self.generate_json_order()
        except FileNotFoundError:
            self.open_new_file()

    def open_new_file(self) -> None:
        """Initialize racks with order from database."""
        try:
            i = 1
            while True:
                print(self.read_jason_file(i))
                i = i + 1
        except FileNotFoundError:
            _m = self.db_object.dict_all_order()
            _m[len(_m) - 1]['rack_number'] = 1
            _m[len(_m) - 1] = dict(_m[len(_m) - 1], corridor_number=i)
            self.write_json_file(i, [_m[len(_m) - 1]])

    def generate_json_order(self) -> None:
        """Get order from function dict_all_order and add it to racks."""
        i = 1
        json_order = self.read_jason_file(i)
        _m = self.db_object.dict_all_order()
        _a = 0
        while _a != 7:
            i = i + 1
            _s = len(json_order)
            for j in range(_s):
                if json_order[j]['rack_number'] == -1:
                    _k = _m[len(_m) - 1]
                    _m[len(_m) - 1] = dict(_k, corridor_number=f'{i - 1}')
                    json_order[j] = _m[len(_m) - 1]
                    json_order[j]['rack_number'] = j + 1
                    self.open_file(i - 1)
                    self.write_json_file(i - 1, json_order)
                    _a = 7
                    break
            if len(json_order) < 20 and _a != 7:
                _n = i - 1
                _m[len(_m) - 1] = dict(_m[len(_m) - 1], corridor_number=_n)
                json_order.append(_m[len(_m) - 1])
                _f = len(json_order)
                json_order[len(json_order) - 1]['rack_number'] = _f
                self.open_file(i - 1)
                self.write_json_file(i - 1, json_order)
                _a = 7
            elif _a != 7:
                json_order = self.read_jason_file(i)

    def delete_order_racks(self, order_id: int) -> str:
        """Remove from racks object with the same order_id.

        Args:
            order_id: Id from order.

        Returns:
            Return if order id exists and deleted.

        """
        order_place = self.find_order_place(order_id)
        if order_place:
            rack_number = int(order_place[0])
            corridor_number = int(order_place[1])
            json_order = self.read_jason_file(int(corridor_number))
            json_order[rack_number]['rack_number'] = -1
            self.open_file(corridor_number)
            self.write_json_file(corridor_number, json_order)
        elif not order_place:
            return 'not found'
        return 'deleted'

    def find_order_place(self, _l: int) -> list[str | int]:
        """Find order with order_id.

        Args:
            _l: Id from order.

        Returns:
            Return informations about place of order.

        """
        order_id = _l
        try:
            corridor_number = 1
            json_order = self.read_jason_file(corridor_number)
            while True:
                _k = len(json_order)
                for rack_number in range(_k):
                    _z = json_order[rack_number]['order_id'] == order_id
                    _y = json_order[rack_number]['rack_number'] != -1
                    if _z and _y:
                        return [rack_number, corridor_number]
                corridor_number = corridor_number + 1
                json_order = self.read_jason_file(corridor_number)

        except FileNotFoundError:
            return []

    def generate_file_name(self, i: int) -> str:
        """Generate file_name for racks.

        Args:
            i: Corridor_number.

        Returns:
            Return the name of corridor.

        """
        return 'racks' + str(i)

    def read_jason_file(self, i: int) -> list[dict[str, str | int]]:
        """Return  all orders in a coreponding corridor.

        Args:
            i: corridor_number.

        Returns:
            Return all orders in racksi.

        """
        _k = self.generate_file_name(i)
        with open(_k, 'r+', encoding='utf-8') as file_order:
            return list(json.load(file_order))

    def open_file(self, corridor_number: int) -> None:
        """Update a racks.

        Args:
            corridor_number: all orders in corridor number order_file[0].

        """
        os.remove(self.generate_file_name(corridor_number))

    def write_json_file(self, _k: int, _n: list[dict[str, str | int]]) -> None:
        """Add order to the coresponding rack.

        Args:
            _k: corridor_number
            _n: Content of all racks in _k

        """
        corridor_number = _k
        all_racks = _n
        _g = self.generate_file_name(corridor_number)
        with open(_g, 'w', encoding='utf-8'),\
                open(_g, 'r+', encoding='utf-8') as _l:
            json.dump(all_racks, _l, indent=2)
