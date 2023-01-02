import datetime as dt
import itertools


class Order:
    _counter = itertools.count()

    # def __init__(self, marketId, agentId, symbol, side, price, quantity):
    def __init__(self, **kwargs):
        self._id = next(__class__._counter)
        self._market_id = kwargs.get("marketId")
        self._agent_id = kwargs.get("agentId")
        if "dateTime" in kwargs:
            self._datetime = kwargs.get("dateTime")
        else:
            self._datetime = dt.datetime.utcnow()
        self._symbol = kwargs.get("symbol")
        self._side = kwargs.get("side")
        self._price = kwargs.get("price")  # round(price/market.tick_size) * market.tick_size
        self._quantity = kwargs.get("quantity")

    @property
    def id(self):
        return self._id

    @property
    def datetime(self):
        return self._datetime

    @property
    def market_id(self):
        return self._market_id

    @property
    def agemt_id(self):
        return self._agent_id

    @property
    def price(self):
        return self._price

    @property
    def side(self):
        return self._side

    @property
    def quantity(self):
        return self._quantity

    """
    @staticmethod
    def from_dict(data: dict) -> Order:
        retval = None
        try:
            retval = Order(
                marketId=data["marketId"],
                agentId=data["agentId"],
        except Exception as e:
            logging.error(f"{__class__.__name__}.from_dict e: {e}")
        return retval
    """
