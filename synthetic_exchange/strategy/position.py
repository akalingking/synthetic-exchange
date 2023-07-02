import itertools
import logging

from synthetic_exchange.order import Order


class Position:
    _last_id = itertools.count()

    def __init__(self, order: Order):
        self._id = next(__class__._last_id)
        self._open_price = order.price
        self._size = order.quantity
        self._fill_price = 0
        self._remaining_size = 0
        self._average_fill_price
