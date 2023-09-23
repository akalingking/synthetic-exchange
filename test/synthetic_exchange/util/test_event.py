import datetime as dt
import itertools
import logging
import multiprocessing as mp
import os
import random
import time
import unittest

from synthetic_exchange.util import Event, ProcessEvent, Application


class Subject(Application):
    def __init__(self):
        self._event = ProcessEvent()
        Application.__init__(self, wait=5)

    def _do_work(self):
        logging.debug(f"{__class__.__name__}._do_work pid: {os.getpid()}")
        side = random.choice(["BUY", "SELL"])
        self._event.emit((dt.datetime.utcnow().timestamp(), side))


class Observer(Application):
    _last_id = itertools.count()
    _instance = {}

    def __init__(self):
        self._id = next(__class__._last_id)
        __class__._instance[self._id] = self
        Application.__init__(self, wait=5)

    def _do_work(self):
        logging.debug(f"{__class__.__name__}._do_work pid: {os.getpid()}")

    def on_event(self, event):
        logging.debug(f"{__class__.__name__}.on_event pid: {os.getpid()} {self._id} event: {event}")

    @staticmethod
    def _on_event(event):
        logging.debug(f"{__class__.__name__}._on_event pid: {os.getpid()} event: {event}")
        for _, instance in __class__._instance.items():
            instance.on_event(event)


class EventTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wait = 15

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def _order_event(event: dict):
        assert isinstance(event, dict)
        logging.info(f"---{__class__.__name__}._order_event event: {event}")
        assert event["state"].lower() == "open"  # Only open states

    def test_application(self):
        logging.info(f"---{__class__.__name__}.test_application")

        subject = Subject()
        observers = [Observer() for i in range(5)]
        subject._event.subscribe(Observer._on_event)
        for observer in observers:
            observer.start()
        subject.start()
        time.sleep(self._wait)
        subject.stop()
        for observer in observers:
            observer.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
