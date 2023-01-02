import logging
import time
import unittest

from synthetic_exchange.agent import Agent
from synthetic_exchange.agents import Agents
from synthetic_exchange.strategy import RandomNormal, RandomUniform


class AgentsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._agents = Agents(marketId=0, symbol="SQNC-RSCH")
        agent_1 = Agent(RandomUniform(minPrice=100, maxPrice=130, tickSize=1, minQuantity=100, maxQuantity=200))
        agent_2 = Agent(RandomNormal(initialPrice=100, minQuantity=100, maxQuantity=200))
        agent_1.strategy.order_event.subscribe(cls._order_event)
        agent_2.strategy.order_event.subscribe(cls._order_event)
        cls._agents.add([agent_1, agent_2])

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def _order_event(order):
        print(f"{__class__.__name__}._order_event order: {order}")

    def test_add_agent(self):
        print(f"{__class__.__name__}.test_add_agent")
        self.assertTrue(self._agents.size > 0)
        self._agents.start()
        time.sleep(10)
        self._agents.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
