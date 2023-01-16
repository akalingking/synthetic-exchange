import logging
import operator

import matplotlib.pyplot as plt
import pandas as pd

from synthetic_exchange.agent import Agent
from synthetic_exchange.agents import Agents
from synthetic_exchange.orderbook import OrderBook
from synthetic_exchange.transaction import Transaction, Transactions


class Reports:
    def __init__(self, marketId: int, show=False):
        self._market_id = marketId
        self._show = show

    def show_transactions(self, transactions: Transactions):
        assert isinstance(transactions, Transactions)
        if len(transactions.history_list) < 0:
            logging.warning(f"{__class__.__name__}.show_transactions no history")
            return

        df = pd.DataFrame(transactions.history_list, columns=["id", "time", "price"])
        df["volatility"] = df["price"].rolling(7).std()
        df["volatilityTrend"] = df["volatility"].rolling(100).mean()
        df = df[["id", "price", "volatility", "volatilityTrend"]]
        df = df.set_index("id")

        dfPrice = df["price"]
        dfVolatility = df[["volatility", "volatilityTrend"]]

        # Set plt properties
        fig, axs = plt.subplots(2, 2)
        fig.suptitle("Orderbook Transactions", fontsize=16)
        fig.tight_layout()
        fig.autofmt_xdate()
        plt.subplots_adjust(top=0.88)
        plt.grid(True)

        # Construct subplots
        # 1. Price
        axs[0, 0].plot(dfPrice, label="price")
        axs[0, 0].set_title("Price")
        axs[0, 0].legend()

        # 2. Volatility
        axs[0, 1].plot(dfVolatility)
        axs[0, 1].set_title("Volatility")
        axs[0, 1].legend()

        # 1. Plot positions
        assert isinstance(transactions.agents, Agents)
        assert isinstance(transactions.agents.agents, dict)
        assert len(transactions.agents.agents) > 0
        for i, a in transactions.agents.agents.items():
            data = transactions.history_market_agent(a.id, a.name)
            if len(data) > 0:
                right = pd.DataFrame(data, columns=["id", a.name, str(a.name) + "RunningProfit"])
                right = right.set_index("id")
                right = right[a.name]
                axs[1, 0].plot(right, label=str(a.name))
            else:
                logging.warning(f"{__class__.__name__}.show_transactions no data for agent: {a.name}")
        axs[1, 0].set_title("Positions")

        if transactions.agents.size < 20:
            axs[1, 0].legend()

        # 3. Plot profit
        for i, a in transactions.agents.agents.items():
            data = transactions.history_market_agent(a.id, a.name)
            assert isinstance(data, list)
            if len(data) > 0:
                right = pd.DataFrame(data, columns=["id", a.name, str(a.name) + "RunningProfit"])
                right = right.set_index("id")
                right = right[str(a.name) + "RunningProfit"]
                axs[1, 1].plot(right, label=str(a.name) + "RunningProfit")
            else:
                logging.warning(f"{__class__.__name__}.show_transactions no data for agent: {a.name}")
        axs[1, 1].set_title("Running profit")

        if self._show:
            plt.show()
        else:
            fname = "data/transactions.pdf"
            logging.info(f"{__class__.__name__}.show_transactions saving to {fname}")
            plt.savefig(fname)
            plt.close(fig)

    def show_orderbook(self, ob: OrderBook, depth: int = 10):
        print(f"{__class__.__name__}.show_orderbook")
        width = len("0       Bert    Buy     33      5")
        print(width * 2 * "*")
        assert isinstance(ob.active_sell_orders, list)

        if len(ob.active_sell_orders) > 0:
            sell_orders = sorted(ob.active_sell_orders, key=operator.attrgetter("price"), reverse=True)[:depth]
            for order in sell_orders:
                print(width * "." + " " + str(order))
        else:
            logging.warning(f"{__class__.__name__}.show_orderbook no active sell orders")

        assert isinstance(ob.active_buy_orders, list)
        if len(ob.active_buy_orders) > 0:
            buy_orders = sorted(ob.active_buy_orders, key=operator.attrgetter("price"), reverse=False)[:depth]
            for order in buy_orders:
                print(str(order) + " " + width * ".")
        else:
            logging.warning(f"{__class__.__name__}.show_orderbook no active buy orders")

        print(width * 2 * "*")
        print(" ")
