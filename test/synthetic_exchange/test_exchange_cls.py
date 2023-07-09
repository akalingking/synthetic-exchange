import logging
import multiprocessing as mp
import time
import unittest

from synthetic_exchange import OrderBook, Transactions
from synthetic_exchange.exchange import Exchange
from synthetic_exchange.market import Market
from synthetic_exchange.order import Order
from synthetic_exchange.strategy import RandomNormal, RandomUniform


class ExchangeClsTest(unittest.TestCase):
    _transactions_on = True

    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 30
        cls._config = {
            "exchange": "sqncrsch",
            "api_enable": True,
            "markets": [
                {
                    "marketId": 0,
                    "symbol": "SQNC-RSRCH",
                    "initialPrice": 100.0,
                    "minPrice": 100.0,
                    "maxPrice": 115.0,
                    "tickSize": 1,
                    "minQuantity": 0.5,
                    "maxQuantity": 1.0,
                    "agents": {
                        "agent_1": {
                            "type": "randomnormal",
                            "initialPrice": 50.0,
                            "minPrice": 50.0,
                            "maxPrice": 53.0,
                            "tickSize": 1,
                            "minQuantity": 1.0,
                            "maxQuantity": 5.0,
                        },
                        "agent_2": {
                            "type": "randomnormal",
                            "initialPrice": 50.0,
                            "minPrice": 50.0,
                            "maxPrice": 53.0,
                            "tickSize": 1,
                            "minQuantity": 1.0,
                            "maxQuantity": 5.0,
                        },
                    },
                },
                {
                    "marketId": 1,
                    "symbol": "SQNC-TEST",
                    "initialPrice": 50.0,
                    "minPrice": 50.0,
                    "maxPrice": 53.0,
                    "tickSize": 1,
                    "minQuantity": 1.0,
                    "maxQuantity": 5.0,
                    "agents": {
                        "agent_1": {
                            "type": "randomnormal",
                            "initialPrice": 100.0,
                            "minPrice": 100.0,
                            "maxPrice": 115.0,
                            "tickSize": 1,
                            "minQuantity": 1.0,
                            "maxQuantity": 5.0,
                        },
                        "agent2": {
                            "type": "randomuniform",
                            "initialPrice": 100.0,
                            "minPrice": 100.0,
                            "maxPrice": 115.0,
                            "tickSize": 1,
                            "minQuantity": 1.0,
                            "maxQuantity": 5.0,
                        },
                    },
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

        symbols = self._exchange.symbols()

        for symbol in symbols:
            print(f"******{symbol} orderbook*******")
            ob_ = self._exchange.orderbook(symbol=symbol)
            print(ob_)
            self.assertTrue(i in ob_ for i in ["symbol", "bids", "asks"])
            print(f"******{symbol} orderbook*******")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
