import datetime as dt
import logging
import math
import multiprocessing as mp
import random
from abc import ABC, abstractmethod

import numpy as np

from synthetic_exchange import classproperty
from synthetic_exchange.agent import Agent
from synthetic_exchange.order import Order
from synthetic_exchange.utils.observer import Event


class Strategy(ABC):
    def __init__(self):
        self._order_event = Event()
        self._lock = mp.Lock()
        self._cond = mp.Condition(self._lock)
        self._process = None
        self._timeout = 3
        self._stop = mp.Event()

    @property
    def order_event(self):
        return self._order_event

    @property
    def name(self) -> str:
        return self._name

    def start(self):
        self._process = mp.Process(target=__class__._do_work, args=(self,))
        self._process.start()

    def wait(self):
        self._process.join()

    def stop(self):
        self._lock.acquire()
        self._stop.set()
        self._cond.notify()
        self._lock.release()
        self._process.join()

    def _do_work(self):
        logging.info(f"{self.__class__.__name__}.do_work start")
        while True:
            self._cond.acquire()
            self._cond.wait(timeout=self._timeout)
            if not self._stop.is_set():
                self._cond.release()
                self.do_work()
            else:
                self._cond.release()
                break
        logging.info(f"{self.__class__.__name__}.do_work stopped")

    @abstractmethod
    def do_work(self):
        raise NotImplementedError()


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
        side = random.choice(["BUY", "SELL"])
        prices = np.arange(self._min_price, self._max_price, self._tick_size)
        price = np.random.choice(prices)
        quantity = random.randint(self._min_quantity, self._max_quantity)
        # self._order_event.emit((self._market_id, self._symbol, side, price, quantity))
        order = {
            "marketId": self._market_id,
            "agentId": 0,
            "dateTime": dt.datetime.utcnow(),
            "symbol": self._symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
        }
        self._order_event.emit(order)


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

    def do_work(self):
        side = random.choice(["BUY", "SELL"])
        std = 0.1 * self._last_price
        price = np.random.normal(self._last_price, std)
        self._last_price = price
        quantity = random.randint(self._min_quantity, self._max_quantity)
        # self._order_event.emit((self._market_id, self._symbol, side, price, quantity))
        order = {
            "marketId": self._market_id,
            "agentId": 0,
            "dateTime": dt.datetime.utcnow(),
            "symbol": self._symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
        }
        self._order_event.emit(order)


def create_strategy(*args, **kwargs):
    retval = None
    name = kwargs.get("name")
    if name == "RandomUniform":
        retval = RandomUniform(*args, **kwargs)
    elif name == "RandomNormal":
        retval = RandomNormal(*args, **kwargs)
    else:
        logging.error(f"invalid strategy: {name}")
    return retval
