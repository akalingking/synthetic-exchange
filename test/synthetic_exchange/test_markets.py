import logging
import multiprocessing as mp
import time
import unittest

from synthetic_exchange import OrderBook, Transactions
from synthetic_exchange.exchange import Exchange
from synthetic_exchange.market import Market
from synthetic_exchange.order import Order
from synthetic_exchange.strategy import RandomNormal, RandomUniform


class MarketsTest(unittest.TestCase):
    """Test multiple markets"""

    _transactions_on = True

    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 3
        cls._config = {
            "exchange": "exchange_0",
            "markets": [
                {
                    "marketId": 0,
                    "symbol": "SMBL0",
                    "initialPrice": 100.0,
                    "minPrice": 100.0,
                    "maxPrice": 115.0,
                    "tickSize": 1,
                    "minQuantity": 0.5,
                    "maxQuantity": 1.0,
                },
                {
                    "marketId": 1,
                    "symbol": "SMBL1",
                    "initialPrice": 50.0,
                    "minPrice": 50.0,
                    "maxPrice": 53.0,
                    "tickSize": 1,
                    "minQuantity": 1.0,
                    "maxQuantity": 5.0,
                },
            ],
        }
        cls._queues = {}
        cls._agents = {}
        cls._transactions = {}
        cls._orderbooks = {}
        cls._markets = {}

        markets = cls._config["markets"]
        for market in markets:
            market_id = market["marketId"]
            symbol = market["symbol"]
            initial_price = market["initialPrice"]
            min_price = market["minPrice"]
            max_price = market["maxPrice"]
            tick_size = market["tickSize"]
            min_quantity = market["minQuantity"]
            max_quantity = market["maxQuantity"]

            cls._queues[market_id] = mp.Queue(maxsize=100)

            agent_0 = RandomUniform(
                marketId=market_id,
                agentId=0,
                symbol=symbol,
                minPrice=min_price,
                maxPrice=max_price,
                tickSize=tick_size,
                minQuantity=min_quantity,
                maxQuantity=max_quantity,
                queue=cls._queues[market_id],
                wait=5,
            )
            agent_1 = RandomUniform(
                marketId=market_id,
                agentId=1,
                symbol=symbol,
                minPrice=min_price,
                maxPrice=max_price,
                tickSize=tick_size,
                minQuantity=min_quantity,
                maxQuantity=max_quantity,
                queue=cls._queues[market_id],
                wait=5,
            )
            agent_2 = RandomNormal(
                marketId=market_id,
                agentId=2,
                symbol=symbol,
                initialPrice=initial_price,
                minQuantity=min_quantity,
                maxQuantity=max_quantity,
                queue=cls._queues[market_id],
                wait=5,
            )

            cls._agents = {
                market_id: {
                    agent_0.id: agent_0,
                    agent_1.id: agent_1,
                    agent_2.id: agent_2,
                }
            }

            # 3. Create transactions
            cls._transactions[market_id] = (
                Transactions(agents=cls._agents[market_id]) if __class__._transactions_on else None
            )

            # 4. Create OrderBook
            cls._orderbooks[market_id] = OrderBook(
                marketId=market_id,
                symbol=symbol,
                transactions=cls._transactions[market_id],
                queue=cls._queues[market_id],
                wait=5,
            )
            cls._markets[market_id] = Market(orderbook=cls._orderbooks[market_id])

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_markets(self):
        logging.info(f"{__class__.__name__}.test_markets")

        for _, market in self._markets.items():
            market.start()

        time.sleep(self._wait)

        for _, market in self._markets.items():
            market.stop()

        # Show all transactions
        for _, market in self._markets.items():
            print(f"******{market.symbol} transactions*******")
            for k, v in market.transactions.transactions.items():
                print(v)
            print(f"******{market.symbol} transactions*******")
        # Show history
        for _, market in self._markets.items():
            print(f"******{market.symbol} history*******")
            for v in market.transactions.history:
                print(v)
            print(f"******{market.symbol} history*******")

        for _, ob in self._orderbooks.items():
            print(f"******{ob.symbol} orderbook*******")
            ob_ = ob.orderbook()
            print(ob_)
            self.assertTrue(i in ob_ for i in ["symbol", "bids", "asks"])
            print(f"******{ob.symbol} orderbook*******")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
