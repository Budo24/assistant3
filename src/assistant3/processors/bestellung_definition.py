"""Give content from order."""


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
