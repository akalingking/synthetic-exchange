import datetime as dt
import enum
import itertools


class Order:
    class State(enum.Enum):
        Open = 0
        PartialyFilled = 1
        Filled = 2
        Cancelled = 3
        Failed = 4

    _id = itertools.count()

    def __init__(self, **kwargs):
        self.id = next(__class__._id)
        self.state = __class__.State.Open
        self.market_id = kwargs.get("marketId")
        self.agent_id = kwargs.get("agentId")
        if "dateTime" in kwargs:
            self.datetime = kwargs.get("dateTime")
        else:
            self.datetime = dt.datetime.utcnow()
        self.symbol = kwargs.get("symbol")
        self.side = kwargs.get("side")
        self.price = kwargs.get("price")
        self.quantity = kwargs.get("quantity")
        self.remaining = self.quantity

    def __str__(self):
        return str(self.__dict__)
