import logging
import time
import unittest

from synthetic_exchange.agent import Agent
from synthetic_exchange.market import Market
from synthetic_exchange.strategy import create_strategy


class MarketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        symbol = "SQNC-RSCH"
        cls._market = Market(symbol=symbol, minPrice=100, maxPrice=200, tickSize=1, minQuantity=25, maxQuantity=50)
        """
        agents = []
        agent_1 = Agent(
            create_strategy(
                name="RandomUniform",
                minPrice=100,
                maxPrice=150,
                tickSize=1,
                minQuantity=10,
                maxQuantity=25,
                marketId=cls._market.id,
                symbol=symbol,
                handler=__class__._order_event,
            )
        )
        agents.append(agent_1)
        cls._market.add_agents(agents)
        """

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
        """
        agents = []
        agent_1 = Agent(
            create_strategy(
                name="RandomUniform",
                minPrice=100,
                maxPrice=150,
                tickSize=1,
                minQuantity=10,
                maxQuantity=25,
                marketId=self._market.id,
                symbol=self._market.symbol,
                handler=__class__._order_event,
            )
        )
        agents.append(agent_1)
        self._market.add_agents(agents)
        """

        self._market.start()
        time.sleep(60 * 2)
        self._market.stop()
        self.assertTrue(self._market._transactions is not None)
        self.assertTrue(self._market._transactions.agents is not None)
        self.assertTrue(self._market._transactions.agents.agents is not None)
        self.assertTrue(self._market._orderbook.transactions.size > 0)
        self._market.show_transactions()
        self._market.show_orderbook()
        ret = self._market.orderbook()
        buy_orders, sell_orders = self._market._orderbook.orderbook_raw()
        self.assertTrue(isinstance(buy_orders, list))
        self.assertTrue(isinstance(sell_orders, list))
        print(ret)
        self.assertTrue(len(ret["buy"]) == len(buy_orders))
        self.assertTrue(len(ret["sell"]) == len(sell_orders))
        print(f"buy price: {self._market.get_buy_price()}")
        print(f"sell price: {self._market.get_sell_price()}")
        print(f"spread: {self._market.get_spread()}")
        print(f"mid price: {self._market.get_mid_price()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
