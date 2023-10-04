import unittest
import logging
from decimal import Decimal
from synthetic_exchange.experimental.dtype import Side as TradeType
from synthetic_exchange.experimental.dtype import PositionAction
from synthetic_exchange.experimental.in_flight_order import TradeUpdate
from synthetic_exchange.experimental.trade_fee import (
	AddedToCostTradeFee,
	DeductedFromReturnsTradeFee,
	TokenAmount,
	TradeFeeBase,
	TradeFeeSchema,
)


class TradeFeeTest(unittest.TestCase):
	_pct_fee_token = "SQNC"
	_token = "SQNCRSCH"
	_trading_pair = "SQNC-RSCH"

	def test_added_to_cost_spot_fee_created_for_buy_and_fee_not_deducted_from_return(self):
		schema = TradeFeeSchema(
			percent_fee_token=self._pct_fee_token,
			maker_percent_fee_decimal=Decimal("1"),
			taker_percent_fee_decimal=Decimal("1"),
			buy_percent_fee_deducted_from_returns=False,
		)

		fee = TradeFeeBase.new_spot_fee(
			fee_schema=schema,
			trade_type=TradeType.Buy,
			percent=Decimal("1.1"),
			percent_token=self._pct_fee_token,
			flat_fees=[TokenAmount(token=__class__._token, amount=Decimal("20"))]
		)

		self.assertEqual(AddedToCostTradeFee, type(fee))
		self.assertEqual(Decimal("1.1"), fee.percent)
		self.assertEqual(self._pct_fee_token, fee.percent_token)
		self.assertEqual([TokenAmount(token=self._token, amount=Decimal("20"))], fee.flat_fees)

	def test_deducted_from_return_spot_fee_created_for_buy_and_fee_deducted_from_return(self):
		schema = TradeFeeSchema(
			maker_percent_fee_decimal=Decimal("1"),
			taker_percent_fee_decimal=Decimal("1"),
			buy_percent_fee_deducted_from_returns=True,
		)

		fee = TradeFeeBase.new_spot_fee(
			fee_schema=schema,
			trade_type=TradeType.Buy,
			percent=Decimal("1.1"),
			percent_token=self._pct_fee_token,
			flat_fees=[TokenAmount(token=self._token, amount=Decimal("20"))]
		)

		self.assertEqual(DeductedFromReturnsTradeFee, type(fee))
		self.assertEqual(Decimal("1.1"), fee.percent)
		self.assertEqual(self._pct_fee_token, fee.percent_token)
		self.assertEqual([TokenAmount(token=self._token, amount=Decimal("20"))], fee.flat_fees)

	def test_deducted_from_return_spot_fee_created_for_sell(self):
		schema = TradeFeeSchema(
			percent_fee_token=self._pct_fee_token,
			maker_percent_fee_decimal=Decimal("1"),
			taker_percent_fee_decimal=Decimal("1"),
			buy_percent_fee_deducted_from_returns=False,
		)

		fee = TradeFeeBase.new_spot_fee(
			fee_schema=schema,
			trade_type=TradeType.Sell,
			percent=Decimal("1.1"),
			percent_token=self._pct_fee_token,
			flat_fees=[TokenAmount(token=self._token, amount=Decimal("20"))]
		)

		self.assertEqual(DeductedFromReturnsTradeFee, type(fee))
		self.assertEqual(Decimal("1.1"), fee.percent)
		self.assertEqual(self._pct_fee_token, fee.percent_token)
		self.assertEqual([TokenAmount(token=self._token, amount=Decimal("20"))], fee.flat_fees)

		schema.percent_fee_token = None
		schema.buy_percent_fee_deducted_from_returns = True

		fee = TradeFeeBase.new_spot_fee(
			fee_schema=schema,
			trade_type=TradeType.Sell,
			percent=Decimal("1.1"),
			percent_token=self._pct_fee_token,
			flat_fees=[TokenAmount(token=self._token, amount=Decimal("20"))]
		)

		self.assertEqual(DeductedFromReturnsTradeFee, type(fee))

	def test_added_to_cost_perpetual_fee_created_when_opening_positions(self):
		schema = TradeFeeSchema(
			maker_percent_fee_decimal=Decimal("1"),
			taker_percent_fee_decimal=Decimal("1"),
			buy_percent_fee_deducted_from_returns=False,
		)

		fee = TradeFeeBase.new_perpetual_fee(
			fee_schema=schema,
			position_action=PositionAction.PositionAction_Open,
			percent=Decimal("1.1"),
			percent_token=self._pct_fee_token,
			flat_fees=[TokenAmount(token=self._token, amount=Decimal("20"))]
		)

		self.assertEqual(AddedToCostTradeFee, type(fee))
		self.assertEqual(Decimal("1.1"), fee.percent)
		self.assertEqual(self._pct_fee_token, fee.percent_token)
		self.assertEqual([TokenAmount(token=self._token, amount=Decimal("20"))], fee.flat_fees)

		schema.percent_fee_token = self._pct_fee_token

		fee = TradeFeeBase.new_perpetual_fee(
			fee_schema=schema,
			position_action=PositionAction.PositionAction_Open,
			percent=Decimal("1.1"),
			percent_token=self._pct_fee_token,
			flat_fees=[TokenAmount(token=self._token, amount=Decimal("20"))]
		)

		self.assertEqual(AddedToCostTradeFee, type(fee))

	def test_added_to_cost_perpetual_fee_created_when_closing_position_but_schema_has_percent_fee_token(self):

		schema = TradeFeeSchema(
			percent_fee_token=self._pct_fee_token,
			maker_percent_fee_decimal=Decimal("1"),
			taker_percent_fee_decimal=Decimal("1"),
			buy_percent_fee_deducted_from_returns=False,
		)

		fee = TradeFeeBase.new_perpetual_fee(
			fee_schema=schema,
			position_action=PositionAction.PositionAction_Close,
			percent=Decimal("1.1"),
			percent_token=self._pct_fee_token,
			flat_fees=[TokenAmount(token=self._token, amount=Decimal("20"))]
		)

		self.assertEqual(AddedToCostTradeFee, type(fee))
		self.assertEqual(Decimal("1.1"), fee.percent)
		self.assertEqual(self._pct_fee_token, fee.percent_token)
		self.assertEqual([TokenAmount(token=self._token, amount=Decimal("20"))], fee.flat_fees)

	def test_deducted_from_returns_perpetual_fee_created_when_closing_position_and_no_percent_fee_token(self):
		schema = TradeFeeSchema(
			maker_percent_fee_decimal=Decimal("1"),
			taker_percent_fee_decimal=Decimal("1"),
			buy_percent_fee_deducted_from_returns=False,
		)

		fee = TradeFeeBase.new_perpetual_fee(
			fee_schema=schema,
			position_action=PositionAction.PositionAction_Close,
			percent=Decimal("1.1"),
			percent_token=self._pct_fee_token,
			flat_fees=[TokenAmount(token=self._token, amount=Decimal("20"))]
		)

		self.assertEqual(DeductedFromReturnsTradeFee, type(fee))
		self.assertEqual(Decimal("1.1"), fee.percent)
		self.assertEqual(self._pct_fee_token, fee.percent_token)
		self.assertEqual([TokenAmount(token=self._token, amount=Decimal("20"))], fee.flat_fees)

	def test_added_to_cost_json_serialization(self):
		token_amount = TokenAmount(token=self._token, amount=Decimal("20.6"))
		fee = AddedToCostTradeFee(
			percent=Decimal("0.5"),
			percent_token=self._token,
			flat_fees=[token_amount]
		)
		expected_json = {
			"fee_type": AddedToCostTradeFee.type_descriptor_for_json(),
			"percent": "0.5",
			"percent_token": self._token,
			"flat_fees": [token_amount.to_json()]
		}
		self.assertEqual(expected_json, fee.to_json())

	def test_added_to_cost_json_deserialization(self):
		token_amount = TokenAmount(token=self._token, amount=Decimal("20.6"))
		fee = AddedToCostTradeFee(
			percent=Decimal("0.5"),
			percent_token=self._token,
			flat_fees=[token_amount]
		)

		self.assertEqual(fee, TradeFeeBase.from_json(fee.to_json()))

	def test_deducted_from_returns_json_serialization(self):
		token_amount = TokenAmount(token=self._token, amount=Decimal("20.6"))
		fee = DeductedFromReturnsTradeFee(
			percent=Decimal("0.5"),
			percent_token=self._token,
			flat_fees=[token_amount]
		)
		expected_json = {
			"fee_type": DeductedFromReturnsTradeFee.type_descriptor_for_json(),
			"percent": "0.5",
			"percent_token": self._token,
			"flat_fees": [token_amount.to_json()]
		}
		self.assertEqual(expected_json, fee.to_json())

	def test_deducted_from_returns_json_deserialization(self):
		token_amount = TokenAmount(token=self._token, amount=Decimal("20.6"))
		fee = DeductedFromReturnsTradeFee(
			percent=Decimal("0.5"),
			percent_token=self._token,
			flat_fees=[token_amount]
		)
		self.assertEqual(fee, TradeFeeBase.from_json(fee.to_json()))

	def test_added_to_cost_fee_amount_in_token_does_not_look_for_convertion_rate_when_percentage_zero(self):
		# Configure fee to use a percent token different from the token used to request the fee value
		# That forces the logic to need the convertion rate if the fee amount is calculated
		fee = AddedToCostTradeFee(percent=Decimal("0"), percent_token=self._token)
		fee_amount = fee.fee_amount_in_token(
			trading_pair=self._trading_pair,
			price=Decimal("1000"),
			order_amount=Decimal("1"),
			token="BNB")
		self.assertEqual(Decimal("0"), fee_amount)

	def test_deducted_from_returns_fee_amount_in_token_does_not_look_for_convertion_rate_when_percentage_zero(self):
		# Configure fee to use a percent token different from the token used to request the fee value
		# That forces the logic to need the convertion rate if the fee amount is calculated
		fee = DeductedFromReturnsTradeFee(percent=Decimal("0"), percent_token=self._token)
		fee_amount = fee.fee_amount_in_token(
			trading_pair=self._trading_pair,
			price=Decimal("1000"),
			order_amount=Decimal("1"),
			token="BNB")
		self.assertEqual(Decimal("0"), fee_amount)


class TokenAmountTest(unittest.TestCase):
	_token = "SQNC-RSCH"
	def test_json_serialization(self):
		amount = TokenAmount(token=self._token, amount=Decimal("1000.50"))
		expected_json = {"token": self._token, "amount": "1000.50"}
		self.assertEqual(expected_json, amount.to_json())

	def test_json_deserialization(self):
		amount = TokenAmount(token=self._token, amount=Decimal("1000.50"))
		self.assertEqual(amount, TokenAmount.from_json(amount.to_json()))


class TradeUpdateTest(unittest.TestCase):
	_token = "SQNC"
	_trading_pair = "SQNC-RSCH"

	def test_json_serialization(self):
		token_amount = TokenAmount(token=self._token, amount=Decimal("20.6"))
		fee = DeductedFromReturnsTradeFee(
			percent=Decimal("0.5"),
			percent_token=self._token,
			flat_fees=[token_amount]
		)
		trade_update = TradeUpdate(
			trade_id="12345",
			client_order_id="OID1",
			exchange_order_id="EOID1",
			trading_pair="HBOT-COINALPHA",
			fill_timestamp=1640001112,
			fill_price=Decimal("1000.11"),
			fill_base_amount=Decimal("2"),
			fill_quote_amount=Decimal("2000.22"),
			fee=fee,
		)
		expected_json = trade_update._asdict()
		expected_json.update({
			"fill_price": "1000.11",
			"fill_base_amount": "2",
			"fill_quote_amount": "2000.22",
			"fee": fee.to_json(),
		})
		self.assertEqual(expected_json, trade_update.to_json())

	def test_json_deserialization(self):
		token_amount = TokenAmount(token=self._token, amount=Decimal("20.6"))
		fee = DeductedFromReturnsTradeFee(
			percent=Decimal("0.5"),
			percent_token=self._token,
			flat_fees=[token_amount]
		)
		trade_update = TradeUpdate(
			trade_id="12345",
			client_order_id="OID1",
			exchange_order_id="EOID1",
			trading_pair=self._trading_pair,
			fill_timestamp=1640001112,
			fill_price=Decimal("1000.11"),
			fill_base_amount=Decimal("2"),
			fill_quote_amount=Decimal("2000.22"),
			fee=fee,
		)
		self.assertEqual(trade_update, TradeUpdate.from_json(trade_update.to_json()))


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	unittest.main()
