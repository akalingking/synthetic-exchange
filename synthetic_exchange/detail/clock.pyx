# distutils: language=c++

import logging
import time
import asyncio
from typing import List

NaN = float("nan")


cdef class Clock:
	def __init__(self, clock_mode: ClockMode, tick_size: float = 1.0, start_time: float=0.0, end_time: float=0.0):
		self._clock_mode = clock_mode
		self._tick_size = tick_size
		self._start_time = start_time
		self._end_time = end_time
		self._current_tick = start_time if clock_mode is ClockMode.Backtest else \
			(time.time() // tick_size) * tick_size
		self._child_iterators = []
		self._current_context = None
		self._started = False

	@property
	def clock_mode(self) -> ClockMode:
		return self._clock_mode

	@property
	def start_time(self) -> float:
		return self._start_time

	@property
	def tick_size(self) -> float:
		return self._tick_size

	@property
	def child_iterators(self) -> List[TimeIterator]:
		return self._child_iterators

	@property
	def current_timestamp(self) -> float:
		return self._current_tick

	def __enter__(self) -> Clock:
		if self._current_context is not None:
			raise EnvironmentError("Clock context is not re-entrant.")
		self._current_context = self._child_iterators.copy()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self._current_context is not None:
			for iterator in self._current_context:
				(<TimeIterator>iterator).c_stop(self)
		self._current_context = None
	
	def add_iterator(self, iterator: TimeIterator):
		if self._current_context is not None:
			self._current_context.append(iterator)
		if self._started:
			(<TimeIterator>iterator).c_start(self, self._current_tick)
		self._child_iterators.append(iterator)

	def remove_iterator(self, iterator: TimeIterator):
		if self._current_context is not None and iterator in self._current_context:
			(<TimeIterator>iterator).c_stop(self)
			self._current_context.remove(iterator)
		self._child_iterators.remove(iterator)

	cdef c_backtest_til(self, double timestamp):
		cdef TimeIterator child_iterator

		if not self._started:
			for ci in self._child_iterators:
				child_iterator = ci
				child_iterator.c_start(self, self._start_time)
			self._started = True

		try:
			while not (self._current_tick >= timestamp):
				self._current_tick += self._tick_size
				for ci in self._child_iterators:
					child_iterator = ci
					try:
						child_iterator.c_tick(self._current_tick)
					except StopIteration:
						raise
					except Exception as e:
						logging.error(f"Clock.c_backtest_til e: {e}")
		except StopIteration:
			return
		finally:
			for ci in self._child_iterators:
				child_iterator = ci
				child_iterator._clock = None

	def backtest_til(self, end_time: float=None):
		if end_time is not None:
			self.c_backtest_til(end_time)
		else:
			self.c_backtest_til(self._end_time)	

	async def run(self):
		await self.run_til(float("nan"))

	async def run_til(self, timestamp: float):
		cdef:
			TimeIterator child_iterator
			double now = time.time()
			double next_tick_time

		if self._current_context is None:
			raise EnvironmentError("run() and run_til() can only be used within the context of a `with...` statement.")

		self._current_tick = (now // self._tick_size) * self._tick_size
		if not self._started:
			for ci in self._current_context:
				child_iterator = ci
				child_iterator.c_start(self, self._current_tick)
			self._started = True

		try:
			while True:
				now = time.time()
				if now >= timestamp:
					return

				# Sleep until the next tick
				next_tick_time = ((now // self._tick_size) + 1) * self._tick_size
				await asyncio.sleep(next_tick_time - now)
				self._current_tick = next_tick_time

				# Run through all the child iterators.
				for ci in self._current_context:
					child_iterator = ci
					try:
						child_iterator.c_tick(self._current_tick)
					except StopIteration:
						logging.error("Clock.run_til stop iteration triggered in real time mode")
						return
					except Exception as e:
						logging.error(f"Clock.run_til e: {e}")
		finally:
			for ci in self._current_context:
				child_iterator = ci
				child_iterator._clock = None


cdef class TimeIterator(PubSub):
	def __init__(self):
		self._current_timestamp = NaN
		self._clock = None

	cdef c_start(self, Clock clock, double timestamp):
		self._clock = clock
		self._current_timestamp = timestamp

	cdef c_stop(self, Clock clock):
		self._current_timestamp = NaN
		self._clock = None

	cdef c_tick(self, double timestamp):
		self._current_timestamp = timestamp

	def tick(self, timestamp: float):
		self.c_tick(timestamp)

	@property
	def current_timestamp(self) -> float:
		return self._current_timestamp

	@property
	def clock(self) -> Optional[Clock]:
		return self._clock

	def start(self, clock: Clock):
		self.c_start(clock, clock.current_timestamp)

	def stop(self, clock: Clock):
		self.c_stop(clock)

	def _set_current_timestamp(self, timestamp: float):
		self._current_timestamp = timestamp
