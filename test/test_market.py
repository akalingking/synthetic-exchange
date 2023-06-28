import logging
import time
import unittest

from synthetic_exchange.agent import Agent
from synthetic_exchange.market import Market
from synthetic_exchange.order import Order
from synthetic_exchange.strategy import create_strategy


class MarketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 2
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
    def _order_event(order: Order):
        logging.info(f"{__class__.__name__}._order_event order: {order}")

    def test_market(self):
        logging.info(f"{__class__.__name__}.test_market")
        self._market.start()
        time.sleep(self._wait)
        self._market.stop()
        self.assertTrue(self._market._transactions is not None)
        self.assertTrue(self._market._transactions.agents is not None)
        self.assertTrue(self._market._transactions.agents.agents is not None)
        self.assertTrue(self._market._orderbook.transactions.size > 0)
        self._market.show_transactions()
        self._market.show_orderbook()
        ret = self._market.orderbook()
        print(f"---{__class__.__name__}.test_market orderbook: {ret}")
        buy_orders, sell_orders = self._market._orderbook.orderbook_raw()
        print(f"---buy_orders: {buy_orders}")
        self.assertTrue(isinstance(buy_orders, list))
        self.assertTrue(isinstance(sell_orders, list))
        print(ret)
        self.assertTrue(len(ret["buy"]) == len(buy_orders))
        self.assertTrue(len(ret["sell"]) == len(sell_orders))
        print(f"---{__class__.__name__}.test_market buy price: {self._market.get_buy_price()}")
        print(f"---{__class__.__name__}.test_market sell price: {self._market.get_sell_price()}")
        print(f"---{__class__.__name__}.test_market spread: {self._market.get_spread()}")
        print(f"---{__class__.__name__}.test_market mid price: {self._market.get_mid_price()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
