"""Give content from order."""


class Order:
    """Give all members from Order."""

    def __init__(self, _li: list[str | int]) -> None:
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

    def make_tuple(self, _m: list[str | int]) -> tuple[str | int, ...]:
        """Make tuple for insert_db().

        Args:
            _m: List of order members.

        Returns:
            Return tuple of order elements.

        """
        return tuple(_m)

    def make_list_order(self) -> tuple[str | int, ...]:
        """Make tuple with order member.

        Returns:
            Return tuple order.

        """
        _k = [self.name, self.object, self.amount]
        _n = [self.order_id, self.pick_time, self.rack_number]
        return self.make_tuple(_k + _n)
