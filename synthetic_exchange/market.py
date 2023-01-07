import itertools
import logging
import operator
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from synthetic_exchange import classproperty
from synthetic_exchange.agent import Agent
from synthetic_exchange.agents import Agents
from synthetic_exchange.order import Order
from synthetic_exchange.orderbook import OrderBook
from synthetic_exchange.reports import Reports
from synthetic_exchange.strategy import create_strategy
from synthetic_exchange.transaction import Transaction


class Market:
    """Synthetic exchange generating orderbook for one instrument.
    Multiple markets can be chained to create multi-asset exchange.
    """

    _counter = itertools.count()
    _markets = {}

    def __init__(self, symbol, minPrice=1, maxPrice=100, tickSize=1, minQuantity=1, maxQuantity=100):
        random.seed(100)
        np.random.seed(100)
        self._symbol = symbol
        self._id = next(__class__._counter)
        # self._transaction_counter = 0
        self._min_price = minPrice
        self._max_price = maxPrice
        self._tick_size = tickSize
        self._min_quantity = minQuantity
        self._max_quantity = maxQuantity
        self._agents = Agents(self._id, symbol)
        self._orderbook = OrderBook(self._id, symbol)
        self._reports = Reports(self._id)

        # Create agents
        self._agents = Agents(symbol=symbol, marketId=0)
        agent_1 = Agent(
            create_strategy(
                name="RandomUniform",
                minPrice=100,
                maxPrice=150,
                tickSize=1,
                minQuantity=10,
                maxQuantity=25,
                marketId=self._id,
                symbol=symbol,
                handler=__class__._order_event,
            )
        )
        self._agents.add([agent_1])

        __class__._markets[self._id] = self

        self._orderbook.events.partial_fill.subscribe(__class__._orderbook_event)
        self._orderbook.events.fill.subscribe(__class__._orderbook_event)
        self._orderbook.events.cancel.subscribe(__class__._orderbook_event)

    @staticmethod
    def _orderbook_event(event: dict):
        try:
            market_id = event["_market_id"]
            assert market_id is not None
            assert market_id in __class__._markets
            __class__._markets[market_id]._agents.on_orderbook_event(event)
        except Exception as e:
            logging.error(f"{__class__.__name__}._orderbook_event exception: {e}")

    @staticmethod
    def _order_event(order: dict):
        print(f"{__class__.__name__}._order_event: {order}")
        assert isinstance(order, dict)
        if "marketId" in order:
            market_id = order.get("marketId")
            if market_id in __class__._markets:
                market = __class__._markets[market_id]
                assert market is not None
                order_ = Order(**order)
                assert order_ is not None
                market.on_order_event(order_)
            else:
                logging.error(f"{__class__.__name__}._order_event invalid market id: {market_id}")
        else:
            logging.error(f"{__class__.__name__}._order_event missing market id")

    def on_order_event(self, order: Order):
        self._orderbook.process(order)

    @property
    def agents(self):
        return self._agents

    @property
    def id(self):
        return self._id

    @property
    def tick_size(self):
        return self._tick_size

    @property
    def max_price(self):
        return self._max_price

    @property
    def min_price(self):
        return self._min_price

    @property
    def max_quantity(self):
        return self._max_quantity

    @property
    def min_quantity(self):
        return self._min_quantity

    # @property
    # def transaction_counter(self):
    #    #return self._transaction_counter
    #    return Transaction.transaction_counter

    # @transaction_counter.setter
    # def transaction_counter(self, value):
    #    self._transaction_counter = value

    def start(self, n=1000, clearAt=10000):
        # c = 1
        """
        for o in range(n):
            for i, agent in self._agents.agents.items():
                if self._id in Transaction.history:
                    last_transaction_id = Transaction.history[self._id][-1].id
                else:
                    self._strategies.add(self._id, agent.id, agent.strategy)
        """

        # c += 1
        # if c % clearAt == 0:
        #    self.clear()
        self._agents.start()
        logging.info(">>>agents started")
        self._orderbook.start()
        logging.info(">>>orderbook started")

    def stop(self):
        self._agents.stop()
        self._orderbook.stop()

    def clear(self):
        Order.active_buy_orders[self._id] = []
        Order.active_sell_orders[self._id] = []

    def add_agents(self, agents: list):
        self._agents.add(agents)

    def show_transactions(self):
        self._reports.show_transactions(self._orderbooks.transactions)
        """
        df = pd.DataFrame(Transaction.history_list(self.id), columns=["id", "time", "price"])
        df["volatility"] = df["price"].rolling(7).std()
        df["volatilityTrend"] = df["volatility"].rolling(100).mean()
        df = df[["id", "price", "volatility", "volatilityTrend"]]
        df = df.set_index("id")

        dfPrice = df["price"]
        dfVolatility = df[["volatility", "volatilityTrend"]]

        # PLOT PRICE
        fig, axs = plt.subplots(2, 2)
        axs[0, 0].plot(dfPrice, label="price")
        axs[0, 0].set_title("Price")
        axs[0, 0].legend()
        # PLOT VOLATILITY
        axs[0, 1].plot(dfVolatility)
        axs[0, 1].set_title("Volatility")
        axs[0, 1].legend()
        # PLOT RUNNING POSITIONS + RUNNING PROFITS AGENTS
        for i, a in self._agents.agents.items():
            right = pd.DataFrame(
                Transaction.history_market_agent(self.id, a.name), columns=["id", a.name, str(a.name) + "RunningProfit"]
            )
            right = right.set_index("id")
            right = right[a.name]
            axs[1, 0].plot(right, label=str(a.name))
        axs[1, 0].set_title("Positions")

        if self._agents.size < 20:
            axs[1, 0].legend()

        for i, a in self._agents.agents.items():
            right = pd.DataFrame(
                Transaction.history_market_agent(self.id, a.name), columns=["id", a.name, str(a.name) + "RunningProfit"]
            )
            right = right.set_index("id")
            right = right[str(a.name) + "RunningProfit"]
            axs[1, 1].plot(right, label=str(a.name) + "RunningProfit")

        axs[1, 1].set_title("Running profit")
        return plt.show()
        """

    """
    def showOrderbook(self, show_depth=10):
        widthOrderbook = len("0       Bert    Buy     33      5")
        print(widthOrderbook * 2 * "*")

        if self.id in Order.active_sell_orders:
            for sellOrder in sorted(Order.active_sell_orders[self.id], key=operator.attrgetter("price"), reverse=True)[
                :show_depth
            ]:
                print(widthOrderbook * "." + " " + str(sellOrder))
        if self.id in Order._active_buy_orders:
            buy_orders = sorted(Order.active_buy_orders[self.id], key=operator.attrgetter("price"), reverse=True)[
                :show_depth
            ]
            for buy_order in buy_orders:
                print(str(buy_order) + " " + widthOrderbook * ".")

        print(widthOrderbook * 2 * "*")
        print(" ")
    """

    def show_orderbook(self, depth: int = 10):
        self._reports.show_orderbook(self._orderbook, depth)

    @staticmethod
    def get_max_price(marketId):
        retval = None
        if marketId in __class__._markets:
            retval = __class__._markets[marketId].max_price
        return retval

    @staticmethod
    def get_last_price(marketId):
        retval = None
        if marketId in __class__._markets:
            if marketId in Transaction.history:
                retval = Transaction.history[marketId][-1].price
            else:
                market = __class__._markets[marketId]
                retval = (market.max_price - market.min_price) / 2
        else:
            logging.error(f"{__class__.__name__}.get_last_price {marketId} not found")
        return retval

    @staticmethod
    def show_transactions_by_id(marketId):
        assert marketId in __class__._markets
        __class__._markets[marketId].show_transactions()

    @staticmethod
    def show_orderbook_by_id(marketId: int, depth: int = 10):
        assert marketId in __class__._markets
        __class__._markets[marketId].show_orderbook(depth)
