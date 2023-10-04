from enum import Enum
from synthetic_exchange.experimental.dtype cimport Side


cdef class Event:
	def __init__(self, **kwargs):
		self.time = kwargs.get("time")
		self.now = kwargs.get("now")
		self.type = kwargs.get("type", EventType.EventType_Custom)
		self.instrument = kwargs.get("instrument", None)

	cdef Event copy(self):
		cdef Event event = Event()
		event.time = self.time
		event.now = self.now
		event.type = self.type
		event.instrument = self.instrument
		return event

	def __gt__(self, other: Event):
		if self.now > other.now:
			return True
		if self.now < other.now:
			return False
		if self.now == other.now and self.type > other.type:
			return True
		if self.now == other.now and \
				self.type == EventType.EventType_Trade and \
				other.type == EventType.EventType_Trade:
			return self.row.id > other.row.id

	def __str__(self):
		return f"Event type: {self.type} instrument: {self.instrument} time: {self.time} now: {self.now}"


cdef class EventTrade(Event):
	def __init__(self, **kwargs):
		Event.__init__(self, **kwargs)
		self.type = EventType.EventType_Trade
		self.side = kwargs.get("side")
		self.price = kwargs.get("price")
		self.size = kwargs.get("size")
		trade_id = kwargs.get("id")
		if not isinstance(trade_id, str):
			self.trade_id = str(trade_id)
		else:
			self.trade_id = trade_id

	cdef Event copy(self):
		event = Event.copy(self)
		event.type = self.type
		event.side = self.side
		event.price = self.price
		event.size = self.size
		event.trade_id =self.trade_id
		return event

	def __str__(self):
		s = Event.__str__(self)
		s += f" side: {self.side} price: {self.price} size: {self.size} trade_id: {self.trade_id}"
		return s

cdef class EventAggTrade(Event):
	def __init__(self, **kwargs):
		Event.__init__(self, **kwargs)
		self.type = EventType.EventType_AggTrade
		self.side = kwargs.get("side")
		self.price = kwargs.get("price")
		self.size = kwargs.get("size")
		self.first_id = kwargs.get("first_id")
		self.last_id = kwargs.get("last_id")

	cdef Event copy(self):
		event = Event.copy(self)
		event.type = self.type
		event.side = self.side
		event.price = self.price
		event.size = self.size
		event.first_id =self.first_id
		event.last_id =self.last_id
		return event

	def __str__(self):
		s = Event.__str__(self)
		s += f" side: {self.side} price: {self.price} size: {self.size} first_id: {self.first_id} last id: {self.last_id}"
		return s


cdef class EventBBO(Event):
	def __init__(self, **kwargs):
		Event.__init__(self, **kwargs)
		self.type = EventType.EventType_BBO
		self.bid_price = kwargs.get("bid_price")
		self.bid_size = kwargs.get("bid_size")
		self.ask_price = kwargs.get("ask_price")
		self.ask_size = kwargs.get("ask_size")
		self.update_id = kwargs.get("update_id")

	cdef Event copy(self):
		event = Event.copy(self)
		event.type = self.type
		event.bid_price = self.bid_price
		event.bid_size= self.bid_size
		event.ask_price = self.ask_price
		event.ask_size = self.ask_size
		event.update_id = self.update_id
		return event

	def __str__(self):
		s = Event.__str__(self)
		s += f" bid price: {self.bid_price} bid size: {self.bid_size} ask price: {self.ask_price} "
		s += f"ask size: {self.ask_size} update id: {self.update_id}"
		return s


cdef class EventSnapshot(Event):
	def __init__(self, **kwargs):
		Event.__init__(self, **kwargs)
		self.type = EventType.EventType_Snapshot
		self.bids = kwargs.get("bids")
		self.asks = kwargs.get("asks")
		self.update_id = kwargs.get("update_id")

	cdef Event copy(self):
		event = Event.copy(self)
		event.bids= self.bids
		event.asks = self.asks
		event.update_id = self.update_id
		return event

	def __str__(self):
		s = Event.__str__(self)
		s += f" bids: {self.bids} asks: {self.asks} "
		s += f" update_id: {self.update_id}"


cdef class EventDiff(Event):
	def __init__(self, **kwargs):
		Event.__init__(self, **kwargs)
		self.type = EventType.EventType_Diff
		self.bids = kwargs.get("bids")
		self.asks = kwargs.get("asks")
		self.update_id = kwargs.get("update_id")
		self.prev_update_id = kwargs.get("prev_update_id")

	cdef Event copy(self):
		event = Event.copy(self)
		event.bids= self.bids
		event.asks = self.asks
		event.update_id = self.update_id
		event.prev_update_id = self.prev_update_id
		return event

	def __str__(self):
		s = Event.__str__(self)
		s += f" bids: {self.bids} asks: {self.asks} "
		s += f" update_id: {self.update_id} prev update id: {self.prev_update_id}"
		return s
