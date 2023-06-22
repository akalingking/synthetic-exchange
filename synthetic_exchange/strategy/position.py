import itertools
import logging

from synthetic_exchange.order import Order


class Position:
    _id = itertools.count()

    def __init__(self, openOrder: Order):
        self.id = next(__class__._id)
        self.open = openOrder
        self.close = None
