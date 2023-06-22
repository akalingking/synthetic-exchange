import datetime as dt
import logging
import multiprocessing as mp
import os
import signal
import threading


class Application(mp.Process):
    def __init__(self, *args, **kwargs):
        self._duration = None
        self._wait = kwargs.get("wait", 30)
        self._stop_time = None
        self._do_work_on_start = True
        self._run = True
        self._lock = threading.RLock()
        self._cond = threading.Condition(self._lock)
        self._stop_lock = threading.RLock()
        self._stop = threading.Condition(self._stop_lock)
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
        logging.info(f"{__class__.__name__}.terminate entry")
        try:
            self._cond.acquire()
            self._run = False
            self._cond.notify_all()
            self._cond.release()
        except Exception as e:
            logging.error(f"{__class__.__name__}.terminate e: {e}")
        logging.info(f"{__class__.__name__}.terminate exit")

    def run(self):
        start_time = dt.datetime.utcnow()

        if self._duration is not None and self._duration > 0:  # otherwise it runs forever
            self._stop_time = start_time + dt.timedelta(seconds=self._duration)

        logging.info(f"{__class__.__name__}.run START: {start_time} STOP: {self._stop_time}...")

        while True:
            try:
                self._lock.acquire()
                if self._run:
                    self._lock.release()
                    try:
                        self._do_work()
                    except Exception as e:
                        logging.error(f"{__class__.__name__}.run while doing work e: {e}")
                    """
                    self._lock.acquire()
                    logging.info(f"{__class__.__name__}.run wait for {self._wait} seconds...")
                    if not self._cond.wait(self._wait):
                        self._lock.release()
                        continue
                    else:
                        self._lock.release()
                        logging.warning(f"{__class__.__name__}.run wait interrupt")
                    """
                    with self._lock:
                        logging.info(f"{__class__.__name__}.run wait for {self._wait} seconds...")
                        if not self._cond.wait(self._wait):
                            continue
                        else:
                            logging.warning(f"{__class__.__name__}.run wait interrupt")
                else:
                    self._lock.release()

                # with self._lock:
                #    if not self._run:
                #        break
            except KeyboardInterrupt:
                os._exit()
            except Exception as e:
                logging.error(f"{__class__.__name__}.run exception: {e}")

        self._stop_cond.notify_all()

        if self._is_stop_time():
            self._run = False
            signal.raise_signal(signal.SIGINT)
            signal.raise_signal(signal.SIGTERM)
            os._exit(0)

        logging.info(f"{__class__.__name__}.run STOPPED!")

    def _do_work(self):
        raise NotImplementedError()
