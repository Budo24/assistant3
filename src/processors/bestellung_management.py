from processors.class_makedb import MakeDB
from processors.class_makeracks import MakeRacks
from processors.class_collect_pick import PickAndCollect
#print w2n.word_to_num("two million three thousand nine hundred and eighty four")
from word2number import w2n


class OrderManager:
    """Manage how the Values from dictionary in plug.db with assistent 3 be obtained"""

    def __init__(self):
        self.doc_add = '0'
        self.order_spit = 'nothing'
        self.db_object = MakeDB()
        self.rack_object = MakeRacks()
        self.db_object.make_db_plugin()
        self.db_object.make_db()
        self.collect_object = PickAndCollect()
        #self.mark_collect = 0
        #get the dictionary in plug.db

    def get_order_list(self):
        """Unpack the contents of the dictionary in plug.db and paste them into list"""
        task = self.db_object.read_db_plugin()
        plug_order = []
        for key in task:
            plug_order.append(task[key])
        return plug_order

    def creat_list_order(self, get_task: dict):
        """get dictionary get_task and unpack its content in list"""
        plug_order = []
        for key in get_task:
            plug_order.append(get_task[key])
        return plug_order

    def update_db(self, plug_order: list):
        """Remove the older dictionary in plug.db and Input a new update"""
        self.db_object.remove_db_plugin()
        self.db_object.insert_db_plugin(plug_order)

    def get_interrupt_control(self):
        """Get the Value of interrupt in the dictionary in plug.db"""
        task = self.db_object.read_db_plugin()
        if len(task) == 0:
            return False
        else:
            return task['interrupt']

    def set_interrupt_control(self, interrupt_contorl):
        """Set the Value of interrupt in the dictionary in plug.db"""
        task = self.db_object.read_db_plugin()
        print("WEEEE", task)
        if len(task) != 0:
            task['interrupt'] = interrupt_contorl
            self.update_db(self.creat_list_order(task))

    def check_order_triger(self, doc):
        task = self.db_object.read_db_plugin()
        self.doc_add = doc
        if len(task) == 0:
            self.db_object.insert_db_plugin(['activ', '0', '0', '0', '0', 0])
            return False
        elif len(task) != 0:
            #plugin for add new order
            if self.get_interrupt_control() in (1, 2):
                return self.check_add_order_triger(task)
            #plugin for collect order
            elif self.get_interrupt_control() in (4, 6, 5):
                return self.check_collect_plugin(task)
            #plugin for pick order from racks
            elif self.get_interrupt_control() in (7, 8, 9, -2):
                return self.check_pick_plugin(task)

    def check_pick_plugin(self, task):
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
                    if self.collect_object.creat_pick_task() == -1:
                        return False
                    else:
                        return True
            else:
                #continue with the state, that we get with break ctrl+c during the introduction of elements in dictionary from plug
                self.interrupt_pick_task()
                return True

    def creat_pick_task(self):
        collect_item = self.collect_object.creat_pick_task()
        if collect_item != -1:
            collect_item = dict(collect_item, interrupt=7)
            self.update_db(self.creat_list_order(collect_item))
        else:
            return -1

    def check_add_order_triger(self, task):
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
            else:
                #continue with the state, that we get with break ctrl+c during the introduction of elements in dictionary from plug
                if len(task) == 4:
                    self.db_object.remove_db_plugin()
                return False

    def store_task_in_racks(self):
        ready_order = self.get_order_list()
        self.rack_object.creat_racks(ready_order[:3])
        self.set_interrupt_control(3)
        return True

    def check_collect_plugin(self, task):
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
                    if self.collect_object.creat_collect_task() == -1:
                        return False
                    else:
                        return True
            else:
                #continue with the state, that we get with break ctrl+c during the introduction of elements in dictionary from plug
                self.interrupt_task()
                return True

    def mark_corridor(self):
        """Mark Order with collected if you finish collect"""
        corridor_info = self.finde_corridor()
        json_order = self.rack_object.read_jason_file(corridor_info[1])
        json_order[corridor_info[0]]['corridor_number'] = -1
        self.rack_object.open_file([json_order, corridor_info[1]])

    def mark_pick_corridor(self):
        corridor_info = self.finde_corridor()
        if corridor_info != -1:
            json_order = self.rack_object.read_jason_file(corridor_info[1])
            json_order[corridor_info[0]]['corridor_number'] = corridor_info[1]
            json_order[corridor_info[0]]['rack_number'] = -1
            self.rack_object.open_file([json_order, corridor_info[1]])

    def finde_corridor(self):
        """Use this to finde order with id"""
        task = self.db_object.read_db_plugin()
        corridor_info = self.rack_object.find_order_place(task['order_id'])
        if corridor_info != 'not found':
            return corridor_info
        else:
            self.db_object.remove_db_plugin()
            return -1

    def creat_next_task(self):
        """Creat next task for collecting"""
        collect_item = self.collect_object.creat_collect_task()
        if type(collect_item) == dict:
            collect_item = dict(collect_item, interrupt=4)
            self.update_db(self.creat_list_order(collect_item))
        else:
            return -1

    def creat_sentence(self, key) -> str:
        """Creat sentence to say"""
        place_centence = 'got to ' + key
        object_centence = 'take the ' + key
        client_centence = 'client ' + key
        if key == 'object' or key == 'amount':
            return object_centence
        elif key == 'corridor_number' or key == 'rack_number':
            return place_centence
        elif key == 'name':
            return client_centence

    def next_object(self):
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
                if str(task[key]) != 'collected' and key != 'interrupt' and task[
                    'interrupt'] == 4 and key != 'order_id':
                    order = str(task[key])
                    task[key] = 'collected'
                    self.update_db(self.creat_list_order(task))
                    return self.creat_sentence(key) + order
            else:
                self.interrupt_task()
                return 'stop for dont save'

    def next_element(self):
        task = self.db_object.read_db_plugin()
        for key in task:
            if str(task[key]) != 'collected' and key != 'interrupt' and key != 'order_id' and task[
                'interrupt'] == 4:
                return 'next'
        else:
            return 'stop for dont save'

    def interrupt_task(self):
        self.set_interrupt_control(5)

    def next_pick_object(self):
        task = self.db_object.read_db_plugin()
        if self.get_interrupt_control() == 9:
            #here we should check if we have something else to do
            if self.collect_object.creat_pick_task() == -1:
                self.db_object.remove_db_plugin()
                return 'no order more'
            elif self.creat_pick_task() != -1:
                self.mark_pick_corridor()
                self.creat_pick_task()
                return 'save completed. next order'

        else:
            for key in task:
                if str(task[key]) != 'collected' and key != 'interrupt' and task[
                    'interrupt'] == 7 and key != 'order_id':
                    order = str(task[key])
                    task[key] = 'collected'
                    self.update_db(self.creat_list_order(task))
                    return self.creat_sentence(key) + order
            else:
                #self.interrupt_pick_task()
                return 'stop for dont save'

    def next_pick_element(self):
        task = self.db_object.read_db_plugin()
        for key in task:
            if str(task[key]) != 'collected' and key != 'interrupt' and key != 'order_id' and task[
                'interrupt'] == 7:
                return 'next'
        else:
            return 'stop for dont save'

    def interrupt_pick_task(self):
        self.set_interrupt_control(8)

    def get_spit_response_triger(self):
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
        else:
            return False


if __name__ == '__main__':
    #manager_objectk = OrderManager()
    #manager_objectk.mark_corridor()
    #print(manager_objectk.get_interrupt_control())
    """if self.get_interrupt_control() == 6:
                if self.collect_object.creat_collect_task() == -1:
                    self.order_spit = 'no order more'
                    self.update_db(['0', '0', '0', '0', '0', 0])
                    return True
                else:
                    self.order_spit = 'save completed. next order'
                    self.creat_next_task()
                    return True"""
