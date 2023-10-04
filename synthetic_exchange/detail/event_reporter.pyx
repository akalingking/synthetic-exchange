import logging
import dataclasses
from typing import Optional
from .event_listener cimport EventListener


cdef class EventReporter(EventListener):
	def __init__(self, event_source: Optional[str] = None):
		EventListener.__init__(self)
		self.event_source = event_source

	cdef c_call(self, object event_object):
		try:
			if dataclasses.is_dataclass(event_object):
				event_dict = dataclasses.asdict(event_object)
			else:
				event_dict = event_object._asdict()
			event_dict.update({
				"event_name": event_object.__class__.__name__,
				"event_source": self.event_source
			})
			logging.debug("EventReporter event: {}".format(event_dict))
		except Exception as e:
			logging.error("EventReporte e: {}".format(e))
