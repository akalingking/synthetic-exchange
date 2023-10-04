import unittest
import logging
import pandas as pd
from synthetic_exchange.experimental.backtest_exchange import BacktestExchange
from synthetic_exchange.detail.clock import Clock, ClockMode


class BacktestExchangeTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		trading_pair = "SQNC-RSCH"
		trading_pairs = [trading_pair,]
		events = []
		cls._start = pd.Timestamp("2023-10-01-00:00:00", tz="UTC")
		cls._end = pd.Timestamp("2023-10-02-00:00:00", tz="UTC")
		cls._backtest = BacktestExchange(config={}, trading_pairs=trading_pairs, events=events)
		cls._clock = Clock(ClockMode.Backtest, start_time=cls._start.timestamp(), end_time=cls._end.timestamp())
		cls._clock.add_iterator(cls._backtest)

	@classmethod
	def tearDownClass(cls):
		pass

	def test_clock(self):
		self._clock.backtest_til(self._start.timestamp() + 1)

	def test_clock_end(self):
		self._clock.backtest_til(self._end.timestamp())


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	unittest.main()
