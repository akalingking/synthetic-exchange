import datetime as dt
import logging
import multiprocessing as mp
import os
import signal
import threading
from ctypes import c_int


class Application(mp.Process):
	def __init__(self, *args, **kwargs):
		self._duration = None
		self._wait = kwargs.get("wait", 30)
		self._run = mp.Value(c_int, 1)
		self._lock = mp.RLock()
		self._cond = mp.Condition(self._lock)
		self._stop_lock = mp.RLock()
		self._stop_cond = mp.Condition(self._stop_lock)
		mp.Process.__init__(self)

	def stop(self):
		self.terminate()

	def wait(self):
		self._lock.acquire()
		if self._run.value == 1:
			self._lock.release()
			while True:
				with self._stop_lock:
					if not self._stop_cond.wait(self._wait):
						continue  # timeout
					else:
						break  # signalled
		else:
			self._lock.release()
			

	def terminate(self):
		logging.debug(f"{self.__class__.__name__}.terminate entry")
		try:
			self._lock.acquire()
			if self._run.value == 1:
				self._run.value = 0
				# logging.debug(f"{self.__class__.__name__}.terminate run: {self._run.value}")
				self._cond.notify_all()
			self._lock.release()
		except Exception as e:
			logging.error(f"{self.__class__.__name__}.terminate e: {e}")
		logging.debug(f"{self.__class__.__name__}.terminate exit")

	def run(self):
		logging.debug(f"{__class__.__name__}.run start...")
		while True:
			try:
				self._lock.acquire()
				if self._run.value == 1:
					self._lock.release()
					try:
						self._do_work()
					except Exception as e:
						logging.error(f"{self.__class__.__name__}.run while doing work e: {e}")
					self._lock.acquire()
					if self._run.value == 0:
						self._lock.release()
						break
					else:
						if not self._cond.wait(self._wait):
							#logging.warning(f"{self.__class__.__name__}.run wait timeout, run: {self._run.value} continue..")
							self._lock.release()
						else:
							logging.warning(f"{self.__class__.__name__}.run wait interrupt run: {self._run.value}")
							self._lock.release()
							break
				else:
					logging.warning(f"{self.__class__.__name__}.run stopped")
					self._lock.release()
					break
			except KeyboardInterrupt:
				os._exit(1)
			except Exception as e:
				logging.error(f"{__class__.__name__}.run exception: {e}")

		with self._stop_lock:
			self._stop_cond.notify_all()

		logging.debug(f"{__class__.__name__}.run stopped!")

	def _do_work(self):
		raise NotImplementedError()
