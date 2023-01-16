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
        self.position = 0
        self.running_profit = 0.0
        self.value_bought = 0.0
        self.quantity_bought = 0.0
        self.value_sold = 0.0
        self.quantity_sold = 0.0
        # self.stop = {}
        print(f"{__class__.__name__}.__init__ adding {self.name}")

    def start(self):
        self.strategy.start()

    def on_orderbook_event(self, event: dict):
        logging.info(f"{__class__.__name__}.on_order_event agent id: {self.id} agent name: {self.name} event: {event}")
