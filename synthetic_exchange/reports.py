import logging
import multiprocessing as mp
import operator

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from synthetic_exchange.agent import Agent
from synthetic_exchange.agents import Agents
from synthetic_exchange.orderbook import OrderBook
from synthetic_exchange.transaction import Transaction, Transactions


class _Config:
    vol_period = 7
    trend_period = 100


class Reports:
    def __init__(self, marketId: int, show=False):
        self._market_id = marketId
        self._show = show

    def show_transactions(self, transactions: Transactions):
        assert isinstance(transactions, Transactions)
        if len(transactions.history_list) < 0:
            logging.warning(f"{__class__.__name__}.show_transactions no history")
            return

        data = np.array(transactions.history_list)
        df = pd.DataFrame(data, columns=["id", "time", "price"])
        df["volatility"] = df["price"].rolling(_Config.vol_period).std()
        df["volatilityTrend"] = df["volatility"].rolling(_Config.trend_period).mean()
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

        print(f"{__class__.__name__}.show_transactions history_market_agent: {transactions.history_market_agent}")
        for i, a in transactions.agents.agents.items():
            # data = transactions.history_market_agent(a.id, a.name)
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
        logging.info(f"{__class__.__name__}.show_orderbook entry")
        width = len("0       Bert    Buy     33      5")
        assert isinstance(ob.active_sell_orders, mp.managers.ListProxy)
        assert isinstance(ob.active_buy_orders, mp.managers.ListProxy)

        print(width * 1 * "*" + "Active Sell Orders" + width * 1 * "*")
        if len(ob.active_sell_orders) > 0:
            sell_orders = sorted(ob.active_sell_orders, key=operator.attrgetter("price"), reverse=True)[:depth]
            for order in sell_orders:
                # print(width * "." + " " + str(order))
                print(str(order))
        else:
            logging.warning(f"{__class__.__name__}.show_orderbook no active sell orders")
        print(width * 1 * "*" + "Active Sell Orders" + width * 1 * "*")

        print(width * 1 * "*" + "Active Buy Orders" + width * 1 * "*")
        if len(ob.active_buy_orders) > 0:
            buy_orders = sorted(ob.active_buy_orders, key=operator.attrgetter("price"), reverse=False)[:depth]
            for order in buy_orders:
                # print(str(order) + " " + width * ".")
                print(str(order))
        else:
            logging.warning(f"{__class__.__name__}.show_orderbook no active buy orders")
        print(width * 1 * "*" + "Active Buy Orders" + width * 1 * "*")
        print(" ")
        logging.info(f"{__class__.__name__}.show_orderbook exit")
