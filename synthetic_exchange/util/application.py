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
		logging.debug(f"{self.__class__.__name__}.wait entry")
		while True:
			if self._run.value == 1:
				with self._stop_lock:
					if not self._stop_cond.wait(self._wait):
						# logging.debug(f"{self.__class__.__name__}.wait timeout...")
						continue  # timeout
					else:
						# logging.debug(f"{self.__class__.__name__}.wait signalled...")
						break  # signalled
			else:
				break
		logging.debug(f"{self.__class__.__name__}.wait exit")
			
	def terminate(self):
		logging.debug(f"{self.__class__.__name__}.terminate entry")
		try:
			if self._run.value == 1:
				self._run.value = 0
				logging.debug(f"{self.__class__.__name__}.terminate run: {self._run.value}")
				with self._lock:
					self._cond.notify_all
		except Exception as e:
			logging.error(f"{self.__class__.__name__}.terminate e: {e}")
		logging.debug(f"{self.__class__.__name__}.terminate exit")

	def run(self):
		logging.debug(f"{__class__.__name__}.run start...")
		while True:
			try:
				if self._run.value == 1:
					try:
						self._do_work()
					except Exception as e:
						logging.error(f"{self.__class__.__name__}.run while doing work e: {e}")
					if self._run.value == 0:
						break
					else:
						self._lock.acquire()
						if not self._cond.wait(self._wait):
							# logging.debug(f"{self.__class__.__name__}.run wait timeout, run: {self._run.value} continue..")
							self._lock.release()
						else:
							# logging.debug(f"{self.__class__.__name__}.run wait interrupt run: {self._run.value}")
							self._lock.release()
							break
				else:
					logging.warning(f"{self.__class__.__name__}.run stopped")
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
