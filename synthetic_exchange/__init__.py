# from .exchange import Exchange
from .order import Order
from .orderbook import OrderBook
from .transaction import Transaction


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
