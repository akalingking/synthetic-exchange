#distutils: sources=["synthetic_exchange/experimental/LimitOrder.cpp"]

from synthetic_exchange.detail.clock cimport Clock, TimeIterator


cdef class BacktestExchange(TimeIterator):
	def __init__(
		self,
		dict config,
		list trading_pairs,
		list events
	):
		TimeIterator.__init__(self)
		self._config = config
		self._trading_pairs = trading_pairs
		self._in_flight_orders = {}
		self._account_balances = {}
		self._available_balances = {}
		self._trade_fee_schema = None

	def tick(self, timestamp: float):
		print(f"BacktestExchange.tick timestamp: {timestamp}")

	cdef c_tick(self, double timestamp):
		TimeIterator.c_tick(self, timestamp)
		self.tick(timestamp)

	cdef c_start(self, Clock clock, double timestamp):
		self.start(clock=clock, timestamp=timestamp)

	def start(self, clock, timestamp: float):
		TimeIterator.c_start(self, clock, timestamp)

	cdef c_stop(self, Clock clock):
		self.stop(clock=clock)

	def stop(self, clock):
		TimeIterator.c_stop(self, clock)
