import enum
import logging
import multiprocessing as mp
import operator

from synthetic_exchange.app import Application
from synthetic_exchange.order import Order
from synthetic_exchange.transaction import Transaction, Transactions
from synthetic_exchange.util import Event


class OrderEvent(enum.Enum):
    PartialFill = 0
    Fill = 1
    Cancel = 2


class OrderEvents:
    """todo: Send dict or order type, update position & strategy classes"""

    def __init__(self):
        self.partial_fill = Event()
        self.fill = Event()
        self.cancel = Event()

    def on_partial_fill(self, order: Order):
        data = {"event": "partial_fill"}
        data.update(order.__dict__)
        self.partial_fill.emit(data)

    def on_fill(self, order: Order):
        data = {"event": "fill"}
        data.update(order.__dict__)
        self.fill.emit(data)

    def on_cancel(self, order: Order):
        data = {"event": "cancel"}
        data.update(order.__dict__)
        self.cancel.emit(data)


class OrderBook(mp.Process):
    _fields = ["price", "remaining", "timestamp", "id", "agent_id"]
    _max_size = 100

    def __init__(self, *args, **kwargs):
        assert "marketId" in kwargs, f"{__class__.__name__} missing marketId"
        assert "symbol" in kwargs, f"{__class__.__name__} missing symbol"
        assert "queue" in kwargs, f"{__class__.__name__} missing queue"
        self._market_id = kwargs.get("marketId", None)
        self._symbol = kwargs.get("symbol", None)
        self._transactions = kwargs.get("transactions", None)
        self._wait = kwargs.get("wait", 30)
        self._queue = kwargs.get("queue", None)

        self._history = []
        self._active_orders = []
        self._active_buy_orders = mp.Manager().list()
        self._active_sell_orders = mp.Manager().list()
        self._history_initial_orders = {}

        self._lock = mp.RLock()
        self._stop = mp.Event()
        self._cond = mp.Condition(self._lock)
        self._events = OrderEvents()

        mp.Process.__init__(self)

    @property
    def symbol(self):
        return self._symbol

    @property
    def market_id(self):
        return self._market_id

    @property
    def transactions(self) -> dict:
        return self._transactions.transactions

    @property
    def active_buy_orders(self) -> list:
        return self._active_buy_orders

    @property
    def active_sell_orders(self) -> list:
        return self._active_sell_orders

    @property
    def events(self):
        return self._events

    def buy_orders(self, depth: int = -1) -> list:
        return sorted(self._active_buy_orders, key=operator.attrgetter("price"), reverse=False)[:depth]

    def sell_orders(self, depth: int = -1) -> list:
        return sorted(self._active_sell_orders, key=operator.attrgetter("price"), reverse=True)[:depth]

    def orderbook(self, depth: int = -1) -> dict:
        buys, sells = [], []
        buy_orders, sell_orders = self.buy_orders(depth), self.sell_orders(depth)
        if len(buy_orders) > 0:
            buys = [{k: v for (k, v) in item.__dict__.items() if k in __class__._fields} for item in buy_orders]
            for item in buys:
                item["quantity"] = item.pop("remaining")
                item["timestamp"] = item["timestamp"]

        if len(sell_orders) > 0:
            sells = [{k: v for (k, v) in item.__dict__.items() if k in __class__._fields} for item in sell_orders]
            for item in sells:
                item["quantity"] = item.pop("remaining")
                item["timestamp"] = item["timestamp"]

        retval = {"symbol": self._symbol, "bids": buys, "asks": sells}
        logging.info(f"{__class__.__name__}.orderbook buys: {len(buys)} sell: {len(sells)}")
        return retval

    def start(self):
        mp.Process.start(self)

    def wait(self):
        mp.Process.wait(self)

    def stop(self):
        with self._cond:
            self._stop.set()
        mp.Process.terminate(self)

    """
    def process(self, order: Order):
        try:
            with self._lock:
                self._queue.put_nowait(order)
                self._queue_cond.notify()
        except mp.queue.Full:
            logging.warning(f"{__class__.__name__}.process pid: {self.pid} queue is full size: {self._queue.qsize()}")
        except Exception as e:
            logging.error(f"{__class__.__name__}.process pid: {self.pid} e: {e}")
    """

    def run(self):
        self._do_work()

    """
    def _do_work(self):
        logging.debug(f"{__class__.__name__}._do_work start")

        while True:
            self._cond.acquire()
            while self._queue.empty() and not self._stop_event.is_set():
                logging.debug(f"{__class__.__name__}._do_work pid: {self.pid} wait for orders..")
                self._cond.wait(timeout=10)
            if self._stop_event.is_set():
                self._cond.release()
                break

            order: Order = self._queue.get()
            self._cond.release()

            if order is not None:
                logging.debug(f"{__class__.__name__}.do_work {type(order)}: {order}")
                if order.cancel:
                    self._process_cancel(order, self._transactions)
                else:
                    self._history_initial_orders[order.id] = {
                        "id": order.id,
                        "market": self._market_id,
                        "side": order.side,
                        "price": order.price,
                        "quantity": order.quantity,
                    }
                    if order.side.lower() == "buy":
                        self._process_buy(order, self._transactions)
                    elif order.side.lower() == "sell":
                        self._process_sell(order, self._transactions)
                    else:
                        logging.error(f"{__class__.__name__}._do_work pid: {self.pid} invalid order side: {order.side}")

        logging.debug(f"{__class__.__name__}._do_work stopped")
    """

    def _do_work(self):
        logging.debug(f"{__class__.__name__}._do_work start")

        while True:
            with self._cond:
                if self._stop.is_set():
                    break
            # order: Order = self._queue.get()
            kwargs = self._queue.get()
            order = None
            if kwargs is not None:
                order = Order(**kwargs)

            if order is not None:
                logging.debug(f"{__class__.__name__}.do_work {type(order)}: {order}")
                if order.cancel:
                    self._process_cancel(order, self._transactions)
                else:
                    self._history_initial_orders[order.id] = {
                        "id": order.id,
                        "market": self._market_id,
                        "side": order.side,
                        "price": order.price,
                        "quantity": order.quantity,
                    }
                    if order.side.lower() == "buy":
                        self._process_buy(order, self._transactions)
                    elif order.side.lower() == "sell":
                        self._process_sell(order, self._transactions)
                    else:
                        logging.error(f"{__class__.__name__}._do_work pid: {self.pid} invalid order side: {order.side}")

        logging.debug(f"{__class__.__name__}._do_work stopped")

    def _process_cancel(self, order: Order, transactions: Transactions):
        # logging.debug(f"{__class__.__name__}._process_cancel order: {order} size: {transactions.size} entry")
        logging.debug(f"{__class__.__name__}._process_cancel order: {order} entry")

        result = False
        if order.side.lower() == "buy":
            result = self._remove_bid(order)
        elif order.side.lower() == "sell":
            result = self._remove_offer(order)
        if result:
            self._events.on_cancel(order)
        else:
            logging.warning(f"{__class__.__name__}._process_cancel pid: {self.pid} fail order: {order}")

        # logging.debug(f"{__class__.__name__}._process_cancel order: {order} size: {transactions.size} exit")

    def _process_buy(self, order: Order, transactions: Transactions):
        # logging.debug(f"{__class__.__name__}._process_buy {order} size: {transactions.size} entry")
        logging.debug(f"{__class__.__name__}._process_buy {order} entry")

        assert isinstance(order, Order)
        assert order.side.lower() == "buy"
        market_id = order.market_id
        remaining_quantity = order.quantity
        while True:
            active_sell_orders = [item for item in self._active_sell_orders if item.agent_id != order.agent_id]
            if len(active_sell_orders) > 0:
                sell_orders = sorted(active_sell_orders, key=operator.attrgetter("price"))
                best_offer: Order = sell_orders[0]
                if order.price >= best_offer.price:
                    transaction_price = best_offer.price
                    if remaining_quantity > best_offer.quantity:
                        transaction_quantity = best_offer.quantity
                        # Transaction(order, best_offer, market_id, transaction_price, transaction_quantity)
                        if transactions is not None:
                            _ = transactions.create(
                                order, best_offer, market_id, transaction_price, transaction_quantity
                            )
                            assert len(transactions.transactions) > 0
                        self._remove_offer(best_offer)
                        remaining_quantity -= transaction_quantity
                        logging.info(
                            f"{__class__.__name__}._process_buy pid: {self.pid} order: {order.id} "
                            f"partial fill remaining quantity: {remaining_quantity}"
                        )
                        order.remaining = remaining_quantity
                        self._events.on_partial_fill(order)
                        # Find next best offer
                    elif remaining_quantity == best_offer.quantity:
                        transaction_quantity = best_offer.quantity
                        # Transaction(order, best_offer, market_id, transaction_price, transaction_quantity)
                        if transactions is not None:
                            _ = transactions.create(
                                order, best_offer, market_id, transaction_price, transaction_quantity
                            )
                            assert len(transactions.transactions) > 0
                        self._remove_offer(best_offer)
                        logging.info(
                            f"{__class__.__name__}._process_buy pid: {self.pid} order: {order.id} executed "
                            f"order quantity == offer quantity"
                        )
                        order.remaining = 0
                        self._events.on_fill(order)
                        break
                    else:
                        transaction_quantity = remaining_quantity
                        # Transaction(order, best_offer, market_id, transaction_price, transaction_quantity)
                        if transactions is not None:
                            _ = transactions.create(
                                order, best_offer, market_id, transaction_price, transaction_quantity
                            )
                            assert len(transactions.transactions) > 0
                        self._reduce_offer(best_offer, transaction_quantity)
                        logging.info(
                            f"{__class__.__name__}._process_buy pid: {self.pid} order: {order.id} executed "
                            f"order quantity < best offer quantity"
                        )
                        order.remaining = 0
                        self._events.on_fill(order)
                        break
                else:
                    logging.info(
                        f"{__class__.__name__}._process_buy pid: {self.pid} bid price < best offer, no transaction"
                    )
                    order.quantity = remaining_quantity
                    self._active_orders.append(order)
                    self._active_buy_orders.append(order)
                    break
            else:
                logging.info(f"{__class__.__name__}._process_buy pid: {self.pid} no active sell orders, no transaction")
                order.quantity = remaining_quantity
                self._active_orders.append(order)
                self._active_buy_orders.append(order)
                break

        logging.debug(f"{__class__.__name__}._process_buy active: {self._active_buy_orders} exit")

    def _process_sell(self, order: Order, transactions: Transactions):
        # logging.debug(f"{__class__.__name__}._process_sell {order} tx size: {transactions.size} entry")
        logging.debug(f"{__class__.__name__}._process_sell {order} entry")

        assert order.side.lower() == "sell"
        assert order.market_id == self._market_id
        market_id = order.market_id
        remaining_quantity = order.quantity
        while True:
            active_buy_orders = [item for item in self._active_buy_orders if item.agent_id != order.agent_id]
            if len(active_buy_orders) > 0:
                buy_orders = sorted(active_buy_orders, key=operator.attrgetter("price"))
                best_bid: Order = buy_orders[0]
                if order.price >= best_bid.price:
                    transaction_price = best_bid.price
                    if remaining_quantity > best_bid.quantity:
                        transaction_quantity = best_bid.quantity
                        if transactions is not None:
                            _ = transactions.create(best_bid, order, market_id, transaction_price, transaction_quantity)
                        self._remove_bid(best_bid)
                        remaining_quantity -= transaction_quantity
                        logging.info(
                            f"{__class__.__name__}._process_sell pid: {self.pid} order: {order.id} "
                            f"partial fill remaining quantity: {remaining_quantity}"
                        )
                        order.remaining = remaining_quantity
                        order.state = Order.State.PartialyFilled
                        self._events.on_partial_fill(order)
                        # Find next best offer
                    elif remaining_quantity == best_bid.quantity:
                        transaction_quantity = best_bid.quantity
                        if transactions is not None:
                            _ = transactions.create(best_bid, order, market_id, transaction_price, transaction_quantity)
                        self._remove_bid(best_bid)
                        logging.info(
                            f"{__class__.__name__}._process_sell pid: {self.pid} order: {order.id} executed "
                            f"order quantity == offer quantity"
                        )
                        order.remaining = 0
                        order.state = Order.State.Filled
                        self._events.on_fill(order)
                        break
                    else:
                        transaction_quantity = remaining_quantity
                        if transactions is not None:
                            _ = transactions.create(best_bid, order, market_id, transaction_price, transaction_quantity)
                        self._reduce_bid(best_bid, transaction_quantity)
                        logging.info(
                            f"{__class__.__name__}._process_sell pid: {self.pid} order: {order.id} executed "
                            f"order quantity < best bid quantity"
                        )
                        order.remaining = 0
                        order.state = Order.State.Filled
                        self._events.on_fill(order)
                        break
                else:
                    logging.info(
                        f"{__class__.__name__}._process_sell pid: {self.pid} offer price > best bid, no transaction"
                    )
                    order.quantity = remaining_quantity
                    self._active_orders.append(order)
                    self._active_sell_orders.append(order)
                    break
            else:
                logging.info(f"{__class__.__name__}._process_sell pid: {self.pid} no active buy orders, no transaction")
                order.quantity = remaining_quantity
                self._active_orders.append(order)
                self._active_sell_orders.append(order)
                break

        logging.debug(f"{__class__.__name__}._process_sell active: {self._active_sell_orders} exit")

    def _remove_offer(self, offer: Order) -> bool:
        retval = False
        for i, order in enumerate(self._active_sell_orders):
            if order.id == offer.id:
                logging.info(f"{__class__.__name__}._remove_offer pid: {self.pid} order id: {offer.id}")
                del self._active_sell_orders[i]
                retval = True
                break
        return retval

    def _reduce_offer(self, offer: Order, transactionQuantity: int):
        for i, order in enumerate(self._active_sell_orders):
            if order.id == offer.id:
                if self._active_sell_orders[i].quantity == transactionQuantity:
                    self._remove_offer(offer)
                else:
                    self._active_orders[i].quantity -= transactionQuantity
                break

    def _remove_bid(self, bid: Order) -> bool:
        retval = False
        for i, order in enumerate(self._active_buy_orders):
            if order.id == bid.id:
                logging.debug(f"{__class__.__name__}._remove_bid pid: {self.pid} order id: {bid.id}")
                del self._active_buy_orders[i]
                retval = True
                break
        return retval

    def _reduce_bid(self, bid: Order, transactionQuantity: int):
        for i, order in enumerate(self._active_buy_orders):
            if order.id == bid.id:
                if self._active_buy_orders[i].quantity == transactionQuantity:
                    self._remove_bid(bid)
                else:
                    self._active_orders[i].quantity -= transactionQuantity
                break
