# distutils: language=c++
from collections import namedtuple
from enum import Enum


ExchangeTypeToName = {
    ExchangeType.ExchangeType_Binance: "binance",
}

NameToExchangeType = {
    "binance": ExchangeType.ExchangeType_Binance,
}

NameToAssetType = {
    "spot": AssetType.AssetType_Spot,
    "perpetual": AssetType.AssetType_Perpetual,
}


cpdef Side side_from_str(str side):
	cdef:
		Side retval = Side.Buy
		str side_ = side.lower()
	if side_ == "buy":
		retval = Side.Buy
	elif side_ == "sell":
		retval = Side.Sell
	else:
		assert False
	return retval


cdef class Instrument:
	def __init__(self, **kwargs):
		print(kwargs)
		self.exchange = kwargs.get("exchange")
		self.trading_pair = kwargs.get("tradingPair")
		self.asset_type = NameToAssetType[kwargs.get("assetType").lower()]
		self.taker_fee = <float>kwargs.get("takerFee")
		self.limit_fee = <float>kwargs.get("limitFee")
		self.price_mult = <float>kwargs.get("priceMult")
		self.size_mult = <float>kwargs.get("sizeMult")


class OrderBookRow(namedtuple("_OrderBookRow", "price, amount, update_id")):
	price: float
	amount: float
	update_id: int


class PositionAction(Enum):
	PositionAction_Open = "OPEN"
	PositionAction_Close = "CLOSE"
	PositionAction_Nil = "NIL"
