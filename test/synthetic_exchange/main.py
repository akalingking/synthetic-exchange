import logging
import unittest as ut
from test.synthetic_exchange.test_agent import AgentTest
from test.synthetic_exchange.test_exchange import ExchangeTest
from test.synthetic_exchange.test_exchange_cls import ExchangeClsTest
from test.synthetic_exchange.test_market import MarketTest
from test.synthetic_exchange.test_transactions import TransactionsTest

import matplotlib.pyplot as plt


def main():
    loader = ut.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in [
            AgentTest,
            MarketTest,
            TransactionsTest,
            ExchangeTest,
            ExchangeClsTest,
        ]
    ]
    suite = ut.TestSuite(tests)
    runner = ut.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    plt.set_loglevel("info")
    main()
