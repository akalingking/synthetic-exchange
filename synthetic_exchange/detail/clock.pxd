# distutils: language=c++
from .pubsub cimport PubSub

cpdef enum ClockMode:
	Realtime = 1
	Backtest = 2


cdef class Clock:
	cdef:
		ClockMode _clock_mode
		double _tick_size
		double _start_time
		double _current_tick
		double _end_time
		list _child_iterators
		list _current_context
		bint _started

	cdef c_backtest_til(self, double timestamp)


cdef class TimeIterator(PubSub):
	cdef:
		double _current_timestamp
		Clock _clock

	cdef c_start(self, Clock clock, double timestamp)
	cdef c_stop(self, Clock clock)
	cdef c_tick(self, double timestamp)
