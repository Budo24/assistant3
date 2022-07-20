"""Give content from order."""
import datetime

from processors import nlp_keys


class Order:
    """Give all members from Order."""

    def __init__(self: object, *_li: list) -> None:
        """Initilize order.

        Args:
            _li: List with informations about order.

        """
        self.name = _li[0]
        self.object = _li[1]
        self.amount = _li[2]
        self.order_id = _li[3]
        self.pick_time = _li[4]
        self.rack_number = _li[5]
        self.tuple_of_order = tuple(_li)

    def creat_order(self: object, new_order: list) -> object:
        """Create with new_order an order object.

        Args:
            new_order: Has all properties from class order.

        Returns:
            Return order object with infos in new_order.

        """
        new_order.append(nlp_keys.order_id_generate(datetime.datetime.now()))
        new_order.append(nlp_keys.pick_time_generate(new_order[3]))
        new_order.append(0)
        return Order(*new_order)
