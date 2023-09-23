import logging
import multiprocessing as mp
import time
import unittest

from synthetic_exchange.strategy.random_normal import RandomNormal
from synthetic_exchange.strategy.random_uniform import RandomUniform
from synthetic_exchange.transaction import Transactions


class TransactionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        symbols = ["SMBL0", "SMBL1"]
        # 1. Create queue to pass orders from Agents -> OrderBook
        queue = mp.Queue(maxsize=100)
        # 2. Create Agents to drive the OrderBook
        agent_1 = RandomUniform(
            marketId=0,
            symbol=symbols[0],
            minPrice=100,
            maxPrice=130,
            tickSize=1,
            minQuantity=100,
            maxQuantity=200,
            wait=5,
            queue=queue,
        )
        agent_2 = RandomNormal(
            marketId=1, symbol=symbols[1], initialPrice=100, minQuantity=100, maxQuantity=200, wait=5, queue=queue
        )
        cls._agents = {
            agent_1.id: agent_1,
            agent_2.id: agent_2,
        }
        # 3. Create transaction to record buy,sell transactions
        cls._transactions = Transactions(agents=cls._agents)
        cls._wait = 10 * 3

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
        print(f"---{__class__.__name__}.test_transactions")
        for _, agent in self._agents.items():
            agent.start()

        print(f"---{__class__.__name__}.test_transactions run for {self._wait} seconds...")
        time.sleep(self._wait)

        for _, agent in self._agents.items():
            agent.stop()

        # Empty transactions since there is no OrderBook process
        history = self._transactions.history
        logging.info(f"---{__class__.__name__}.test_transactions history: {history}")
        transactions = self._transactions.transactions
        logging.info(f"---{__class__.__name__}.test_transactions transactions: {transactions}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
