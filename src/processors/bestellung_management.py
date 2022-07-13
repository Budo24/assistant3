from processors.class_makedb import MakeDB
from processors.class_makeracks import MakeRacks


class OrderManager:
    """Manage how the Values from dictionary in plug.db with assistent 3 be obtained"""

    def __init__(self):
        self.doc_add = '0'
        self.order_spit = 'nothing'
        self.db_object = MakeDB()
        self.rack_object = MakeRacks()
        self.db_object.make_db_plugin()
        self.db_object.make_db()
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
        task['interrupt'] = interrupt_contorl
        self.update_db(self.creat_list_order(task))

    def check_order_triger(self, doc):
        task = self.db_object.read_db_plugin()
        self.doc_add = doc
        if len(task) == 0:
            self.db_object.insert_db_plugin(['activ', '0', '0', '0', 0])
            return False
        elif len(task) != 0:
            #add new order
            if self.get_interrupt_control() in (1, 2):
                return self.check_add_order_triger(task)
            #creact task for collect
            elif self.get_interrupt_control() not in (4, 5):
                pass

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
                self.db_object.remove_db_plugin()
                return False

    def store_task_in_racks(self):
        ready_order = self.get_order_list()
        self.rack_object.creat_racks(ready_order[:3])
        self.set_interrupt_control(3)
        return True

    def get_spit_response_triger(self):
        if self.get_interrupt_control() in (1, 3):
            if self.get_interrupt_control() == 1:
                self.order_spit = 'you gave me' + str(self.doc_add)
                return True
            elif self.get_interrupt_control() == 3:
                self.order_spit = 'new order'
                return True
        elif self.get_interrupt_control() in (4, 6):
            pass
        else:
            return False


if __name__ == '__main__':
    manager_objectk = OrderManager()
    print(manager_objectk.get_interrupt_control())
