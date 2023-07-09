import logging
import multiprocessing as mp
import time
import unittest

from synthetic_exchange import OrderBook, Transactions
from synthetic_exchange.exchange import Exchange
from synthetic_exchange.market import Market
from synthetic_exchange.order import Order
from synthetic_exchange.strategy import RandomNormal, RandomUniform


class ExchangesTest(unittest.TestCase):
    _transactions_on = True

    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 10
        # Sample exchange config
        cls._exchange_0_config = {
            "exchangeId": 0,
            "exchange": "exchange_0",
            "api_enable": True,
            "markets": [
                {
                    "marketId": 0,
                    "symbol": "SMBL1",
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
                    "symbol": "SMBL2",
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
                        "agent_2": {
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
        cls._exchange_1_config = cls._exchange_0_config
        cls._exchange_1_config["exchangeId"] = 1
        cls._exchange_1_config["exchange"] = "exchange_1"

        cls._exchange_configs = {
            0: cls._exchange_0_config,
            1: cls._exchange_1_config,
        }

        cls._exchanges = {}
        for exchange_id, config in cls._exchange_configs.items():
            cls._exchanges[exchange_id] = Exchange(config=config)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_exchanges(self):
        logging.info(f"{__class__.__name__}.test_exchanges")

        for _, exchange in self._exchanges.items():
            exchange.start()

        time.sleep(self._wait)

        for _, exchange in self._exchanges.items():
            exchange.stop()

        for id_, exchange in self._exchanges.items():
            symbols = exchange.symbols()
            for symbol in symbols:
                print(f"******exchange: {exchange.name} symbol: {symbol} orderbook*******")
                ob_ = exchange.orderbook(symbol=symbol)
                print(ob_)
                self.assertTrue(i in ob_ for i in ["symbol", "bids", "asks"])
                print(f"******exchange: {exchange.name} symbol: {symbol} orderbook*******")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
