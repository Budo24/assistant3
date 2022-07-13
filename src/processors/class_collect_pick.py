from processors.class_makeracks import MakeRacks
from processors.class_makedb import MakeDB
import queue


class PickAndCollect:
    db_object = MakeDB()
    rack_object = MakeRacks()

    def __init__(self):
        pass

    """nach picken rack auf '-1' und corridor wieder auf corridor_number setzen setzen und nach collect corridor auf -1 setzen"""

    def pick_order_ability(self, order_id):
        """Give info if client can pick his order"""
        order_place = self.rack_object.find_order_place(order_id)
        if order_place != 'not found':
            rack_number = order_place[0]
            corridor_number = order_place[1]
            status = self.order_status(rack_number, corridor_number)
            if status[0] == 'not picked' and status[1] == 'collected':
                return 'ready to pick'
            elif status[1] == 'not collected':
                return status[1]
        else:
            return 'not found'

    def pick_order_info(self, order_id):
        """Give information about order, when client want to pick his order"""
        if self.pick_order_ability(order_id) == 'ready to pick':
            order_place = self.rack_object.find_order_id(order_id)
            rack_number = order_place[0]
            corridor_number = order_place[1]
            json_order = self.rack_object.read_jason_file(corridor_number)
            pick_info = [json_order[rack_number]['name'], rack_number + 1, corridor_number]
            return pick_info
        else:
            self.pick_order_ability(order_id)

    def order_status(self, rack_number, corridor_number):
        order_picked = 'not picked'
        order_collected = 'not collected'
        if self.check_collected(rack_number, corridor_number):
            order_collected = 'collected'
        if self.check_picked(rack_number, corridor_number):
            order_picked = 'picked'
        return [order_picked, order_collected]

    def check_picked(self, rack_number, corridor_number):
        json_order = self.rack_object.read_jason_file(corridor_number)
        if json_order[rack_number]['rack_number'] == -1:
            return True
        else:
            return False

    def check_collected(self, rack_number, corridor_number):
        json_order = self.rack_object.read_jason_file(corridor_number)
        if json_order[rack_number]['corridor_number'] == -1:
            return True
        else:
            return False

    def collect_order_with_id(self, order_id):
        if self.pick_order_ability(order_id) == 'not collected':
            order_place = self.rack_object.find_order_place(order_id)
            rack_number = order_place[0]
            corridor_number = order_place[1]
            order_place = self.db_object.find_order_place(order_id)
            object_name = order_place[1]
            object_amount = order_place[2]
            collect_info = [object_name, object_amount, corridor_number, rack_number + 1]
            collect_info = dict(
                zip(['object', 'amount', 'corridor_number', 'rack_number'], collect_info)
            )
            return collect_info
        else:
            return self.pick_order_ability(order_id)

    def creat_collect_task(self) -> queue:
        corridor_number = 1
        json_order = self.rack_object.read_jason_file(corridor_number)
        collect_queue = queue.Queue(0)
        try:
            while True:
                for to_pick_order in json_order:
                    #print("HEEE", to_pick_order)
                    #print("ryokay", json_order)
                    print("what", json_order[0]['rack_number'])
                    status = self.order_status(to_pick_order['rack_number'] - 1, corridor_number)
                    if status == ['not picked', 'not collected']:
                        collect_info = self.collect_order_with_id(to_pick_order['order_id'])
                        collect_queue.put(collect_info)
                corridor_number = corridor_number + 1
                json_order = self.rack_object.read_jason_file(corridor_number)
        except FileNotFoundError:
            collect_queue.put(-1)
        return collect_queue


if __name__ == '__main__':
    collect_object = PickAndCollect()
    collect_task2 = collect_object.creat_collect_task()
    while True:
        m = collect_task2.get()
        if m == -1:
            break
        print(m)
