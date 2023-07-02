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
        symbols = ["SQNC-RSCH", "SQNC-TEST"]
        cls._agents = Agents(marketId=0)
        strategy_1 = RandomUniform(
            marketId=0, symbol=symbols[0], minPrice=100, maxPrice=130, tickSize=1, minQuantity=100, maxQuantity=200
        )
        agent_1 = Agent(strategy=strategy_1)
        agent_1.strategy.order_event.subscribe(cls._order_event)

        strategy_2 = RandomNormal(marketId=1, symbol=symbols[1], initialPrice=100, minQuantity=100, maxQuantity=200)
        agent_2 = Agent(strategy=strategy_2)
        agent_2.strategy.order_event.subscribe(cls._order_event)

        cls._agents.add([agent_1, agent_2])
        cls._transactions = Transactions(marketId=0, agents=cls._agents)

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
        print(f"---{__class__.__name__}._order_event event: {event}")

    def test_transactions(self):
        print(f"---{__class__.__name__}.test_add_agent")
        self.assertTrue(self._agents.size > 0)
        self._agents.start()
        time.sleep(30)
        self._agents.stop()

        history = self._transactions.history
        logging.info(f"---{__class__.__name__}.test_transactions history: {history}")
        transactions = self._transactions.transactions
        logging.info(f"---{__class__.__name__}.test_transactions transactions: {transactions}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
