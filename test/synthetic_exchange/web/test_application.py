import logging
import multiprocessing as mp
import time
import unittest

from synthetic_exchange.app.web.application import WebApplication


class ApplicationTest(unittest.TestCase):
    _transactions_on = True

    @classmethod
    def setUpClass(cls):
        cls._wait = 30 * 1
        cls._config = {"application": {}}
        cls._exchange = WebApplication(**cls._config)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_exchange(self):
        logging.info(f"{__class__.__name__}.test_exchange")

        self._exchange.start()

        time.sleep(self._wait)

        self._exchange.stop()

        symbols = self._exchange._markets.keys()
        for symbol in symbols:
            print(f"******exchange: {self._exchange.name} symbol: {symbol} orderbook*******")
            ob_ = self._exchange.orderbook(symbol=symbol)
            print(ob_)
            self.assertTrue(i in ob_ for i in ["symbol", "bids", "asks"])
            print(f"******exchange: {self._exchange.name} symbol: {symbol} orderbook*******")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
