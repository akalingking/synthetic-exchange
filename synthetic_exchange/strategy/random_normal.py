import datetime as dt
import logging
import random

import numpy as np

from synthetic_exchange.order import Order
from synthetic_exchange.strategy.agent import Agent


class RandomNormal(Agent):
    def __init__(self, *args, **kwargs):
        Agent.__init__(self, *args, **kwargs)
        logging.info(f"{__class__.__name__}.__init__")
        self._market_id = kwargs.get("marketId")
        self._last_price = kwargs.get("initialPrice")
        self._min_quantity = kwargs.get("minQuantity")
        self._max_quantity = kwargs.get("maxQuantity")
        if "handler" in kwargs:
            self._order_event.subscribe(kwargs.get("handler"))

    def _do_work(self):
        try:
            side = random.choice(["BUY", "SELL"])
            std = 0.1 * self._last_price
            price = np.random.normal(self._last_price, std)
            self._last_price = price
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

        event_type: str = event["event"].lower()
        if event_type == "cancel":
            pass
        elif event_type == "fill":
            pass
        elif event_type == "partially_filled":
            pass
        else:
            logging.warning(f"{__class__.__name__}.orderbook_event unhandled event: {event_type}")
