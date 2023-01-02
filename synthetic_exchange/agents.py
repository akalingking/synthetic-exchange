import time
from multiprocessing import Process

from synthetic_exchange.agent import Agent
from synthetic_exchange.utils.observer import Event


class Agents:
    def __init__(self, marketId: int, symbol: str):
        self._market_id = marketId
        self._symbol = symbol
        self._agents = {}
        self._order_event = Event()

    @property
    def market_id(self):
        return self._market_id

    @property
    def symbol(self):
        return self._symbol

    @property
    def size(self):
        return len(self._agents)

    def add(self, agents):
        assert isinstance(agents, list)
        for agent in agents:
            self._agents[agent.id] = agent

    def start(self):
        print(f"{__class__.__name__}.start entry")
        self._do_work()
        print(f"{__class__.__name__}.start exit")

    def stop(self):
        self._run = False
        for i, agent in self._agents.items():
            agent.strategy.stop()
        self.wait()

    def wait(self):
        for i, agent in self._agents.items():
            agent.strategy.wait()

    @staticmethod
    def on_order_event(order: tuple):
        print(f"on_order_event order: {order}")

    def _do_work(self):
        for i, agent in self._agents.items():
            agent.start()

    def on_buy_event(self, *args, **kwargs):
        pass

    def on_sell_event(self, *args, **kwargs):
        pass

    def on_cancel_event(self, *args, **kwargs):
        pass
