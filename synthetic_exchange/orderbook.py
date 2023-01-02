import logging
import multiprocessing as mp

from synthetic_exchange.order import Order


class OrderBook:
    def __init__(self, marketId: int, symbol: str):
        self._market_id = marketId
        self._symbol = symbol
        self._history = []
        self._active_orders = []
        self._active_buy_orders = []
        self._active_sell_orders = []
        self._history_initial_orders = {}
        self._queue = mp.Queue()
        self._stop = mp.Event()
        self._lock = mp.Lock()
        self._condition = mp.Condition(self._lock)
        self._process = None
        logging.info(f"{__class__.__name__} created")

    @property
    def symbol(self):
        return self._symbol

    @property
    def market_id(self):
        return self._market_id

    def start(self):
        self._process = mp.Process(target=self._do_work, args=())
        self._process.start()

    def wait(self):
        if self._process is not None and self._stop.is_set():
            self._process.join()

    def stop(self):
        self._condition.acquire()
        self._stop.set()
        self._condition.notify()
        self._condition.release()

    def process(self, order: Order):
        self._lock.acquire()
        self._queue.put_nowait(order)
        self._condition.notify()
        self._lock.release()

    def _do_work(self):
        logging.info(f"{__class__.__name__}._do_work start")
        while True:
            self._condition.acquire()
            while self._queue.empty() and not self._stop.is_set():
                logging.info(f"{__class__.__name__}._do_work wait for orders..")
                self._condition.wait(timeout=10)
            if self._stop.is_set():
                self._condition.release()
                break
            order: Order = self._queue.get()
            self._condition.release()
            if order is not None:
                print(f"{__class__.__name__}.do_work {order}")
                self._history_initial_orders[order.id] = {
                    "id": order.id,
                    "market": self._market_id,
                    "side": order.side,
                    "price": order.price,
                    "quantity": order.quantity,
                }
                if order.side.lower() == "buy":
                    self._process_buy(order)
                elif order.side.lower() == "sell":
                    self._process_sell(order)
                else:
                    logging.error(f"{__class__.__name__}._do_work invalid order side: {order.side}")
        logging.info(f"{__class__.__name__}._do_work stopped")

    def _process_sell(self, order: Order):
        logging.info(f"{__class__.__name__}._process_sell {order}")

    def _process_buy(self, order: Order):
        logging.info(f"{__class__.__name__}._process_buy {order}")
