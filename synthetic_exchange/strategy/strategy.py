import itertools
import logging
import multiprocessing as mp
from abc import ABC, abstractmethod

from synthetic_exchange.util import Event


class Strategy(ABC, mp.Process):
    _last_id = itertools.count()

    def __init__(self):
        self._order_event = Event()
        self._lock = mp.Lock()
        self._cond = mp.Condition(self._lock)
        self._timeout = 3
        self._stop = mp.Event()
        self._id = next(__class__._last_id)
        self._agent_id = None
        mp.Process.__init__(self)

    @property
    def order_event(self):
        return self._order_event

    @property
    def name(self) -> str:
        return self._name

    @property
    def agent_id(self) -> int:
        return self._agent_id

    @agent_id.setter
    def agent_id(self, value: int):
        self._agent_id = value

    def wait(self):
        mp.Process.join(self)

    def terminate(self):
        self._lock.acquire()
        self._stop.set()
        self._cond.notify()
        self._lock.release()
        mp.Process.terminate(self)

    def stop(self):
        self.terminate()

    def run(self):
        logging.debug(f"{self.__class__.__name__}.do_work agent id: {self._agent_id} name: {self._name} starting..")
        while True:
            self._cond.acquire()
            # logging.debug(f"{self.__class__.__name__}.do_work wait id: {self._agent_id} name: {self._name} wait {self._timeout} seconds..")
            self._cond.wait(timeout=self._timeout)
            if not self._stop.is_set():
                self._cond.release()
                self.do_work()
            else:
                self._cond.release()
                break
        logging.debug(f"{self.__class__.__name__}.do_work agent id: {self._agent_id} name: {self._name} stopped!")

    @abstractmethod
    def do_work(self):
        raise NotImplementedError()

    @abstractmethod
    def orderbook_event(self, event: dict):
        raise NotImplementedError()
