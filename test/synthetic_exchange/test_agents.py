import logging
import time
import unittest

from synthetic_exchange.agent import Agent
from synthetic_exchange.agents import Agents
from synthetic_exchange.order import Order
from synthetic_exchange.strategy import RandomNormal, RandomUniform


class AgentsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 3
        symbols = ["SQNC-RSCH", "SQNC-TEST"]
        cls._agents = Agents(marketId=0)
        agent_1 = Agent(
            strategy=RandomUniform(
                marketId=0, symbol=symbols[0], minPrice=100, maxPrice=130, tickSize=1, minQuantity=100, maxQuantity=200
            )
        )
        agent_2 = Agent(
            strategy=RandomNormal(marketId=1, symbol=symbols[1], initialPrice=100, minQuantity=100, maxQuantity=200)
        )
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
    def _order_event(event: dict):
        assert isinstance(event, dict)
        logging.info(f"---{__class__.__name__}._order_event event: {event}")
        assert event["state"].lower() == "open"  # Only open states

    def test_add_agent(self):
        logging.info(f"---{__class__.__name__}.test_add_agent")
        self.assertTrue(self._agents.size > 0)
        self._agents.start()
        time.sleep(self._wait)
        self._agents.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
