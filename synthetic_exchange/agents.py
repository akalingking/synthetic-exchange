import logging
import multiprocessing as mp
import time
from typing import List

from synthetic_exchange.agent import Agent
from synthetic_exchange.util import Event


class Agents:
    def __init__(self, marketId: int):
        self._market_id = marketId
        self._agents = mp.Manager().dict()
        self._order_event = Event()
        # mp.Process.__init__(self)

    @property
    def market_id(self):
        return self._market_id

    @property
    def agents(self):
        return self._agents

    @property
    def size(self):
        return len(self._agents)

    def add(self, agents: List[Agent]):
        assert isinstance(agents, list)
        agents_ = {item.id: item for item in agents + self._agents.values()}
        self._agents = agents_

    def get(self, agentId: int) -> Agent:
        retval = None
        if agentId in self._agents:
            retval = self._agents[agentId]
        else:
            logging.error(f"{__class__.__name__}.get {agentId} not found")
        return retval

    def start(self):
        self._do_work()

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
        print(f"{__class__.__name__}.on_order_event order: {order}")

    def _do_work(self):
        for i, agent in self._agents.items():
            agent.start()

    def on_buy_event(self, *args, **kwargs):
        raise NotImplementedError()

    def on_sell_event(self, *args, **kwargs):
        raise NotImplementedError()

    def on_cancel_event(self, *args, **kwargs):
        raise NotImplementedError()

    def on_orderbook_event(self, event: dict):
        for i, agent in self._agents.items():
            agent.on_orderbook_event(event)
