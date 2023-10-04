# distutils: language=c++
from collections import namedtuple


cpdef enum ExchangeType:
	ExchangeType_Binance = 1


cpdef enum AssetType:
	AssetType_Spot = 1
	AssetType_Perpetual = 2


cdef class Instrument:
	cdef public:
		str exchange
		str trading_pair
		AssetType asset_type
		double taker_fee
		double limit_fee
		double price_mult
		double size_mult


cpdef enum Side:
	Buy = 1
	Sell = -1

cpdef Side side_from_str(str side)


cpdef enum OrderType:
	Limit = 100
	LimitMarket = 200
	StopLimit = 300
	Market = 400


cpdef enum EventType:
	EventType_Snapshot = 100
	EventType_Diff = 101
	EventType_AggTrade = 102
	EventType_Trade = 103
	EventType_BBO = 104
	EventType_DepthUpdate = 105
	EventType_FundingInfo = 107
	EventType_Pending = 200
	EventType_Quote = 201
	EventType_Open = 202
	EventType_ReceivedAsset = 203
	EventType_BuyOrderCompleted = 104
	EventType_OrderOpen = 205
	EventType_OrderFill = 206
	EventType_OrderPartialFill = 207
	EventType_OrderCancel = 208
	EventType_OrderExpire = 209
	EventType_OrderUpdate = 210
	EventType_Custom = 999


cpdef enum LimitOrderStatus:
	LimitOrderStatus_Unknown = 0
	LimitOrderStatus_New = 1
	LimitOrderStatus_Open = 2
	LimitOrderStatus_Canceling = 3
	LimitOrderStatus_Canceled = 4
	LimitOrderStatus_Completed = 5
	LimitOrderStatus_Failed = 6


cpdef enum PriceType:
	PriceType_MidPrice = 1
	PriceType_BestBid = 2
	PriceType_BestAsk = 3
	PriceType_LastTrade = 4
	PriceType_Custom = 5
