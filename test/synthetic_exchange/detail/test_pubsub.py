import unittest
import gc
import weakref
import logging
from enum import Enum
from typing import NamedTuple
from synthetic_exchange.detail.pubsub import PubSub
from synthetic_exchange.experimental.event_logger import EventLogger


class MockEventType(Enum):
	Event0 = 0
	Event1 = 1


class MockEvent(NamedTuple):
	payload: int


class PubSubTest(unittest.TestCase):
	def setUp(self):
		self.pubsub = PubSub()
		self.listener_0 = EventLogger()
		self.listener_1 = EventLogger()

		self.event_tag_0 = MockEventType.Event0
		self.event_tag_1 = MockEventType.Event1
		self.event = MockEvent(payload=1)

	def test_get_linteners_no_listeners(self):
		listeners_count = len(self.pubsub.get_listeners(self.event_tag_0))
		self.assertEqual(0, listeners_count)

	def test_add_listeners(self):
		self.pubsub.add_listener(self.event_tag_0, self.listener_0)
		listeners = self.pubsub.get_listeners(self.event_tag_0)
		self.assertEqual(1, len(listeners))
		self.assertIn(self.listener_0, listeners)

		self.pubsub.add_listener(self.event_tag_0, self.listener_1)
		listeners = self.pubsub.get_listeners(self.event_tag_0)
		self.assertEqual(2, len(listeners))
		self.assertIn(self.listener_0, listeners)
		self.assertIn(self.listener_1, listeners)

	def test_add_listener_twice(self):
		self.pubsub.add_listener(self.event_tag_0, self.listener_0)
		listeners_count = len(self.pubsub.get_listeners(self.event_tag_0))
		self.assertEqual(1, listeners_count)

		self.pubsub.add_listener(self.event_tag_0, self.listener_0)
		listeners_count = len(self.pubsub.get_listeners(self.event_tag_0))
		self.assertEqual(1, listeners_count)

	def test_remove_listener(self):
		self.pubsub.add_listener(self.event_tag_0, self.listener_0)
		self.pubsub.add_listener(self.event_tag_0, self.listener_1)

		self.pubsub.remove_listener(self.event_tag_0, self.listener_0)
		listeners = self.pubsub.get_listeners(self.event_tag_0)
		self.assertNotIn(self.listener_0, listeners)
		self.assertIn(self.listener_1, listeners)

	def test_add_listeners_to_separate_events(self):
		self.pubsub.add_listener(self.event_tag_0, self.listener_0)
		self.pubsub.add_listener(self.event_tag_1, self.listener_1)

		listeners_0 = self.pubsub.get_listeners(self.event_tag_0)
		listeners_1 = self.pubsub.get_listeners(self.event_tag_1)
		self.assertEqual(1, len(listeners_0))
		self.assertEqual(1, len(listeners_1))

	def test_trigger_event(self):
		self.pubsub.add_listener(self.event_tag_0, self.listener_0)
		self.pubsub.add_listener(self.event_tag_1, self.listener_1)

		self.pubsub.trigger_event(self.event_tag_0, self.event)
		self.assertEqual(1, len(self.listener_0.event_log))
		self.assertEqual(self.event, self.listener_0.event_log[0])
		self.assertEqual(0, len(self.listener_1.event_log))

	def test_lapsed_listener_remove_on_get_listeners(self):
		self.pubsub.add_listener(self.event_tag_0, self.listener_0)
		self.listener_0 = None	# remove strong reference
		gc.collect()
		listeners = self.pubsub.get_listeners(self.event_tag_0)
		self.assertEqual(0, len(listeners))

	def test_lapsed_listener_remove_on_remove_listener(self):
		self.pubsub.add_listener(self.event_tag_0, self.listener_0)
		self.pubsub.add_listener(self.event_tag_0, self.listener_1)
		listener_0_weakref = weakref.ref(self.listener_0)
		listener_1_weakref = weakref.ref(self.listener_1)
		self.listener_0 = None	# remove strong reference
		gc.collect()
		self.pubsub.remove_listener(self.event_tag_0, self.listener_1)
		self.assertEqual(None, listener_0_weakref())
		self.assertNotEqual(None, listener_1_weakref())
		listeners = self.pubsub.get_listeners(self.event_tag_0)
		self.assertEqual(0, len(listeners))


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	unittest.main()
	


