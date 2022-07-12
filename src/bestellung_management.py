from multiprocessing import Manager
from class_makedb import MakeDB
from class_makeracks import MakeRacks


class OrderManager:
    """Manage how the Values from dictionary in plug.db with assistent 3 be obtained"""

    def __init__(self):
        self.doc_add = '0'
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
        return task['interrupt']

    def set_interrupt_control(self, interrupt_contorl):
        """Set the Value of interrupt in the dictionary in plug.db"""
        task = self.db_object.read_db_plugin()
        task['interrupt'] = interrupt_contorl
        self.update_db(self.creat_list_order(task))

    def check_add_order_triger(self, task, doc):
        self.doc_add = doc
        if len(task) == 0:
            return 'task empty'
        elif len(task) != 0:
            if self.get_interrupt_control() == 2:
                if str(self.doc_add) == 'stop':
                    self.db_object.remove_db_plugin()
                    return 'stop is activated. remove the actually order'
                else:
                    return 'we will add new order'
            else:
                for key in task:
                    if task[key] == 'activ' and self.get_interrupt_control() == 1:
                        if str(self.doc_add) == 'stop':
                            self.db_object.remove_db_plugin()
                            return 'interrupt plugin AddOrder'
                        else:
                            task[key] = str(self.doc_add)
                            self.update_db(self.creat_list_order(task))
                            return 'we will continue with this order'
                else:
                    #continue with the state, that we get with break ctrl+c during the introduction of elements in dictionary from plug
                    self.db_object.remove_db_plugin()
                    return 'we had an order not continued with state not activ. remove it'

    def stor_task_in_racks(self):
        ready_order = self.get_order_list()
        self.rack_object.creat_racks(ready_order[:3])
        self.set_interrupt_control(2)
        return True


if __name__ == '__main__':
    manager_objectk = OrderManager()
    print(manager_objectk.get_interrupt_control())