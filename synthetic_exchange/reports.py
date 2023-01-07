import operator

import matplotlib.pyplot as plt
import pandas as pd

from synthetic_exchange.orderbook import OrderBook
from synthetic_exchange.transaction import Transaction, Transactions


class Reports:
    def __init__(self, marketId: int):
        self._market_id = marketId

    def summary(self, transactions: Transactions):
        df = pd.DataFrame(Transaction.history_list(self.id), columns=["id", "time", "price"])
        df["volatility"] = df["price"].rolling(7).std()
        df["volatilityTrend"] = df["volatility"].rolling(100).mean()
        df = df[["id", "price", "volatility", "volatilityTrend"]]
        df = df.set_index("id")

        dfPrice = df["price"]
        dfVolatility = df[["volatility", "volatilityTrend"]]

        # PLOT PRICE
        fig, axs = plt.subplots(2, 2)
        axs[0, 0].plot(dfPrice, label="price")
        axs[0, 0].set_title("Price")
        axs[0, 0].legend()
        # PLOT VOLATILITY
        axs[0, 1].plot(dfVolatility)
        axs[0, 1].set_title("Volatility")
        axs[0, 1].legend()
        # PLOT RUNNING POSITIONS + RUNNING PROFITS AGENTS
        for i, a in self._agents.agents.items():
            right = pd.DataFrame(
                Transaction.history_market_agent(self.id, a.name), columns=["id", a.name, str(a.name) + "RunningProfit"]
            )
            right = right.set_index("id")
            right = right[a.name]
            axs[1, 0].plot(right, label=str(a.name))
        axs[1, 0].set_title("Positions")

        if self._agents.size < 20:
            axs[1, 0].legend()

        for i, a in self._agents.agents.items():
            right = pd.DataFrame(
                Transaction.history_market_agent(self.id, a.name), columns=["id", a.name, str(a.name) + "RunningProfit"]
            )
            right = right.set_index("id")
            right = right[str(a.name) + "RunningProfit"]
            axs[1, 1].plot(right, label=str(a.name) + "RunningProfit")

        axs[1, 1].set_title("Running profit")
        return plt.show()

    def show_orderbook(self, ob: OrderBook, depth: int = 10):
        width = len("0       Bert    Buy     33      5")
        print(width * 2 * "*")

        sell_orders = sorted(ob.active_sell_orders[self.id], key=operator.attrgetter("price"), reverse=True)[:depth]
        for order in sell_orders:
            print(width * "." + " " + str(order))

        buy_orders = sorted(ob.active_buy_orders[self.id], key=operator.attrgetter("price"), reverse=False)[:depth]
        for order in buy_orders:
            print(str(order) + " " + width * ".")

        print(width * 2 * "*")
        print(" ")
