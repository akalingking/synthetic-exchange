import unittest
import logging
from decimal import Decimal
import time
from synthetic_exchange.experimental.limit_order import LimitOrder
from synthetic_exchange.experimental.dtype import LimitOrderStatus


class LimitOrderTest(unittest.TestCase):
    _base_asset = "SQNC"
    _quote_asset = "USDT"
    _trading_pair = "".join([_base_asset, "-", _quote_asset])

    def test_order_creation_with_default_values(self):
        price = Decimal("100")
        quantity = Decimal("1.5")
        client_order_id = "COID_1"
        order = LimitOrder(
            client_order_id=client_order_id,
            trading_pair=__class__._trading_pair,
            is_buy=False,
            base_currency=__class__._base_asset,
            quote_currency=__class__._quote_asset,
            price=price,
            quantity=quantity
        )
        self.assertEqual(client_order_id, order.client_order_id)
        self.assertEqual(__class__._trading_pair, order.trading_pair)
        self.assertEqual(False, order.is_buy)
        self.assertEqual(__class__._base_asset, order.base_currency)
        self.assertEqual(__class__._quote_asset, order.quote_currency)
        self.assertEqual(price, order.price)
        self.assertEqual(quantity, order.quantity)
        self.assertTrue(Decimal.is_nan(order.filled_quantity))
        self.assertEqual(0, order.creation_timestamp)
        self.assertEqual(LimitOrderStatus.LimitOrderStatus_Unknown, order.status)
        self.assertEqual(-1, order.age())

    def test_order_creation_with_all_values(self):
        created = int((time.time() - 100.) * 1e6)
        client_order_id = "COID_1"
        price = Decimal("100")
        quantity = Decimal("1.5")
        filled_quantity = Decimal("0.5")
        order = LimitOrder(
            client_order_id=client_order_id,
            trading_pair=__class__._trading_pair,
            is_buy=False,
            base_currency=__class__._base_asset,
            quote_currency=__class__._quote_asset,
            price=price,
            quantity=quantity,
            filled_quantity=filled_quantity,
            creation_timestamp=created,
            status=LimitOrderStatus.LimitOrderStatus_Open
        )
        self.assertEqual(filled_quantity, order.filled_quantity)
        self.assertEqual(created, order.creation_timestamp)
        self.assertEqual(LimitOrderStatus.LimitOrderStatus_Open, order.status)
        self.assertEqual(100, order.age())
        end_time = created + int(50 * 1e6)
        self.assertEqual(50, order.age_til(end_time))
        end_time = created - int(50 * 1e6)
        self.assertEqual(-1, order.age_til(end_time))

    def test_to_pandas(self):
        # Fix the timestamp here so that we can test order age accurately
        created = 1625835199511442
        now_ts = created + 100 * 10**6
        self.maxDiff = None
        orders = [
            LimitOrder("COID_1", "A-B", True, "A", "B", Decimal("1"), Decimal("1.5")),
            LimitOrder(f"COID_{str(created)}", "C-D", True, "C", "D", Decimal("1"), Decimal("1")),
            LimitOrder("COID_2", "A-B ", False, "A", "B", Decimal("2.5"), Decimal("1"), Decimal("0"),\
                created, LimitOrderStatus.LimitOrderStatus_Open),
            LimitOrder(f"COID_{str(created)}", "A-B ", False, "A", "B", Decimal("2"), Decimal("1"),\
                Decimal(0), created, LimitOrderStatus.LimitOrderStatus_Canceled),
        ]
        df = LimitOrder.to_pandas(orders, 1.5, end_time_order_age=now_ts)
        # Except df output is as below

        # Order ID Type  Price Spread  Amount      Age Hang
        #   HBOT_2 sell    2.5 66.67%     1.0 00:01:40  n/a
        #  ...1442 sell    2.0 33.33%     1.0 00:01:40  n/a
        #   HBOT_1  buy    1.0 33.33%     1.5      n/a  n/a
        #  ...1442  buy    1.0 33.33%     1.0 00:01:40  n/a
        # we can't compare the text output directly as for some weird reason the test file passes when run individually
        # but will fail under coverage run -m nose test.hummingbot
        # self.assertEqual(expect_txt, df.to_string(index=False, max_colwidth=50))
        self.assertEqual("COID_2", df["Order ID"][0])
        self.assertEqual("sell", df["Type"][0])
        self.assertAlmostEqual(2.5, df["Price"][0])
        self.assertEqual("66.67%", df["Spread"][0])
        self.assertAlmostEqual(1., df["Amount"][0])
        self.assertEqual("00:01:40", df["Age"][0])
        self.assertEqual("n/a", df["Hang"][0])

        # Test to see if hanging orders are displayed correctly
        df = LimitOrder.to_pandas(orders, 1.5, ["COID_1", "COID_2"], end_time_order_age=now_ts)
        # Except df output is as below
        # Order ID Type  Price Spread  Amount      Age Hang
        #   HBOT_2 sell    2.5 66.67%     1.0 00:01:40  yes
        #  ...1442 sell    2.0 33.33%     1.0 00:01:40   no
        #   HBOT_1  buy    1.0 33.33%     1.5      n/a  yes
        #  ...1442  buy    1.0 33.33%     1.0 00:01:40   no

        self.assertEqual("COID_2", df["Order ID"][0])
        self.assertEqual("sell", df["Type"][0])
        self.assertAlmostEqual(2.5, df["Price"][0])
        self.assertEqual("66.67%", df["Spread"][0])
        self.assertAlmostEqual(1., df["Amount"][0])
        self.assertEqual("00:01:40", df["Age"][0])
        self.assertEqual("yes", df["Hang"][0])
        # Test to see if df is created and order age is calculated
        df = LimitOrder.to_pandas(orders, 1.5, [])
        self.assertAlmostEqual(2.5, df["Price"][0])
        self.assertTrue(":" in df["Age"][0])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
