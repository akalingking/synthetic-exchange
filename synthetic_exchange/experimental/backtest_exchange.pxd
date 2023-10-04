# distutils: language=c++
from libcpp.set cimport set as cpp_set
from libcpp.string cimport string
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair

from synthetic_exchange.detail.clock cimport TimeIterator
from synthetic_exchange.detail.event_reporter cimport EventReporter
from synthetic_exchange.experimental.event_logger cimport EventLogger
from synthetic_exchange.experimental.LimitOrder cimport LimitOrder as CPPLimitOrder
from synthetic_exchange.experimental.OrderExpirationEntry cimport OrderExpirationEntry as CPPOrderExpirationEntry
from synthetic_exchange.experimental.orbderbook_tracker import OrderBookTracker

ctypedef cpp_set[CPPLimitOrder] SingleTradingPairLimitOrders
ctypedef cpp_set[CPPLimitOrder].iterator SingleTradingPairLimitOrdersIterator
ctypedef cpp_set[CPPLimitOrder].reverse_iterator SingleTradingPairLimitOrdersRIterator
ctypedef pair[string, SingleTradingPairLimitOrders] LimitOrdersPair

ctypedef unordered_map[string, SingleTradingPairLimitOrders] LimitOrders
ctypedef unordered_map[string, SingleTradingPairLimitOrders].iterator LimitOrdersIterator
ctypedef cpp_set[CPPOrderExpirationEntry] LimitOrderExpirationSet
ctypedef cpp_set[CPPOrderExpirationEntry].iterator LimitOrderExpirationSetIterator


cdef class BacktestExchange(TimeIterator):
	cdef:
		EventReporter _event_reporter
		EventLogger _event_logger
		object _orderbook_tracker
		public dict _in_flight_orders
		public dict _account_balances
		public dict _available_balances
		public object _trade_fee_schema
		public dict _config
		public list _trading_pairs

		LimitOrders _bid_limit_orders
		LimitOrders _ask_limit_orders
		LimitOrderExpirationSet _limit_order_expiration_set
		object _queued_orders
		object _order_book_trade_listener
		object _market_order_filled_listener
		

	"""
	cdef str c_buy(self, str trading_pair, object amount, object order_type=*, object price=*, dict kwargs=*)
	cdef str c_sell(self, str trading_pair, object amount, object order_type=*, object price=*, dict kwargs=*)
	cdef c_cancel(self, str trading_pair, str client_order_id)
	cdef c_stop_tracking_order(self, str order_id)
	cdef c_get_balance(self, str currency)
	cdef c_get_available_balance(self, str currency)
	cdef c_get_price(self, str trading_pair, bint is_buy)
	cdef c_get_order_price_quantum(self, str trading_pair)
	cdef c_get_order_size_quantum(self, str trading_pair)

	cdef c_process_market_orders(self)
	cdef c_process_limit_orders(self)
	cdef c_process_limit_bid_orders(self)
	cdef c_process_limit_ask_orders(self)
	"""
	pass
