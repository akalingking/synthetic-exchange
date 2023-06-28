import logging
import time
import unittest

from synthetic_exchange.agent import Agent
from synthetic_exchange.agents import Agents
from synthetic_exchange.strategy import RandomNormal, RandomUniform
from synthetic_exchange.transaction import Transactions


class TransactionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._agents = Agents(marketId=0, symbol="SQNC-RSCH")
        agent_1 = Agent(RandomUniform(minPrice=100, maxPrice=130, tickSize=1, minQuantity=100, maxQuantity=200))
        agent_2 = Agent(RandomNormal(initialPrice=100, minQuantity=100, maxQuantity=200))
        agent_1.strategy.order_event.subscribe(cls._order_event)
        agent_2.strategy.order_event.subscribe(cls._order_event)
        cls._agents.add([agent_1, agent_2])
        cls._transactions = Transactions(0, cls._agents)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def _order_event(order):
        print(f"---{__class__.__name__}._order_event order: {order}")

    def test_transactions(self):
        print(f"{__class__.__name__}.test_add_agent")
        self.assertTrue(self._agents.size > 0)
        self._agents.start()
        time.sleep(30)
        self._agents.stop()

        history = self._transactions.history
        logging.info(f"---{__class__.__name__}.test_transactions history: {history}")
        history_list = self._transactions.history_list
        logging.info(f"---{__class__.__name__}.test_transactions history_list: {history_list}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
