import datetime as dt
import logging
import random

import numpy as np

from synthetic_exchange.strategy.strategy import Strategy


class RandomUniform(Strategy):
    def __init__(self, *args, **kwargs):
        Strategy.__init__(self)
        logging.info(f"{__class__.__name__}.__init__")
        self._name = "RandomUniform"
        self._symbol = kwargs.get("symbol")
        self._market_id = kwargs.get("marketId")
        self._min_price = kwargs.get("minPrice")
        self._max_price = kwargs.get("maxPrice")
        self._tick_size = kwargs.get("tickSize")
        self._min_quantity = kwargs.get("minQuantity")
        self._max_quantity = kwargs.get("maxQuantity")
        if "handler" in kwargs:
            self._order_event.subscribe(kwargs.get("handler"))

    def do_work(self):
        assert self._agent_id is not None
        side = random.choice(["BUY", "SELL"])
        prices = np.arange(self._min_price, self._max_price, self._tick_size)
        price = np.random.choice(prices)
        quantity = random.randint(self._min_quantity, self._max_quantity)
        # self._order_event.emit((self._market_id, self._symbol, side, price, quantity))
        order = {
            "marketId": self._market_id,
            "agentId": self._agent_id,
            "dateTime": dt.datetime.utcnow(),
            "symbol": self._symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
        }
        self._order_event.emit(order)

    def orderbook_event(self, event: dict):
        logging.info(f"\n>>>{__class__.__name__}.orderbook_event event: {event}")
