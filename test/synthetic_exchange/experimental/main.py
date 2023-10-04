import logging
import unittest as ut
from test.synthetic_exchange.experimental.test_orderbook import OrderBookTest
from test.synthetic_exchange.experimental.test_orderbook_message import OrderBookMessageTest
from test.synthetic_exchange.experimental.test_limit_order import LimitOrderTest
from test.synthetic_exchange.experimental.test_in_flight_order import InFlightOrderTest
from test.synthetic_exchange.experimental.test_trade_fee import TradeFeeTest
from test.synthetic_exchange.experimental.test_event import EventTest
from test.synthetic_exchange.experimental.test_backtest_exchange import BacktestExchangeTest

import matplotlib.pyplot as plt


def main():
    loader = ut.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in [
			OrderBookTest,
			OrderBookMessageTest,
			LimitOrderTest,
			InFlightOrderTest,
			TradeFeeTest,
			EventTest,
			BacktestExchangeTest
        ]
    ]
    suite = ut.TestSuite(tests)
    runner = ut.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    plt.set_loglevel("info")
    logging.basicConfig(level=logging.DEBUG)
    main()
