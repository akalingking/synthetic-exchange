import itertools
import multiprocessing as mp

from synthetic_exchange.app import Application


class Agent(Application):
    _last_id = itertools.count()

    def __init__(self, *args, **kwargs):
        self._id = kwargs.get("agentId", None)
        if self._id is None:
            self._id = next(__class__._last_id)
        Application.__init__(self, *args, **kwargs)
        self._marketid = kwargs.get("marketId")
        self._symbol = kwargs.get("symbol")
        assert self._symbol is not None and len(self._symbol) > 0
        self._queue = kwargs.get("queue", None)
        self._inflight_orders = mp.Manager().dict()
        self._positions = mp.Manager().dict()
        # backward compatibility
        self.position = 0.0
        self.quantity_bought = 0.0
        self.quantity_sold = 0.0
        self.value_bought = 0.0
        self.value_sold = 0.0

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self.__class__.__name__.lower()

    def _do_work(self):
        raise NotImplementedError()

    def orderbook_event(self, event: dict):
        raise NotImplementedError()
