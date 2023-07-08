import logging
import time
import unittest

from synthetic_exchange.app import Application


class TestApplication(Application):
    def __init__(self):
        Application.__init__(self, wait=5)

    def _do_work(self):
        logging.debug(f"{__class__.__name__}._do_work")


class ApplicationTest(unittest.TestCase):
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
        app = TestApplication()
        app.start()
        time.sleep(self._wait)
        app.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
