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
from synthetic_exchange.transaction import Transaction, Transactions


class Market:
    """Synthetic exchange generating orderbook for one instrument.
    Multiple markets can be chained to create multi-asset exchange.
    """

    _last_id = itertools.count()
    _markets = {}

    def __init__(self, symbol, minPrice=1, maxPrice=100, tickSize=1, minQuantity=1, maxQuantity=100):
        random.seed(100)
        np.random.seed(100)
        self._symbol = symbol
        self._id = next(__class__._last_id)
        self._min_price = minPrice
        self._max_price = maxPrice
        self._tick_size = tickSize
        self._min_quantity = minQuantity
        self._max_quantity = maxQuantity
        self._agents = Agents(self._id, symbol)
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
        self._transactions = Transactions(self._id, self._agents)

        self._orderbook = OrderBook(self._id, symbol, self._transactions)
        self._orderbook.events.partial_fill.subscribe(__class__._orderbook_event)
        self._orderbook.events.fill.subscribe(__class__._orderbook_event)
        self._orderbook.events.cancel.subscribe(__class__._orderbook_event)

    @staticmethod
    def _orderbook_event(event: dict):
        try:
            assert "market_id" in event
            market_id = event["market_id"]
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
    def reports(self):
        return self._reports

    @property
    def transactions(self):
        return self._transactions

    @property
    def agents(self):
        return self._agents

    @property
    def orderbook(self):
        return self._orderbook

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

    def start(self, n=1000, clearAt=10000):
        self._agents.start()
        self._orderbook.start()

    def stop(self):
        self._orderbook.stop()
        self._agents.stop()

    def clear(self):
        Order.active_buy_orders[self._id] = []
        Order.active_sell_orders[self._id] = []

    def add_agents(self, agents: list):
        self._agents.add(agents)

    def show_transactions(self):
        assert self._transactions is not None
        assert self._transactions.size > 0
        assert self._orderbook.transactions.size > 0
        self._reports.show_transactions(self._orderbook.transactions)

    def show_orderbook(self, depth: int = 10):
        self._reports.show_orderbook(self._orderbook, depth)

    def get_last_price(self):
        retval = None
        if len(self._transactions.history) > 0:
            retval = self._transactions.history[-1].price
        else:
            retval = self._max_price - self._min_price / 2.0
        return retval

    @staticmethod
    def get_max_price(marketId):
        retval = None
        if marketId in __class__._markets:
            retval = __class__._markets[marketId].max_price
        return retval

    """
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
    """

    @staticmethod
    def show_transactions_by_id(marketId):
        assert marketId in __class__._markets
        __class__._markets[marketId].show_transactions()

    @staticmethod
    def show_orderbook_by_id(marketId: int, depth: int = 10):
        assert marketId in __class__._markets
        __class__._markets[marketId].show_orderbook(depth)
