import logging
import unittest as ut
import matplotlib.pyplot as plt
from test.synthetic_exchange.test_agent import AgentTest
from test.synthetic_exchange.test_exchange import ExchangeTest
from test.synthetic_exchange.test_exchanges import ExchangesTest
from test.synthetic_exchange.test_market import MarketTest
from test.synthetic_exchange.test_markets import MarketsTest
from test.synthetic_exchange.test_transactions import TransactionsTest


def main():
    loader = ut.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in [
            AgentTest,
            MarketTest,
            MarketsTest,
            TransactionsTest,
            ExchangeTest,
            ExchangesTest,
        ]
    ]
    suite = ut.TestSuite(tests)
    runner = ut.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    plt.set_loglevel("info")
    main()
