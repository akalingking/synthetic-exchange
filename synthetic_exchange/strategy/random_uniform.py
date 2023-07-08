import datetime as dt
import logging
import random

import numpy as np

from synthetic_exchange.order import Order
from synthetic_exchange.strategy.agent import Agent


class RandomUniform(Agent):
    def __init__(self, *args, **kwargs):
        Agent.__init__(self, *args, **kwargs)
        assert self._queue is not None
        try:
            self._market_id = kwargs.get("marketId")
            self._min_price = kwargs.get("minPrice")
            self._max_price = kwargs.get("maxPrice")
            self._tick_size = kwargs.get("tickSize")
            self._min_quantity = kwargs.get("minQuantity")
            self._max_quantity = kwargs.get("maxQuantity")
        except Exception as e:
            logging.error(f"{__class__.__name__}.__init__ e: {e}")

    def _do_work(self):
        try:
            side = random.choice(["BUY", "SELL"])
            prices = np.arange(self._min_price, self._max_price, self._tick_size)
            price = np.random.choice(prices)
            quantity = random.uniform(self._min_quantity, self._max_quantity)
            kwargs = {
                "marketid": self._market_id,
                "agentid": self.id,
                "timestamp": dt.datetime.utcnow().timestamp() * 1000,
                "symbol": self._symbol,
                "side": side,
                "price": price,
                "quantity": quantity,
                "state": Order.State.Open.name,
            }
            logging.debug(f"{__class__.__name__}._do_work order: {kwargs}")
            self._queue.put_nowait(kwargs)
            order = Order(**kwargs)
            self._inflight_orders[order.id] = order
        except Exception as e:
            logging.error(f"{__class__.__name__}._do_work e: {e}")

    def orderbook_event(self, event: dict):
        logging.debug(f"{__class__.__name__}.orderbook_event event: {event}")
