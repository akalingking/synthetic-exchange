import logging
import time
import unittest

from synthetic_exchange.agent import Agent
from synthetic_exchange.exchange import Exchange
from synthetic_exchange.market import Market
from synthetic_exchange.order import Order


class ExchangeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 3
        cls._config = {
            "exchange": "test",
            "currencies": [
                {
                    "symbol": "SQNC-RSRCH",
                    "min_price": 100,
                    "max_price": 115,
                    "tick_size": 1,
                    "min_quantity": 0.5,
                    "max_quantity": 1.0,
                },
                {
                    "symbol": "SQNC-TEST",
                    "min_price": 50,
                    "max_price": 53,
                    "tick_size": 1,
                    "min_quantity": 1,
                    "max_quantity": 5,
                },
            ],
        }
        cls._exchange = Exchange(config=cls._config)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_exchange(self):
        logging.info(f"{__class__.__name__}.test_market")
        self._exchange.start()
        time.sleep(self._wait)
        self._exchange.stop()

        currencies = self._config["currencies"]
        symbols = [i["symbol"] for i in currencies]
        exchange_symbols = self._exchange.symbols()
        logging.info(f"---{__class__.__name__}.test_exchange symbols: {exchange_symbols}")
        self.assertTrue(len(exchange_symbols) == 2)
        self.assertTrue(all([i in exchange_symbols for i in symbols]))
        for symbol in symbols:
            ob = self._exchange.orderbook(symbol)
            logging.info(f"---{__class__.__name__}.test_exchange {symbol} ob: {ob}")
            self.assertTrue(isinstance(ob, dict))
            self.assertTrue(all([i in ob for i in ["symbol", "bids", "asks"]]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()