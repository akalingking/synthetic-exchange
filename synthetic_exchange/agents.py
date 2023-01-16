import logging
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
    def agents(self):
        return self._agents

    @property
    def size(self):
        return len(self._agents)

    def add(self, agents):
        assert isinstance(agents, list)
        for agent in agents:
            assert isinstance(agent, Agent)
            self._agents[agent.id] = agent

    def get(self, agentId: int) -> Agent:
        retval = None
        if agentId in self._agents:
            retval = self._agents[agentId]
        else:
            logging.error(f"{__class__.__name__}.get {agentId} not found")
        return retval

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

    def on_orderbook_event(self, event: dict):
        for i, agent in self._agents.items():
            agent.on_orderbook_event(event)
