"""Give all orders in expl.db rack_number and corridor_number."""
import json
import os

from processors.class_makedb import MakeDB


class MakeRacks:
    """Give structure of racks."""

    db_object = MakeDB()

    def __init__(self: object) -> None:
        """Init."""

    def creat_racks(self: object, new_order: list) -> None:
        """Create a racks for the order in database.

        Args:
            new_order: contain name of client, object and amount.
        """
        self.db_object.insert_db(new_order)
        self.add_json_order()

    def add_json_order(self: object) -> None:
        """Determine how racks are created."""
        try:
            self.generate_json_order()
        except FileNotFoundError:
            self.open_new_file()

    def open_new_file(self: object) -> None:
        """Initialize racks with order from database."""
        try:
            i = 1
            while True:
                _s = self.generate_file_name(i)
                with open('r+', encoding='utf-8') as _s:
                    json.load(_s)
                i = i + 1
        except FileNotFoundError:
            _m = self.db_object.dict_all_order()
            _j = self.generate_file_name(i)
            open(_j, 'w', encoding='utf-8')
            _m[len(_m) - 1]['rack_number'] = 1
            _m[len(_m) - 1] = dict(_m[len(_m) - 1], corridor_number=i)
            self.write_json_file([[_m[len(_m) - 1]], i])

    def generate_json_order(self: object) -> None:
        """Get order from function dict_all_order and add it to racks."""
        i = 1
        json_order = self.read_jason_file(i)
        _m = self.db_object.dict_all_order()
        _a = 0
        while _a != 7:
            i = i + 1
            _k = len(json_order)
            for j in range(_k):
                if json_order[j]['rack_number'] == -1:
                    _k = _m[len(_m) - 1]
                    _m[len(_m) - 1] = dict(_k, corridor_number=i - 1)
                    json_order[j] = _m[len(_m) - 1]
                    json_order[j]['rack_number'] = j + 1
                    self.open_file([json_order, i - 1])
                    _a = 7
                    break
            if len(json_order) < 20 and _a != 7:
                _m[len(_m) - 1] = dict(_m[len(_m) - 1], corridor_number=i - 1)
                json_order.append(_m[len(_m) - 1])
                _f = len(json_order)
                json_order[len(json_order) - 1]['rack_number'] = _f
                self.open_file([json_order, i - 1])
                _a = 7
            elif _a != 7:
                json_order = self.read_jason_file(i)

    def delete_order_racks(self: object, order_id: int) -> str:
        """Remove from racks object with the same order_id.

        Args:
            order_id: Id from order.

        Returns:
            Return if order id exists and deleted.
        """
        order_place = self.find_order_place(order_id)
        if order_place != 'not found':
            rack_number = order_place[0]
            corridor_number = order_place[1]
            json_order = self.read_jason_file(corridor_number)
            json_order[rack_number]['rack_number'] = -1
            self.open_file([json_order, corridor_number])
        elif order_place == 'not found':
            return 'not found'
        return 'deleted'

    def find_order_place(self: object, order_id: int) -> list:
        """Find order with order_id.

        Args:
            order_id: Id from order.

        Returns:
            Return informations about place of order.
        """
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
            return 'not found'

    def generate_file_name(self: object, i: int) -> str:
        """Generate file_name for racks.

        Args:
            i: Corridor_number.

        Returns:
            Return the name of corridor.
        """
        return 'racks' + str(i)

    def read_jason_file(self: object, i: int) -> list:
        """Return  all orders in a coreponding corridor.

        Args:
            i: corridor_number.

        Returns:
            Return all orders in racksi.
        """
        _k = self.generate_file_name(i)
        with open(_k, 'r+', encoding='utf-8') as file_order:
            return json.load(file_order)

    def open_file(self: object, order_file: list[dict, int]) -> None:
        """Update a racks.

        Args:
            order_file: all orders in corridor number order_file[0].
        """
        os.remove(self.generate_file_name(order_file[1]))
        _g = self.generate_file_name(order_file[1])
        open(_g, 'w', encoding='utf-8')
        self.write_json_file(order_file)

    def write_json_file(self: object, order_file: list[dict, int]) -> None:
        """Add order to the coresponding rack.

        Args:
            order_file: all orders in corridor number: order_file[0].
        """
        _x = self.generate_file_name(order_file[1])
        with open(_x, 'r+', encoding='utf-8') as file_order:
            json.dump(order_file[0], file_order, indent=2)


if __name__ == '__main__':
    db = MakeDB()
    rack = MakeRacks()
