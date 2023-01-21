import enum
import logging
import multiprocessing as mp
import operator

from synthetic_exchange.order import Order
from synthetic_exchange.transaction import Transaction, Transactions
from synthetic_exchange.utils.observer import Event


class OrderEvent(enum.Enum):
    PartialFill = 0
    Fill = 1
    Cancel = 2


class OrderEvents:
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
    def __init__(self, marketId: int, symbol: str, transactions: Transactions = None):
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
        self._events = OrderEvents()
        self._transactions = transactions
        mp.Process.__init__(self)

    @property
    def symbol(self):
        return self._symbol

    @property
    def market_id(self):
        return self._market_id

    @property
    def transactions(self) -> Transactions:
        return self._transactions

    @property
    def active_buy_orders(self) -> list:
        return self._active_buy_orders

    @property
    def active_sell_orders(self) -> list:
        return self._active_sell_orders

    @property
    def events(self):
        return self._events

    def start(self):
        mp.Process.start(self)

    def wait(self):
        mp.Process.wait(self)

    def stop(self):
        self._condition.acquire()
        self._stop.set()
        self._condition.notify()
        self._condition.release()
        assert self._transactions.size > 0

    def process(self, order: Order):
        self._lock.acquire()
        self._queue.put_nowait(order)
        self._condition.notify()
        self._lock.release()

    def run(self):
        self._do_work()

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
                # print(f"{__class__.__name__}.do_work {order}")
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
                    logging.error(f"{__class__.__name__}._do_work invalid order side: {order.side}")
        logging.info(f"{__class__.__name__}._do_work stopped")

    def _process_buy(self, order: Order, transactions: Transactions):
        logging.info(f"{__class__.__name__}._process_buy {order} size: {transactions.size}")
        assert order.side.lower() == "buy"
        market_id = order.market_id
        remaining_quantity = order.quantity
        while True:
            if len(self._active_sell_orders) > 0:
                sell_orders = sorted(self._active_sell_orders, key=operator.attrgetter("price"))
                best_offer: Order = sell_orders[0]
                if order.price >= best_offer.price:
                    transaction_price = best_offer.price
                    if remaining_quantity > best_offer.quantity:
                        transaction_quantity = best_offer.quantity
                        # Transaction(order, best_offer, market_id, transaction_price, transaction_quantity)
                        _ = transactions.create(order, best_offer, market_id, transaction_price, transaction_quantity)
                        assert len(transactions.transactions) > 0
                        self._remove_offer(best_offer)
                        remaining_quantity -= transaction_quantity
                        logging.info(
                            f">>>{__class__.__name__}._process_buy order: {order.id} "
                            f"partial fill remaining quantity: {remaining_quantity}"
                        )
                        order.remaining = remaining_quantity
                        self._events.on_partial_fill(order)
                        # Find next best offer
                    elif remaining_quantity == best_offer.quantity:
                        transaction_quantity = best_offer.quantity
                        # Transaction(order, best_offer, market_id, transaction_price, transaction_quantity)
                        _ = transactions.create(order, best_offer, market_id, transaction_price, transaction_quantity)
                        assert len(transactions.transactions) > 0
                        self._remove_offer(best_offer)
                        logging.info(
                            f">>>{__class__.__name__}._process_buy order: {order.id} executed "
                            f"order quantity == offer quantity"
                        )
                        order.remaining = 0
                        self._events.on_fill(order)
                        break
                    else:
                        transaction_quantity = remaining_quantity
                        # Transaction(order, best_offer, market_id, transaction_price, transaction_quantity)
                        _ = transactions.create(order, best_offer, market_id, transaction_price, transaction_quantity)
                        assert len(transactions.transactions) > 0
                        self._reduce_offer(best_offer, transaction_quantity)
                        logging.info(
                            f">>>{__class__.__name__}._process_buy order: {order.id} executed "
                            f"order quantity < best offer quantity"
                        )
                        order.remaining = 0
                        self._events.on_fill(order)
                        break
                else:
                    logging.info(f"{__class__.__name__}._process_buy bid price < best offer, no transaction")
                    order.quantity = remaining_quantity
                    self._active_orders.append(order)
                    self._active_buy_orders.append(order)
                    break
            else:
                logging.info(f"{__class__.__name__}._process_buy no active sell orders, no transaction")
                order.quantity = remaining_quantity
                self._active_orders.append(order)
                self._active_buy_orders.append(order)
                break

    def _process_sell(self, order: Order, transactions: Transactions):
        logging.info(f"{__class__.__name__}._process_sell {order} tx size: {transactions.size}")
        assert order.side.lower() == "sell"
        assert order.market_id == self._market_id
        market_id = order.market_id
        remaining_quantity = order.quantity
        while True:
            if len(self._active_buy_orders) > 0:
                buy_orders = sorted(self._active_buy_orders, key=operator.attrgetter("price"))
                best_bid: Order = buy_orders[0]
                if order.price >= best_bid.price:
                    transaction_price = best_bid.price
                    if remaining_quantity > best_bid.quantity:
                        transaction_quantity = best_bid.quantity
                        _ = transactions.create(best_bid, order, market_id, transaction_price, transaction_quantity)
                        self._remove_bid(best_bid)
                        remaining_quantity -= transaction_quantity
                        logging.info(
                            f"{__class__.__name__}._process_sell order: {order.id} "
                            f"partial fill remaining quantity: {remaining_quantity}"
                        )
                        order.remaining = remaining_quantity
                        order.state = Order.State.PartialyFilled
                        self._events.on_partial_fill(order)
                        # Find next best offer
                    elif remaining_quantity == best_bid.quantity:
                        transaction_quantity = best_bid.quantity
                        _ = transactions.create(best_bid, order, market_id, transaction_price, transaction_quantity)
                        self._remove_bid(best_bid)
                        logging.info(
                            f"{__class__.__name__}._process_sell order: {order.id} executed "
                            f"order quantity == offer quantity"
                        )
                        order.remaining = 0
                        order.state = Order.State.Filled
                        self._events.on_fill(order)
                        break
                    else:
                        transaction_quantity = remaining_quantity
                        _ = transactions.create(best_bid, order, market_id, transaction_price, transaction_quantity)
                        self._reduce_bid(best_bid, transaction_quantity)
                        logging.info(
                            f"{__class__.__name__}._process_sell order: {order.id} executed "
                            f"order quantity < best bid quantity"
                        )
                        order.remaining = 0
                        order.state = Order.State.Filled
                        self._events.on_fill(order)
                        break
                else:
                    logging.info(f"{__class__.__name__}._process_sell offer price > best bid, no transaction")
                    order.quantity = remaining_quantity
                    self._active_orders.append(order)
                    self._active_sell_orders.append(order)
                    break
            else:
                logging.info(f"{__class__.__name__}._process_sell no active buy orders, no transaction")
                order.quantity = remaining_quantity
                self._active_orders.append(order)
                self._active_sell_orders.append(order)
                break

    def _remove_offer(self, offer: Order):
        for i, order in enumerate(self._active_sell_orders):
            if order.id == offer.id:
                logging.info(f"{__class__.__name__}._remove_offer order id: {offer.id}")
                del self._active_sell_orders[i]
                break

    def _reduce_offer(self, offer: Order, transactionQuantity: int):
        for i, order in enumerate(self._active_sell_orders):
            if order.id == offer.id:
                if self._active_sell_orders[i].quantity == transactionQuantity:
                    self._remove_offer(offer)
                else:
                    self._active_orders[i].quantity -= transactionQuantity
                break

    def _remove_bid(self, bid: Order):
        for i, order in enumerate(self._active_buy_orders):
            if order.id == bid.id:
                logging.info(f"{__class__.__name__}._remove_bid order id: {bid.id}")
                del self._active_buy_orders[i]
                break

    def _reduce_bid(self, bid: Order, transactionQuantity: int):
        for i, order in enumerate(self._active_buy_orders):
            if order.id == bid.id:
                if self._active_buy_orders[i].quantity == transactionQuantity:
                    self._remove_bid(bid)
                else:
                    self._active_orders[i].quantity -= transactionQuantity
                break
