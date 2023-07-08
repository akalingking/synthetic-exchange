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

    _last_id = itertools.count()

    def __init__(self, **kwargs):
        try:
            self.state = __class__.State.Open
            self.market_id = kwargs.get("marketid")
            self.agent_id = kwargs.get("agentid")
            if "timestamp" in kwargs:
                val = kwargs.get("timestamp")
                if isinstance(val, float):
                    self.timestamp = val
                elif isinstance(val, dt.datetime):
                    self.timestamp = val.timestamp() * 1000
                if isinstance(val, str):
                    self.timestamp = float(val)
            else:
                self.timestamp = dt.datetime.utcnow().timestamp() * 1000  # ms
            self.symbol = kwargs.get("symbol")
            self.side = kwargs.get("side")
            self.price = kwargs.get("price")
            self.quantity = kwargs.get("quantity")
            self.remaining = self.quantity
            self.cancel = kwargs.get("cancel", False)
            if self.cancel:
                self.id = kwargs.get("orderid")
                assert isinstance(self.id, int)
                assert self.id > 0
            else:
                self.id = next(__class__._last_id)
        except Exception as e:
            logging.error(f"{__class__.__name__}.__init__ exception: {e}")

    def __str__(self):
        retval = {}
        for k, v in self.__dict__.items():
            if k.lower() == "state":
                retval[k] = v.name
            elif k.lower() == "timestamp":
                assert isinstance(v, float)
                retval[k] = v
            else:
                retval[k] = v
        return str(retval)

    def __repr__(self):
        return self.__str__()
