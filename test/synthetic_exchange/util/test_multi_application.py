import datetime as dt
import logging
import multiprocessing as mp
import random
import time
import unittest

from synthetic_exchange.util import Application


class Producer(Application):
    def __init__(self, data):
        self._data = data
        Application.__init__(self, wait=5)

    def _do_work(self):
        logging.debug(f"{__class__.__name__}._do_work")
        side = random.choice(["BUY", "SELL"])
        # self._data[dt.datetime.utcnow().timestamp()] = side
        self._data.append((dt.datetime.utcnow().timestamp(), side))


class Consumer(Application):
    def __init__(self, data):
        self._data = data
        Application.__init__(self, wait=5)

    def _do_work(self):
        logging.debug(f"{__class__.__name__}._do_work data: {self._data}")


class MultiApplicationTest(unittest.TestCase):
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
        # data = mp.Manager().dict()
        data = mp.Manager().list()
        prod = Producer(data)
        cons = Consumer(data)
        prod.start()
        cons.start()
        time.sleep(self._wait)
        prod.stop()
        cons.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
