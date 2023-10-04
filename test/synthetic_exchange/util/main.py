import logging
import unittest as ut
import matplotlib.pyplot as plt
from test.synthetic_exchange.util.test_application import ApplicationTest
from test.synthetic_exchange.util.test_multi_application import MultiApplicationTest
from test.synthetic_exchange.util.test_event import EventTest
from test.synthetic_exchange.util.test_queue import QueueTest


def main():
    loader = ut.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in [
			EventTest,
			QueueTest,
			ApplicationTest,
			MultiApplicationTest,
        ]
    ]
    suite = ut.TestSuite(tests)
    runner = ut.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    plt.set_loglevel("info")
    main()
