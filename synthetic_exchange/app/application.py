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
        while True:
            with self._stop:
                if not self._stop.wait(self._wait):
                    continue  # timeout
                else:
                    break  # signalled

    def terminate(self):
        logging.debug(f"{self.__class__.__name__}.terminate entry")
        try:
            self._cond.acquire()
            self._run.value = 0
            self._cond.notify_all()
            self._cond.release()
        except Exception as e:
            logging.error(f"{self.__class__.__name__}.terminate e: {e}")
        logging.debug(f"{self.__class__.__name__}.terminate exit")

    def run(self):
        logging.debug(f"{__class__.__name__}.run start...")
        while True:
            try:
                self._lock.acquire()
                if self._run.value:
                    self._lock.release()
                    try:
                        self._do_work()
                    except Exception as e:
                        logging.error(f"{self.__class__.__name__}.run while doing work e: {e}")

                    with self._lock:
                        logging.debug(f"{self.__class__.__name__}.run wait for {self._wait} seconds...")
                        if not self._cond.wait(self._wait):
                            continue
                        else:
                            logging.warning(f"{self.__class__.__name__}.run wait interrupt run: {self._run}")
                else:
                    self._lock.release()
                    break

                with self._lock:
                    if not self._run.value:
                        break
            except KeyboardInterrupt:
                os._exit()
            except Exception as e:
                logging.error(f"{__class__.__name__}.run exception: {e}")

        with self._stop_lock:
            self._stop_cond.notify_all()

        logging.debug(f"{__class__.__name__}.run stopped!")

    def _do_work(self):
        raise NotImplementedError()
