"""if len(task) == 0:
            activated = self.is_activated(doc)
            if activated:
                self.order_manager.db_object.insert_db_plugin(['activ', '0', '0', 0])
        elif len(task) != 0:
            if self.order_manager.get_interrupt_control() == 2:
                if str(self.order_manager.doc_add) == 'stop':
                    self.order_manager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                else:
                    ready_order = self.order_manager.get_order_list()
                    self.order_manager.rack_object.creat_racks(ready_order[:3])
                    self.order_manager.set_interrupt_control(2)
                    activated = True
            else:
                for key in task:
                    if task[key] == 'activ' and self.order_manager.get_interrupt_control() == 1:
                        if str(self.order_manager.doc_add) == 'stop':
                            self.order_manager.db_object.remove_db_plugin()
                            activated = self.is_activated(doc)
                            break
                        else:
                            activated = True
                        task[key] = str(self.order_manager.doc_add)
                        self.order_manager.update_db(self.order_manager.creat_list_order(task))
                        break
                else:
                    #continue with the state, that we get with break ctrl+c during the introduction of elements in dictionary from plug
                    self.order_manager.db_object.remove_db_plugin()
                    activated = self.is_activated(doc)
                    if activated:
                        self.order_manager.db_object.insert_db_plugin(['activ', '0', '0', 0])"""
"""if self.order_manager.get_interrupt_control() == 2:
            activated = True
            self.order_manager.update_db(['activ', '0', '0', 1])
        elif self.order_manager.get_interrupt_control() == 0:
            activated = self.is_activated(doc)
            if activated:
                self.order_manager.update_db(['activ', '0', '0', 1])
        elif self.order_manager.get_interrupt_control() == 1:
            for key in task:
                if task[key] == '0':
                    task[key] = 'activ'
                    break
            self.order_manager.update_db(self.order_manager.creat_list_order(task))
            activated = True"""