import itertools
import logging


class Agent:
    _counter = itertools.count()

    def __init__(self, strategy, **params):
        self._id = next(__class__._counter)
        self._name = self._id
        self._strategy = strategy
        self._strategy.agent_id = self._id
        self._params = params
        self._position = {}
        self._running_profit = {}
        self._value_bought = {}
        self._quantity_bought = {}
        self._value_sold = {}
        self._quantity_sold = {}
        self._stop = {}
        print(f"{__class__.__name__}.__init__ adding {self.name} strategy: {self.strategy}")

    def start(self):
        self._strategy.start()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def strategy(self):
        return self._strategy

    @property
    def position(self):
        return self._position

    @property
    def value_sold(self):
        return self._value_sold

    @property
    def quantity_sold(self):
        return self._quantity_sold

    @property
    def value_bought(self):
        return self._value_bougth

    @property
    def quantity_bought(self):
        return self._quantity_bought

    def on_orderbook_event(self, event: dict):
        logging.info(f"{__class__.__name__}.on_order_event {self._id}:{self._strategy.name} {event}")
