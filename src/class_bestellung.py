import nlp_key
import datetime


class Order:

    def __init__(self, name, object, amount, order_id, pick_time, rack_number):
        self.name = name
        self.object = object
        self.amount = amount
        self.order_id = order_id
        self.pick_time = pick_time
        self.rack_number = rack_number
        self.tuple_of_order = (name, object, amount, order_id, pick_time,
                               rack_number)


if __name__ == '__main__':
    day_time_func = datetime.datetime.now()
    x = Order(
        'hamza', 'screw', 15, nlp_key.order_id_generate(day_time_func),
        nlp_key.pick_time_generate(nlp_key.order_id_generate(day_time_func)),
        15)
    print(x.tuple_of_order)