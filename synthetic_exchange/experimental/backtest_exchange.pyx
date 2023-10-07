#distutils: sources=["synthetic_exchange/experimental/LimitOrder.cpp"]
import datetime as dt
from synthetic_exchange.detail.clock cimport Clock, TimeIterator
from synthetic_exchange.detail.event_listener cimport EventListener
from synthetic_exchange.experimental.event import Event

"""
cdef class OrderBookTradeListener(EventListner):
	cdef TimeIterator _owner
	def __init__(self, owner):
		EventListener.__init__(self)
		self._owner = owner
	cdef c_call(self, Event event):
		try:
			self._owner.on_trade_event(event)
		except Exception as e:
			logging.error("OrderBookTradeListener e: {}".format(str(e))
"""


cdef class BacktestExchange(TimeIterator):
	def __init__(
		self,
		dict config,
		list trading_pairs,
		Events events
	):
		TimeIterator.__init__(self)
		self._config = config
		self._trading_pairs = trading_pairs
		self._in_flight_orders = {}
		self._account_balances = {}
		self._available_balances = {}
		self._trade_fee_schema = None
		self._exchange_events = events
		self._event_pos = 0
		self._event_size = len(self._exchange_events)

		#self._orderbook_trade_listener = OrderBookTradeListene(self)
		#self.c_add_listener(EventType.EventType_Trade.value, self._orderbook_trade_listener)

	def tick(self, timestamp: float):
		pass

	cdef c_tick(self, double timestamp):
		TimeIterator.c_tick(self, timestamp)
		self.tick(timestamp)
		while self._event_pos < self._event_size:
			event = self._exchange_events[self._event_pos]
			if timestamp >= event.now/1e9:
				self._event_pos += 1
				self.c_process_event(timestamp, event)
			else:
				break

	cdef c_start(self, Clock clock, double timestamp):
		self._event_pos = 0
		self.start(clock=clock, timestamp=timestamp)

	def start(self, clock, timestamp: float):
		TimeIterator.c_start(self, clock, timestamp)

	cdef c_stop(self, Clock clock):
		self.stop(clock=clock)

	cdef c_process_event(self, double timestamp, Event event):
		self.process_event(timestamp, event)

	def process_event(self, timestamp, event):
		pass
		#if event.type = EventType.EventType_Trade:
		#	self.c_trigger_event(EventType.EventType_Trade.value, event)
		
