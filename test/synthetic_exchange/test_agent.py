import logging
import multiprocessing as mp
import time
import unittest

from synthetic_exchange.strategy.random_normal import RandomNormal
from synthetic_exchange.strategy.random_uniform import RandomUniform


class AgentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wait = 10 * 3
        symbols = ["SMBL0", "SMBL1"]
        cls._queue = mp.Queue(maxsize=100)
        agent_1 = RandomUniform(
            marketId=0,
            symbol=symbols[0],
            minPrice=100,
            maxPrice=130,
            tickSize=1,
            minQuantity=100,
            maxQuantity=200,
            queue=cls._queue,
            wait=5,
        )
        agent_2 = RandomNormal(
            marketId=1, symbol=symbols[1], initialPrice=100, minQuantity=100, maxQuantity=200, queue=cls._queue, wait=5
        )
        cls._agents = [
            agent_1,
            agent_2,
        ]

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

    def test_agent(self):
        logging.info(f"---{__class__.__name__}.test_add_agent")

        for agent in self._agents:
            agent.start()

        time.sleep(self._wait)

        for agent in self._agents:
            agent.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
