# distutils: language=c++
from synthetic_exchange.experimental.event cimport Event


cdef class Events:
	cdef:
		public list events
		public int _counter
	cpdef void add(self, list data, str instrument, bint verbose=*,) except *
	cpdef void remove(self, str instrument) except *
	cpdef list get_events(self, list instruments=*)

cpdef Event parse_event(dict row, str instrument)
