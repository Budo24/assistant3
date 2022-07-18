from processors.class_makeracks import MakeRacks
from processors.class_makedb import MakeDB
import nlp_key
import datetime


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
            order_place = self.rack_object.find_order_place(order_id)
            rack_number = order_place[0]
            corridor_number = order_place[1]
            json_order = self.rack_object.read_jason_file(corridor_number)
            pick_info = [json_order[rack_number]['name'], corridor_number, rack_number + 1]
            return dict(zip(['name', 'corridor_number', 'rack_number'], pick_info))
        else:
            return self.pick_order_ability(order_id)

    def order_status(self, rack_number, corridor_number):
        """Give general state of order"""
        order_picked = 'not picked'
        order_collected = 'not collected'
        if self.check_collected(rack_number, corridor_number):
            order_collected = 'collected'
        if self.check_picked(rack_number, corridor_number):
            order_picked = 'picked'
        return [order_picked, order_collected]

    def check_picked(self, rack_number, corridor_number):
        """Give information about picke state"""
        json_order = self.rack_object.read_jason_file(corridor_number)
        if json_order[rack_number]['rack_number'] == -1:
            return True
        else:
            return False

    def check_collected(self, rack_number, corridor_number):
        """Give information about collect state"""
        json_order = self.rack_object.read_jason_file(corridor_number)
        if json_order[rack_number]['corridor_number'] == -1:
            return True
        else:
            return False

    def collect_order_with_id(self, order_id):
        """Give information about order to collect it"""
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

    #first thing we check pick_time< > generate_id if collected go to pick
    #pick with ['name', 'corr', 'rack', 'id_', 10]
    #if someone come to pick his order he give me id
    #with this id we make in plug.db ['name', 'corr', 'rack', 'id_', 10]
    #plug for pick will find this in plug.db and will pick it

    def creat_collect_task(self):
        """Give order to collect"""
        try:
            corridor_number = 1
            json_order = self.rack_object.read_jason_file(corridor_number)
            a = 0
            while a != 7:
                for to_pick_order in json_order:
                    #print("HEEE", to_pick_order)
                    #print("ryokay", json_order)
                    print("what", json_order[0]['rack_number'])
                    status = self.order_status(to_pick_order['rack_number'] - 1, corridor_number)
                    print("creat_collect", status)
                    if status == ['not picked', 'not collected']:
                        collect_info = self.collect_order_with_id(to_pick_order['order_id'])
                        print("creat_collect_task", collect_info)
                        #collect_queue.put(collect_info)
                        if type(collect_info) == dict:
                            a = 7
                            print(a)
                            return dict(collect_info, order_id=to_pick_order['order_id'])
                        """elif collect_info == 'not found':
                            return -1"""
                corridor_number = corridor_number + 1
                json_order = self.rack_object.read_jason_file(corridor_number)
        except FileNotFoundError:
            #collect_queue.put(-1)
            collect_info = -1
        return collect_info

    def creat_pick_task(self):
        """Give order to collect. Emoe all oder that was stored for one day but not collected"""
        try:
            time_now = datetime.datetime.now()
            time_now = nlp_key.order_id_generate(time_now)
            corridor_number = 1
            json_order = self.rack_object.read_jason_file(corridor_number)
            while True:
                for to_pick_order in json_order:
                    status = self.order_status(to_pick_order['rack_number'] - 1, corridor_number)
                    pick_time = self.db_object.find_order_place(to_pick_order['order_id'])
                    if pick_time[4] < time_now:
                        if status[1] == 'not collected':
                            self.rack_object.delete_order_racks(to_pick_order['order_id'])
                        elif status[1] == 'collected':
                            pick_info = self.pick_order_info(to_pick_order['order_id'])
                            print("creat_pick_task", pick_info)
                            return dict(pick_info, order_id=to_pick_order['order_id'])
                            #[json_order[rack_number]['name'], corridor_number, rack_number + 1]
                corridor_number = corridor_number + 1
                json_order = self.rack_object.read_jason_file(corridor_number)
        except FileNotFoundError:
            #collect_queue.put(-1)
            collect_info = -1
        return collect_info

    #pick with id when we have id from id plugin we will ser creat_coollect_task in 'a' and the order with id in place from
    #a when we finish we will change it but if id from a != id


if __name__ == '__main__':
    collect_object = PickAndCollect()
    """collect_task2 = collect_object.creat_collect_task()
    print(collect_task2)"""
    #collect_object.collect_one_order(147221034)
    #print(collect_object.rack_object.read_jason_file(1))
    #print("ja", collect_object.creat_pick_task())
    #print("hier", collect_object.creat_collect_task())
    #print(collect_object.pick_order_info(187011935))
    print(collect_object.collect_order_with_id(187011935))
