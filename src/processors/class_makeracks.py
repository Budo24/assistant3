from processors.class_makedb import MakeDB
import json
import os


class MakeRacks:
    db_object = MakeDB()

    def __init__(self):
        pass

    def creat_racks(self, new_order: list) -> None:
        """Creats a racks for the order in database"""
        self.db_object.insert_db(new_order)
        self.add_json_order()

    def add_json_order(self):
        """Determines how racks are created"""
        try:
            self.generate_json_order()
        except FileNotFoundError:
            self.open_new_file()

    def open_new_file(self) -> None:
        """Initializes racks with order from database"""
        try:
            i = 1
            while True:
                open(self.generate_file_name(i), 'r+', encoding="utf-8")
                i = i + 1
        except FileNotFoundError:
            m = self.db_object.dict_all_order()
            open(self.generate_file_name(i), 'w')
            m[len(m) - 1]['rack_number'] = 1
            m[len(m) - 1] = dict(m[len(m) - 1], corridor_number=i)
            self.write_json_file([[m[len(m) - 1]], i])

    def generate_json_order(self) -> None:
        """Gets order from function dict_all_order and adds it 
        in the coresponding rack"""
        i = 1
        json_order = self.read_jason_file(i)
        m = self.db_object.dict_all_order()
        a = 0
        while a != 7:
            i = i + 1
            for j in range(len(json_order)):
                if json_order[j]['rack_number'] == -1:
                    m[len(m) - 1] = dict(m[len(m) - 1], corridor_number=i - 1)
                    json_order[j] = m[len(m) - 1]
                    json_order[j]['rack_number'] = j + 1
                    self.open_file([json_order, i - 1])
                    a = 7
                    break
            if len(json_order) < 20 and a != 7:
                m[len(m) - 1] = dict(m[len(m) - 1], corridor_number=i - 1)
                json_order.append(m[len(m) - 1])
                json_order[len(json_order) - 1]['rack_number'] = len(json_order)
                self.open_file([json_order, i - 1])
                a = 7
            elif a != 7:
                json_order = self.read_jason_file(i)

    def delete_order_racks(self, order_id):
        """Removes from racks object with the same order_id"""
        order_place = self.find_order_place(order_id)
        if order_place != 'not found':
            rack_number = order_place[0]
            corridor_number = order_place[1]
            json_order = self.read_jason_file(corridor_number)
            json_order[rack_number]['rack_number'] = -1
            self.open_file([json_order, corridor_number])
        elif order_place == 'not found':
            return 'not found'

    def find_order_place(self, order_id):
        try:
            corridor_number = 1
            json_order = self.read_jason_file(corridor_number)
            while True:
                for rack_number in range(len(json_order)):
                    if json_order[rack_number]['order_id'] == order_id:
                        if json_order[rack_number]['rack_number'] != -1:
                            return [rack_number, corridor_number]
                corridor_number = corridor_number + 1
                json_order = self.read_jason_file(corridor_number)

        except FileNotFoundError:
            return 'not found'

    def generate_file_name(self, i: int) -> str:
        """Generate file_name for racks"""
        return 'racks' + str(i)

    def read_jason_file(self, i):
        """Return  all orders in a coreponding corridor"""
        file_order = open(self.generate_file_name(i), 'r+', encoding="utf-8")
        json_order = json.load(file_order)
        return json_order

    def open_file(self, order_file: list[dict, int]) -> None:
        """Updates a racks"""
        os.remove(self.generate_file_name(order_file[1]))
        open(self.generate_file_name(order_file[1]), 'w')
        self.write_json_file(order_file)

    def write_json_file(self, order_file: list[dict, int]) -> None:
        """Adss order to the coresponding rack"""
        file_order = open(self.generate_file_name(order_file[1]), 'r+', encoding="utf-8")

        json.dump(order_file[0], file_order, indent=2)


if __name__ == '__main__':
    db = MakeDB()
    rack = MakeRacks()
    db.make_db()
    """for i in range(5):
        new_order = ['mariam' + str(i), 'matraze', i]
        rack.creat_racks(new_order)
    db.make_db()"""
    #print(rack.find_order_id(97232922))
    """new_order = ['3_10', 'bike', 1]
    rack.delete_order_racks(97232922)
    rack.creat_racks(new_order)"""
    print(db.read_db())
