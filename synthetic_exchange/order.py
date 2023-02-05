import datetime as dt
import enum
import itertools
import json
import logging
import multiprocessing as mp


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
        try:
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
            self.cancel = kwargs.get("cancel", False)
            if self.cancel:
                self.order_id = kwargs.get("orderId")
                assert isinstance(self.order_id, int)
                assert self.order_id > 0
        except Exception as e:
            logging.error(f"{__class__.__name__}.__init__ exception: {e}")

    def __str__(self):
        retval = {}
        for k, v in self.__dict__.items():
            if k.lower() == "state":
                retval[k] = v.name
            elif k.lower() == "datetime":
                retval[k] = v.isoformat()
            else:
                retval[k] = v
        return str(retval)

    def __repr__(self):
        return self.__str__()
