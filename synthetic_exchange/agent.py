import itertools
import logging


class Agent:
    _last_id = itertools.count()

    def __init__(self, strategy, **params):
        self.id = next(__class__._last_id)
        self.name = "_".join([strategy.name, str(self.id)])
        self.strategy = strategy
        self.strategy.agent_id = self.id
        self.params = params
        self.position = {}
        self.running_profit = {}
        self.value_bought = {}
        self.quantity_bought = {}
        self.value_sold = {}
        self.quantity_sold = {}
        self.stop = {}
        print(f"{__class__.__name__}.__init__ adding {self.name}")

    def start(self):
        self.strategy.start()

    def on_orderbook_event(self, event: dict):
        logging.info(f"{__class__.__name__}.on_order_event agent id: {self.id} agent name: {self.name} event: {event}")
