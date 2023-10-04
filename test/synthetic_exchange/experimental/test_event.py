import unittest
import logging
from decimal import Decimal
from synthetic_exchange.experimental.dtype import EventType, Side, side_from_str
from synthetic_exchange.experimental.events import parse_event
from synthetic_exchange.experimental.event import (
	Event,
	EventTrade,
	EventAggTrade,
	EventBBO,
)


class EventTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.instrument = "btc-usdt"

	@classmethod
	def tearDownClass(cls):
		pass

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_event_trade(self):
		data = {
			"type": "Trade",
			"time": 1694147064971000000,
			"now": 1694147064801171000, 
			"side": "sell",
			"price": 262710000,
			"size": 1,
			"id": 4069726173
		}
		event = parse_event(data=data, instrument=self.instrument)
		self.assertTrue(isinstance(event, EventTrade))
		#print(f"---EventTest.test_event event: {event}")
		self.assertEqual(event.type, EventType.EventType_Trade)
		self.assertEqual(event.time, data["time"])
		self.assertEqual(event.now, data["now"])
		self.assertEqual(event.side, side_from_str(data["side"]))
		self.assertEqual(event.price, data["price"])
		self.assertEqual(event.size, data["size"])
		self.assertEqual(event.trade_id, str(data["id"]))

	def test_event_aggtrade(self):
		data = {
			"type": "AggTrade",
			"time": 1694147064971000000,
			"now": 1694147064801171000, 
			"side": "sell",
			"price": 262710000,
			"size": 1,
			"first_id": 4069726173,
			"last_id": 4069726190
		}
		event = parse_event(data=data, instrument=self.instrument)
		#print(f"---EventTest.test_event_aggtrade event: {event}")
		self.assertTrue(isinstance(event, EventAggTrade))
		self.assertEqual(event.type, EventType.EventType_AggTrade)
		self.assertEqual(event.time, data["time"])
		self.assertEqual(event.now, data["now"])
		self.assertEqual(event.side, side_from_str(data["side"]))
		self.assertEqual(event.price, data["price"])
		self.assertEqual(event.size, data["size"])
		self.assertEqual(event.first_id, data["first_id"])
		self.assertEqual(event.last_id, data["last_id"])

	def test_event_bbo(self):
		data = {
			'time': 1694144039780000000,
			'time_e': 1694144039784000000,
			'now': 1694144039807484000,
			'type': 'bbo',
			'bid_price': 262299000,
			'bid_size': 10548,
			'ask_price': 262300000,
			'ask_size': 17159,
			'update_id': 3243904811130
		}
		event = parse_event(data=data, instrument=self.instrument)
		#print(f"---EventTest.test_event_bbo event: {event}")
		self.assertTrue(isinstance(event, EventBBO))
		self.assertEqual(event.type, EventType.EventType_BBO)
		self.assertEqual(event.time, data["time"])
		self.assertEqual(event.now, data["now"])
		self.assertEqual(event.update_id, data["update_id"])
		self.assertEqual(event.bid_price, data["bid_price"])
		self.assertEqual(event.bid_size, data["bid_size"])
		self.assertEqual(event.ask_price, data["ask_price"])
		self.assertEqual(event.ask_size, data["ask_size"])
		self.assertEqual(event.update_id, data["update_id"])

	def test_event_snapshot(self):
		data = {
			'time': 1694144435113000000,
			'time_e': 1694144435120000000,
			'now': 1694144435143925000,
			'type': 'snapshot',
			'bids': [
				[50000000, 7610], [131244000, 0], [249364000, 18], [258014000, 2328],
				[259020000, 589], [259864000, 1], [261964000, 884], [262130000, 158],
				[262149000, 72], [262164000, 4006],[262165000, 2746], [262357000, 5],
				[262363000, 3196], [262390000, 3645], [262430000, 1829], [262432000, 4255],
				[262435000, 84], [262450000, 1269], [262452000, 55], [262453000, 3456], [262488000, 3752]
			],
			'asks': [
				[262489000, 13678], [262500000, 4466], [262531000, 1236], [262532000, 7],
				[262534000, 2072], [262542000, 3216], [262543000, 2905], [262544000, 1469],
				[262545000, 200], [262881000, 1004], [262882000, 763], [262884000, 2055],
				[262885000, 1427], [262886000, 19], [262887000, 2]
			],
			'update_id': 3243915982523,
		}
		event = parse_event(data=data, instrument=self.instrument)
		#print(f"---EventTest.test_event_snapshot event: {event}")
		self.assertEqual(event.type, EventType.EventType_Snapshot)
		self.assertEqual(event.time, data["time"])
		self.assertEqual(event.now, data["now"])
		self.assertEqual(event.bids, data["bids"])
		self.assertEqual(event.asks, data["asks"])
		self.assertEqual(event.update_id, data["update_id"])

	def test_event_diff(self):
		data = {
			'time': 1694144435113000000,
			'time_e': 1694144435120000000,
			'now': 1694144435143925000,
			'type': 'depthUpdate',
			'bids': [
				[50000000, 7610], [131244000, 0], [249364000, 18], [258014000, 2328],
				[259020000, 589], [259864000, 1], [261964000, 884], [262130000, 158],
				[262149000, 72], [262164000, 4006],[262165000, 2746], [262357000, 5],
				[262363000, 3196], [262390000, 3645], [262430000, 1829], [262432000, 4255],
				[262435000, 84], [262450000, 1269], [262452000, 55], [262453000, 3456], [262488000, 3752]
			],
			'asks': [
				[262489000, 13678], [262500000, 4466], [262531000, 1236], [262532000, 7],
				[262534000, 2072], [262542000, 3216], [262543000, 2905], [262544000, 1469],
				[262545000, 200], [262881000, 1004], [262882000, 763], [262884000, 2055],
				[262885000, 1427], [262886000, 19], [262887000, 2]
			],
			'update_id': 3243915982523,
			'prev_update_id': 3243915981041
		}
		event = parse_event(data=data, instrument=self.instrument)
		#print(f"---EventTest.test_event_diff event: {event}")
		self.assertEqual(event.type, EventType.EventType_Diff)
		self.assertEqual(event.time, data["time"])
		self.assertEqual(event.now, data["now"])
		self.assertEqual(event.bids, data["bids"])
		self.assertEqual(event.asks, data["asks"])
		self.assertEqual(event.update_id, data["update_id"])
		self.assertEqual(event.prev_update_id, data["prev_update_id"])


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	unittest.main()
