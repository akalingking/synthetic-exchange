import logging
import multiprocessing as mp
import time
import unittest

from synthetic_exchange.orderbook import OrderBook
from synthetic_exchange.strategy.random_normal import RandomNormal
from synthetic_exchange.strategy.random_uniform import RandomUniform
from synthetic_exchange.transaction import Transactions


class OrderBookTest(unittest.TestCase):
    _transactions_on = True

    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 20
        symbols = ["SQNC-RSCH", "SQNC-TEST"]
        # 1. Order queue from agents -> orderbook
        cls._queue = mp.Queue(maxsize=100)
        # 2. Create agents
        agent_1 = RandomUniform(
            marketId=0,
            symbol=symbols[0],
            minPrice=100,
            maxPrice=130,
            tickSize=1,
            minQuantity=100,
            maxQuantity=200,
            queue=cls._queue,
            wait=5,
        )
        agent_2 = RandomUniform(
            marketId=0,
            symbol=symbols[0],
            minPrice=100,
            maxPrice=130,
            tickSize=1,
            minQuantity=100,
            maxQuantity=200,
            queue=cls._queue,
            wait=5,
        )
        agent_3 = RandomNormal(
            marketId=0, symbol=symbols[0], initialPrice=100, minQuantity=100, maxQuantity=200, queue=cls._queue, wait=5
        )

        cls._agents = {
            agent_1.id: agent_1,
            agent_2.id: agent_2,
            agent_3.id: agent_3,
        }

        # 3. Create transactions
        cls._transactions = Transactions(agents=cls._agents) if __class__._transactions_on else None

        # 4. Create OrderBook
        cls._orderbook = OrderBook(
            marketId=0, symbol=symbols[0], transactions=cls._transactions, wait=5, queue=cls._queue
        )
        for _, agent in cls._agents.items():
            cls._orderbook.events.cancel.subscribe(OrderBookTest._order_event)
            cls._orderbook.events.fill.subscribe(OrderBookTest._order_event)
            cls._orderbook.events.cancel.subscribe(OrderBookTest._order_event)

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

    def test_orderbook(self):
        logging.info(f"---{__class__.__name__}.test_orderbook")

        for _, agent in self._agents.items():
            agent.start()
        self._orderbook.start()

        time.sleep(self._wait)

        self._orderbook.stop()
        for _, agent in self._agents.items():
            agent.stop()

        # Empty transactions since there is no OrderBook process
        if self._transactions is not None:
            history = self._transactions.history
            logging.info(f"---{__class__.__name__}.test_orderbook history: {history}")
            transactions = self._transactions.transactions
            logging.info(f"---{__class__.__name__}.test_orderbook transactions: {transactions}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
