import logging
import unittest as ut
from test.test_agents import AgentsTest
from test.test_exchange import ExchangeTest
from test.test_market import MarketTest
from test.test_transactions import TransactionsTest

import matplotlib.pyplot as plt


def main():
    loader = ut.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in [
            AgentsTest,
            MarketTest,
            TransactionsTest,
            ExchangeTest,
        ]
    ]
    suite = ut.TestSuite(tests)
    runner = ut.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    plt.set_loglevel("info")
    main()
