# distutils: language=c++
from synthetic_exchange.experimental.dtype cimport EventType, OrderType, Side


cdef class Event:
	cdef:
		public EventType type
		public long time
		public long now
		public str instrument
	cdef Event copy(self)


cdef class EventOrderFill(Event):
	cdef public:
		str order_id
		OrderType order_type
		double price
		double size
		double trade_fee
		str exchange_trade_id
		str exchange_order_id
		int leverage


cdef class EventTrade(Event):
	cdef public:
		Side side
		double price
		double size
		str trade_id


cdef class EventAggTrade(Event):
	cdef public:
		Side side
		double price
		double size
		long first_id
		long last_id


cdef class EventBBO(Event):
	cdef public:
		double bid_price
		double bid_size
		double ask_price
		double ask_size
		long update_id


cdef class EventSnapshot(Event):
	cdef public:
		list bids
		list asks
		long update_id


cdef class EventDiff(Event):
	cdef public:
		list bids
		list asks
		long update_id
		long prev_update_id

cdef class EventFundingInfo(Event):
	cdef public:
		double price
		double index_price
		double mark_price
		double next_funding_utc_timestamp
		double rate

