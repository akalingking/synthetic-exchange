import itertools
import logging
import multiprocessing as mp
import operator
import random
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from synthetic_exchange.agent import Agent
from synthetic_exchange.agents import Agents
from synthetic_exchange.order import Order
from synthetic_exchange.orderbook import OrderBook
from synthetic_exchange.reports import Reports
from synthetic_exchange.strategy import create_strategy
from synthetic_exchange.transaction import Transaction, Transactions


class Market:
    """Synthetic exchange generating orderbook for one instrument."""

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
        self._orderbook = None
        self._reports = Reports(self._id)
        __class__._markets[self._id] = self

    def _create_agents(self):
        self._agents = Agents(marketId=self._id)
        agents = []

        strategy_1 = create_strategy(
            name="RandomUniform",
            minPrice=100,
            maxPrice=150,
            tickSize=1,
            minQuantity=10,
            maxQuantity=25,
            marketId=self._id,
            symbol=self._symbol,
            handler=__class__._order_event,
        )
        agent_1 = Agent(strategy_1)
        agents.append(agent_1)

        strategy_2 = create_strategy(
            name="RandomUniform",
            minPrice=100,
            maxPrice=150,
            tickSize=1,
            minQuantity=10,
            maxQuantity=25,
            marketId=self._id,
            symbol=self._symbol,
            handler=__class__._order_event,
        )
        agent_2 = Agent(strategy_2)
        agents.append(agent_2)
        self._agents.add(agents)

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
    def _order_event(event: dict):
        logging.info(f"{__class__.__name__}._order_event: {event}")
        assert isinstance(event, dict)
        if "marketid" in event:
            market_id = event.get("marketid")
            if market_id in __class__._markets:
                market = __class__._markets[market_id]
                assert market is not None
                order = Order(**event)
                assert order is not None
                market.on_order_event(order)
            else:
                logging.error(f"{__class__.__name__}._order_event invalid market id: {market_id}")
        else:
            logging.error(f"{__class__.__name__}._order_event missing market id")

    def on_order_event(self, order: Order):
        assert isinstance(order, Order)
        self._orderbook.process(order)

    @property
    def reports(self):
        return self._reports

    @property
    def transactions(self):
        return self._transactions

    def orderbook(self, depth: int = -1) -> dict:
        return self._orderbook.orderbook(depth)

    @property
    def symbol(self):
        return self._symbol

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
        self._create_agents()
        assert self._agents.size > 0
        self._transactions = Transactions(self._id, self._agents)
        self._orderbook = OrderBook(self._id, self._symbol, self._transactions)
        self._orderbook.events.partial_fill.subscribe(__class__._orderbook_event)
        self._orderbook.events.fill.subscribe(__class__._orderbook_event)
        self._orderbook.events.cancel.subscribe(__class__._orderbook_event)
        self._agents.start()
        self._orderbook.start()

    def stop(self):
        self._orderbook.stop()
        self._agents.stop()

    def clear(self):
        Order.active_buy_orders[self._id] = []
        Order.active_sell_orders[self._id] = []

    def add_agents(self, agents: List[Agent]):
        self._agents.add(agents)

    def show_transactions(self):
        logging.info(f"{__class__.__name__}.show_transactions entry")
        try:
            # assert self._transactions is not None
            # assert self._transactions.size > 0
            # assert self._orderbook.transactions.size > 0
            self._reports.show_transactions(self._orderbook.transactions)
        except Exception as e:
            logging.error(f"{__class__.__name__}.show_transactions e: {e}")
        logging.info(f"{__class__.__name__}.show_transactions exit")

    def show_orderbook(self, depth: int = 10):
        logging.info(f"{__class__.__name__}.show_orderbook entry")
        try:
            self._reports.show_orderbook(self._orderbook, depth)
        except Exception as e:
            logging.error(f"{__class__.__name__}.show_orderbook e: {e}")
        logging.info(f"{__class__.__name__}.show_orderbook exit")

    def get_last_price(self):
        retval = None
        if len(self._transactions.history) > 0:
            retval = self._transactions.history[-1].price
        else:
            retval = self._max_price - self._min_price / 2.0
        return retval

    def get_buy_price(self) -> float:
        retval = 0.0
        orders = self._orderbook.buy_orders()
        if len(orders) > 0:
            retval = orders[0].price
        return retval

    def get_sell_price(self) -> float:
        retval = 0.0
        orders = self._orderbook.sell_orders()
        if len(orders) > 0:
            retval = orders[0].price
        return retval

    def get_spread(self) -> float:
        retval = 0.0
        sell_price = self.get_sell_price()
        buy_price = self.get_buy_price()
        if sell_price > 0 and buy_price > 0.0:
            retval = sell_price - buy_price
        return retval

    def get_mid_price(self) -> float:
        retval = None
        sell_price = self.get_sell_price()
        buy_price = self.get_buy_price()
        if sell_price > 0.0 and buy_price > 0.0:
            retval = (sell_price + buy_price) / 2.0
        elif sell_price > 0.0 and buy_price <= 0.0:
            retval = sell_price
        elif sell_price <= 0.0 and buy_price > 0.0:
            retval = buy_price
        return retval
