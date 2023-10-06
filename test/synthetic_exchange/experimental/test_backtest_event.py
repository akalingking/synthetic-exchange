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


class BacktestEventTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		pass

	@classmethod
	def tearDownClass(cls):
		pass

	def test_events(self):
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
		rows = [
			{"time":1694176672082000000, "now": 1694176672108053000, "type": "bbo", "bid_price": 258950000, \
				"bid_size": 2096, "ask_price": 258951000, "ask_size":14810, "update_id": 3245205006940},
			{"time":1694176672082000000, "now": 1694176672108955000, "type": "Trade", "side": "buy", \
				"price": 258951000, "size": 534, "id":4071000477},
			{'time': 1694176672183000000, 'time_e': 1694176672188000000, 'now': 1694176672210051000, \
				'type': 'depthUpdate', 'bids': [[256361000, 3], [257759000, 46], [258562000, 274], \
				[258604000, 3278], [258812000, 336], [258889000, 511], [258917000, 36], [258946000, 2548], \
				[258950000, 3693]], 'asks': [[258951000, 13863], [258958000, 1], [258968000, 2146], \
				[258974000, 218], [258983000, 1567], [258993000, 1150], [259027000, 521], [259052000, 3757]], \
				'update_id': 3245205010244, 'prev_update_id': 3245205008638
			}
		]

		events = Events()
		events.add(rows, instrument=trading_pair, verbose=True)
		start = pd.Timestamp("2023-09-08-12:30:00", tz="UTC")
		end = pd.Timestamp("2023-09-08-13:00:10", tz="UTC")
		backtest = BacktestExchange(config={}, trading_pairs=[trading_pair], events=events)
		clock = Clock(ClockMode.Backtest, start_time=start.timestamp(), end_time=end.timestamp())
		clock.add_iterator(backtest)
		clock.backtest_til(end.timestamp())


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	unittest.main()
