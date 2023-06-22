import datetime as dt
import logging
import random

import numpy as np

from synthetic_exchange.order import Order
from synthetic_exchange.strategy.strategy import Strategy

# from synthetic_exchange.position import Position


class RandomNormal(Strategy):
    def __init__(self, *args, **kwargs):
        Strategy.__init__(self)
        logging.info(f"{__class__.__name__}.__init__")
        self._name = "RandomNormal"
        self._symbol = kwargs.get("symbol")
        self._market_id = kwargs.get("marketId")
        self._last_price = kwargs.get("initialPrice")
        self._min_quantity = kwargs.get("minQuantity")
        self._max_quantity = kwargs.get("maxQuantity")
        if "handler" in kwargs:
            self._order_event.subscribe(kwargs.get("handler"))
        self._inflight_orders = {}
        self._positions = {}

    def do_work(self):
        assert self._agent_id is not None
        side = random.choice(["BUY", "SELL"])
        std = 0.1 * self._last_price
        price = np.random.normal(self._last_price, std)
        self._last_price = price
        quantity = random.randint(self._min_quantity, self._max_quantity)
        # self._order_event.emit((self._market_id, self._symbol, side, price, quantity))
        kwargs = {
            "marketId": self._market_id,
            "agentId": self._agent_id,
            "dateTime": dt.datetime.utcnow(),
            "symbol": self._symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
        }
        order = Order(**kwargs)
        self._order_event.emit(order)
        self._inflight_orders[order.id] = order

    def orderbook_event(self, event: dict):
        logging.info(f">>>{__class__.__name__}.orderbook_event event: {event}")
        event_type: str = event["event"]
        if event_type == "cancel":
            pass
        elif event_type == "fill":
            pass
        elif event_type == "partially_filled":
            pass
        else:
            logging.error(f"{__class__.__name__}.orderbook_event unhandled event: {event_type}")
