import unittest
import logging
import pandas as pd
import json
from synthetic_exchange.experimental.backtest_exchange import BacktestExchange
from synthetic_exchange.experimental.event import Event
from synthetic_exchange.experimental.events import Events
from synthetic_exchange.detail.clock import Clock, ClockMode
from synthetic_exchange.util.event_parser import Parser
from synthetic_exchange.experimental.dtype import Instrument, AssetType


class BacktestFromFileTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls._filename ="data/btcusdt_20230908.dat.gz"

	@classmethod
	def tearDownClass(cls):
		pass

	def test_events(self):
		# Generate events
		trading_pair = "btc-usdt"
		instrument = Instrument(**{
			"exchange": "binance",
			"tradingPair": trading_pair,
			"assetType": "perpetual",
			"takerFee": 0.00027,
			"limitFee": 0.00002,
			"priceMult": 10000,
			"sizeMult": 1000,
		})
		parser = Parser()

		rows: list = parser.parse(self._filename, instrument, verbose=False)
		self.assertTrue(len(rows) > 0)

		# Construct exchange events
		events = Events()
		events.add(rows, instrument=trading_pair, verbose=False)
		start = pd.Timestamp("2023-09-08-00:00:00", tz="UTC")
		end = pd.Timestamp("2023-09-09-00:00:00", tz="UTC")

		# Create backtest instance
		backtest = BacktestExchange(config={}, trading_pairs=[trading_pair], events=events)
		clock = Clock(ClockMode.Backtest, start_time=start.timestamp(), end_time=end.timestamp())
		clock.add_iterator(backtest)

		# Start backtest
		clock.backtest_til(end.timestamp())


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	unittest.main()
