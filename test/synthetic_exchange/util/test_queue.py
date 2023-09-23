import datetime as dt
import itertools
import logging
import multiprocessing as mp
import random
import time
import unittest

from synthetic_exchange.util import Application

_sides = ["BUY", "SELL"]


class Agent(Application):
    _id = itertools.count()

    def __init__(self, queue: mp.Queue):
        self._id = next(__class__._id)
        self._queue = queue
        Application.__init__(self, wait=5)

    def _do_work(self):
        ts = dt.datetime.now().timestamp()
        side = random.choice(_sides)
        data = (self._id, ts, side)
        print(f">>>>{__class__.__name__}._do_work data: {data}")
        self._queue.put_nowait(data)


class OrderBook(Application):
    def __init__(self, queue: mp.Queue):
        self._queue = queue
        Application.__init__(self, wait=5)

    def _do_work(self):
        print(f"{__class__.__name__}._do_work wait for data...")
        while not self._queue.empty():
            data = self._queue.get()
            print(f"<<<{__class__.__name__}._do_work data: {data}")


class QueueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 3
        cls._symbols = ["SMBL0", "SMBL1"]
        cls._queue = mp.Queue(maxsize=100)
        cls._agents = []
        for i in range(len(cls._symbols)):
            cls._agents.append(Agent(cls._queue))
        cls._ob = OrderBook(cls._queue)

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

    @unittest.skipIf(False, "")
    def test_orderbook(self):
        logging.info(f"---{__class__.__name__}.test_orderbook")
        # self._agent.start()
        for agent in self._agents:
            agent.start()
        self._ob.start()
        time.sleep(self._wait)
        self._ob.stop()
        for agent in self._agents:
            agent.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
