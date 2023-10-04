import datetime as dt
import itertools
import logging
import multiprocessing as mp
import random
import time
import unittest
from synthetic_exchange.util.event_parser import Parser
from synthetic_exchange.experimental.dtype import Instrument, AssetType


class ParserTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls._filename = "data/btcusdt_20230908.dat.gz"

	@classmethod
	def tearDownClass(cls):
		pass

	def setUp(self):
		pass

	def tearDown(self):
		pass


	def test_parser(self):
		logging.info(f"---{__class__.__name__}.test_parser")
		parser = Parser()
		instrument = Instrument(**{
			"exchange": "binance",
			"tradingPair": "btc-usdt",
			"assetType": "perpetual",
			"takerFee": 0.00027,
			"limitFee": 0.00002,
			"priceMult": 10000,
			"sizeMult": 1000,
		})
		events = parser.parse(self._filename, instrument, verbose=False)
		print(f"---events size: {len(events)}")
		self.assertTrue(len(events) > 0)
		self.assertEqual(len(events), 5108624)


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	unittest.main()
