import logging
import time
import unittest

from synthetic_exchange.market import Market


class MarketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        symbol = "SQNC-RSCH"
        cls._market = Market(symbol=symbol, minPrice=100, maxPrice=200, tickSize=1, minQuantity=25, maxQuantity=50)

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

    def test_market(self):
        print(f"{__class__.__name__}.test_market")
        self._market.start()
        time.sleep(30)
        self._market.stop()
        assert self._market.transactions is not None
        assert self._market.transactions.agents is not None
        assert self._market.transactions.agents.agents is not None
        assert self._market.orderbook.transactions.size > 0
        self._market.show_transactions()
        self._market.show_orderbook()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
