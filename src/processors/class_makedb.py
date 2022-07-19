"""Create all databases and their structure."""
import datetime
import os
import sqlite3

import class_bestellung
import nlp_key


class MakeDB:
    """Create structure for all database."""

    def __init__(self: object) -> None:
        """Init."""

    def make_db(self: object) -> None:
        """Open new database with name Bestellung."""
        con = sqlite3.connect('expl.db')
        cur = con.cursor()
        _m = ('name', 'object', 'amount')
        _n = ('order_id', 'pick_time', 'place_number')
        _l = _m + _n
        cur.execute(f'create table if not exists Bestellung {_l}')
        con.close()

    def creat_order(self: object, new_order: list) -> class_bestellung.Order:
        """Create with new_order an order object.

        Args:
            new_order: Has all properties from class order.

        Returns:
            Return order object with infos in new_order.
        """
        new_order.append(nlp_key.order_id_generate(datetime.datetime.now()))
        new_order.append(nlp_key.pick_time_generate(new_order[3]))
        new_order.append(0)
        return class_bestellung.Order(*new_order)

    def insert_db(self: object, new_order: list) -> None:
        """Insert new order to database Bestellung.

        Args:
            new_order: Order.
        """
        con = sqlite3.connect('expl.db')
        cur = con.cursor()
        new_order_object = self.creat_order(new_order)
        _m = new_order_object.tuple_of_order
        if new_order_object.tuple_of_order not in self.read_db():
            cur.execute('insert into Bestellung values (?, ?, ?, ?, ?, ?)', _m)
        con.commit()
        con.close()

    def delete_order_db(self: object, order_id: int) -> None:
        """Determine which object in database has same order_id and delete it.

        Args:
            order_id: Id from order.
        """
        con = sqlite3.connect('expl.db')
        cur = con.cursor()
        cur.execute('delete from Bestellung where order_id=?', (order_id,))
        con.commit()
        con.close()

    def read_db(self: object) -> list:
        """Check all order that we have.

        Returns:
            Return list of all orders in our database expl.db.
        """
        con = sqlite3.connect('expl.db')
        cur = con.cursor()
        list_of_order = []
        for row in cur.execute('select * from Bestellung'):
            list_of_order.append(row)
        con.close()
        return [
            class_bestellung.Order(*list_of_order[i]).tuple_of_order
            for i in range(len(list_of_order))
        ]

    def find_order_place(self: object, order_id: int) -> tuple:
        """Give order with order_id.

        Args:
            order_id: id from searched order.

        Returns:
            Return tuple that contains informations about order.
        """
        order_info = self.read_db()
        _m = len(order_info)
        for i in range(_m):
            if order_id in order_info[i]:
                return order_info[i]
        return 'not found'

    def dict_all_order(self: object) -> list:
        """Give data that we will have in racks.

        Returns:
            Returns a list of dictionaries from database.
        """
        dict_order = []
        for order in self.read_db():
            _d = {'name': order[0], 'order_id': order[3]}
            dict_order.append(dict(_d, rack_number=order[5]))
        return dict_order

    def make_db_plugin(self: object) -> None:
        """Open new databases during our processing from plugins."""
        con = sqlite3.connect('plug.db')
        cur = con.cursor()
        _l = ('name', 'object', 'amount', 'interrupt')
        _m = ('object', 'amount', 'corridor')
        _n = ('rack_number', 'order_id', 'interrupt')
        _k = ('name', 'corridor', 'rack_number', 'order_id', 'interrupt')
        cur.execute(f'create table if not exists Plugin {_l}')
        cur.execute(f'create table if not exists coll {_m + _n}')
        cur.execute(f'create table if not exists pick {_k}')
        con.close()

    def insert_db_plugin(self: object, _l: list) -> None:
        """Insert information for plugins in plug.db.

        Args:
            _l: List with informations needed in plugins.
        """
        con = sqlite3.connect('plug.db')
        cur = con.cursor()
        _l = tuple(_l)
        if len(self.read_db_plugin()) == 0:
            if len(_l) == 4:
                cur.execute('insert into Plugin values (?, ?, ?, ?)', _l)
                con.commit()
                con.close()
            elif len(_l) == 5:
                cur.execute('insert into pick values (?, ?, ?, ?, ?)', _l)
                con.commit()
                con.close()
            elif len(_l) == 6:
                cur.execute('insert into coll values (?, ?, ?, ?, ?, ?)', _l)
                con.commit()
                con.close()

    def remove_db_plugin(self: object) -> None:
        """Remove Content of plug.db."""
        os.remove('plug.db')
        self.make_db_plugin()

    def read_db_plugin(self: object) -> dict:
        """Give information to plugins.

        Returns:
            Return all information to plugins as dictionary.
        """
        con = sqlite3.connect('plug.db')
        cur = con.cursor()
        plugin_order = []
        for row in cur.execute('select * from Plugin'):
            plugin_order.append(row)
        for row in cur.execute('select * from coll'):
            plugin_order.append(row)
        for row in cur.execute('select * from pick'):
            plugin_order.append(row)
        con.close()
        if plugin_order:
            if len(plugin_order[0]) == 4:
                _l = ['name', 'object', 'amount', 'interrupt']
                return dict(zip(_l, list(plugin_order[0])))
            elif len(plugin_order[0]) == 6:
                _m = ['object', 'amount', 'corridor_number']
                _n = ['rack_number', 'order_id', 'interrupt']
                return dict(zip(_m + _n, list(plugin_order[0])))
            elif len(plugin_order[0]) == 5:
                _p = ['name', 'corridor_number']
                _o = ['rack_number', 'order_id', 'interrupt']
                return dict(zip(_p + _o, list(plugin_order[0])))
        return plugin_order
