import class_bestellung
import sqlite3
import nlp_key
import datetime
import os


class MakeDB:

    def __init__(self):
        pass

    def make_db(self):
        """Opens new database with name Bestellung"""
        con = sqlite3.connect("expl.db")
        cur = con.cursor()
        cur.execute(
            "create table if not exists Bestellung (name, object, amount, order_id, pick_time, place_number)"
        )
        con.close()

    def make_db_plugin(self):
        """Opens new database with name Plugin"""
        con = sqlite3.connect("plug.db")
        cur = con.cursor()
        cur.execute("create table if not exists Plugin (name, object, amount, interrupt)")
        con.close()

    def insert_db_plugin(self, l: list):
        con = sqlite3.connect("plug.db")
        cur = con.cursor()
        l = tuple(l)
        cur.execute("insert into Plugin values (?, ?, ?, ?)", l)
        con.commit()
        con.close()

    def remove_db_plugin(self):
        os.remove('plug.db')
        self.make_db_plugin()

    def read_db_plugin(self) -> list:
        con = sqlite3.connect("plug.db")
        cur = con.cursor()
        plugin_order = []
        for row in cur.execute("select * from Plugin"):
            plugin_order.append(row)

        con.close()
        if plugin_order != []:
            return dict(zip(['name', 'object', 'amount', 'interrupt'], list(plugin_order[0])))
        else:
            return plugin_order

    def creat_order(self, new_order: list) -> class_bestellung.Order:
        """Adds properties of class order to new_order object"""
        new_order.append(nlp_key.order_id_generate(datetime.datetime.now()))
        new_order.append(nlp_key.pick_time_generate(new_order[3]))
        new_order.append(0)
        return class_bestellung.Order(*new_order)

    def insert_db(self, new_order: list) -> None:
        """Inserts new order to database Bestellung"""
        con = sqlite3.connect("expl.db")
        cur = con.cursor()
        new_order_object = self.creat_order(new_order)
        if new_order_object.tuple_of_order not in self.read_db():
            cur.execute(
                "insert into Bestellung values (?, ?, ?, ?, ?, ?)", new_order_object.tuple_of_order
            )
        con.commit()
        con.close()

    def delete_order_db(self, order_id):
        """Determines which object in database has same order_id and delete it"""
        con = sqlite3.connect("expl.db")
        cur = con.cursor()
        cur.execute("delete from Bestellung where order_id=?", (order_id,))
        con.commit()
        con.close()

    def read_db(self) -> list:
        """Givs list of all order in database"""
        con = sqlite3.connect("expl.db")
        cur = con.cursor()
        list_of_order = []
        for row in cur.execute("select * from Bestellung"):
            list_of_order.append(row)
        con.close()
        return [
            class_bestellung.Order(*list_of_order[i]).tuple_of_order
            for i in range(len(list_of_order))
        ]

    def find_order_place(self, order_id):
        order_info = self.read_db()
        for i in len(order_info):
            if order_id in order_info[i]:
                return order_info[i]
        else:
            return 'not found'

    def dict_all_order(self) -> list:
        """Returns a list of dictionaries from database"""
        dict_order = []
        for order in self.read_db():
            dict_order.append({'name': order[0], 'order_id': order[3], 'rack_number': order[5]})

        return dict_order

    def order_collect(self):
        order_plugin = []
        for order in self.read_db():
            order_plugin.append(order[:3])
        return order_plugin

    def dict_order_plugin(self):
        order_plugin = self.order_collect()
        for order in order_plugin:
            if 0 in order:
                order_plugin = dict(zip(['name', 'amount', 'object'], order))
                return order_plugin
        else:
            return order


#db_object = MakeDB()
#db_object.make_db()

if __name__ == '__main__':
    db_object = MakeDB()
    db_object.make_db_plugin()
    #db_object.insert_db_plugin(['activ', '0', '0', 1])
    #db_object.insert_db_plugin(['hamza', '0', '0', 1])
    #print(db_object.read_db_plugin())
    #db_object.remove_db_plugin()
    print(db_object.read_db_plugin())
