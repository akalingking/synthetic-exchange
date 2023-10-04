import logging
import unittest as ut
from test.synthetic_exchange.detail.test_clock import ClockTest
from test.synthetic_exchange.detail.test_pubsub import PubSubTest
from test.synthetic_exchange.detail.test_time_iterator import TimeIteratorTest
import matplotlib.pyplot as plt


def main():
    loader = ut.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in [
            ClockTest,
            PubSubTest,
           	TimeIteratorTest,
        ]
    ]
    suite = ut.TestSuite(tests)
    runner = ut.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    plt.set_loglevel("info")
    logging.basicConfig(level=logging.DEBUG)
    main()
