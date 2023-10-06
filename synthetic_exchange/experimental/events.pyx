import datetime as dt
import pandas as pd
import logging
from synthetic_exchange.experimental.dtype import side_from_str, Side
from synthetic_exchange.util import bisect_left, bisect_right
from synthetic_exchange.experimental.event cimport (
	Event,
	EventTrade,
	EventAggTrade,
	EventBBO,
	EventSnapshot,
	EventDiff,
	EventFundingInfo,
)


cdef class Events:
	def __init__(self):
		self.events = []
		self._pos = 0

	cpdef void add(self, list data, str instrument, bint verbose=False) except *:
		cdef:
			list events = []
			int i, n
			dict row
			Event event
		n = len(data)
		for i in range(n):
			try:
				row = data[i]
				event = parse_event(row, instrument)
				if event is not None:
					events.append(event)
			except Exception as e:
				if verbose:
					logging.error("add exception: {} row: {}".format(e, row))
		self.events = sorted(events + self.events)

	cpdef void remove(self, str instrument) except *:
		self.events = [x for x in self.events if x.instrument != instrument]

	cpdef list get_events(self, list instruments=[]):
		cdef:
			events = []
		events = [
			x for x in self.events if (len(instruments) == 0 or x.instrument in instruments)
		]
		return events

	def __add__(self, rhs):
		events = []
		if isinstance(rhs, Events):
			events = sorted(self.events + rhs.events)
		elif isinstance(rhs, list):
			events = sorted(self.events + rhs)
		else:
			raise NotImplemented
		return events

	def __iter__(self):
		for event in self.events:
			yield event

	def __next__(self):
		if self._pos >= len(self.events):
			self._pos = 0
			raise StopIteration
		else:
			val = self.events[self._pos]
			self._pos += 1
			return val

	def __len__(self):
		return len(self.events)

	@staticmethod
	def _type_check(x) -> bool:
		return isinstance(x, (str, dt.datetime, dt.date, pd.Timestamp))

	def __getitem__(self, slice_):
		retval = None
		if isinstance(slice_, slice):
			start = slice_.start
			stop = slice_.stop
			step = slice_.step
			if isinstance(start, int) or isinstance(stop, int):
				events = Events()
				events.events = self.events[slice_]
				return events
			elif self._type_check(start) or self._type_check(stop):
				if self._type_check(start):
					start = pd.Timestamp(start)
				if self._type_check(stop):
					stop = pd.Timestamp(stop)
			else:
				raise ValueError('Incorrect slice')
			if isinstance(start, pd.Timestamp):
				start_pos = bisect_left(self.events, start, key=lambda x: pd.Timestamp(x.now))
			else:
				start_pos = None
			if isinstance(stop, pd.Timestamp):
				stop_pos = bisect_right(self.events, stop, key=lambda x: pd.Timestamp(x.now))
			else:
				stop_pos = None
			retval = self.events[slice(start_pos, stop_pos)]
		elif isinstance(slice_, int):
			retval = self.events[slice_]
		return retval


cpdef Event parse_event(dict data, str instrument):
	cdef:
		Event event = None
		str type = data.get("type", "").lower()

	if type == "trade":
		event = EventTrade(
			instrument=<str>instrument,
			price=<long>data["price"],
			size=<long>data["size"],
			id=<str>str(data["id"]),
			side=side_from_str(data["side"]),
			time=<long>data["time"],
			now=<long>data["now"]
		)

	elif type == "aggtrade":
		event = EventAggTrade(
			time=<long>(data["time"]),
			now=<long>(data["now"]),
			instrument=<str>(instrument),
			side=side_from_str(data["side"]),
			price=<long>data["price"],
			size=<long>data["size"],
			first_id=<long>(data["first_id"]),
			last_id=<long>(data["last_id"])
		)

	elif type == "bbo":
		event = EventBBO(
			instrument=<str>instrument,
			bid_price=<long>data["bid_price"],
			bid_size=<long>data["bid_size"],
			ask_price=<long>data["ask_price"],
			ask_size=<long>data["ask_size"],
			update_id=<long>data["update_id"],
			time=<long>data["time"],
			now=<long>data["now"]
		)

	elif type == "snapshot":
		event = EventSnapshot(
			time=<long>data["time"],
			now=<long>data["now"],
			instrument=<str>instrument,
			bids=<list>data["bids"],
			asks=<list>data["asks"],
			update_id=<long>data["update_id"]
		)

	elif type == "depthupdate" or type == "privatedepthupdate":
		event = EventDiff(
			time=<long>data["time"],
			now=<long>data["now"],
			instrument=<str>instrument,
			bids=<list>data["bids"],
			asks=<list>data["asks"],
			update_id=<long>data["update_id"],
			prev_update_id=<long>data["prev_update_id"]
		)

	elif type == "fundinginfo":
		event = EventFundingInfo(
			time=<long>data["time"],
			now=<long>data["now"],
			instrument=<str>instrument,
			index_price=<double>data["i"],
			mark_price=<double>data["p"],
			price=<double>data["P"],
			rate=<double>data["r"],
			next_funding_utc_timestamp=<long>data["T"]
		)

	else:
		logging.error(f"Event.parse_event invalid event: {data}")

	return event
