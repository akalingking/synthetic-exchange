import datetime as dt
import logging
import multiprocessing as mp
import time

from synthetic_exchange.market import Market
from synthetic_exchange.order import Order
from synthetic_exchange.orderbook import OrderBook
from synthetic_exchange.strategy import RandomNormal, RandomUniform
from synthetic_exchange.transaction import Transaction, Transactions


class Exchange:
    def __init__(self, config: dict):
        self._id = config["exchangeId"]
        self._name = config["exchange"]
        self._config = config
        self._symbol_to_market_id = {}
        self._market_id_to_symbol = {}
        self._symbols = {}
        self._markets = {}
        self._queues = {}
        self._agents = {}
        self._transactions = {}
        self._orderbooks = {}
        self._markets = {}

        markets_conf: list = config.get("markets", [])

        for market_conf in markets_conf:
            try:
                symbol = market_conf["symbol"]
                market_id = market_conf["marketId"]
                initial_price = market_conf["initialPrice"]
                min_price = market_conf["minPrice"]
                max_price = market_conf["maxPrice"]
                tick_size = market_conf["tickSize"]
                min_quantity = market_conf["minQuantity"]
                max_quantity = market_conf["maxQuantity"]

                self._market_id_to_symbol[market_id] = symbol
                self._symbol_to_market_id[symbol] = market_id
                self._queues[market_id] = mp.Queue(maxsize=100)

                # Build agents
                self._agents[market_id] = {}
                agents_conf: dict = market_conf["agents"]
                for _, agent_conf in agents_conf.items():
                    try:
                        agent_id = agent_conf["agentId"]
                        type_ = agent_conf["type"]
                        initial_price = agent_conf["initialPrice"]
                        min_price = agent_conf["minPrice"]
                        max_price = agent_conf["maxPrice"]
                        tick_size = agent_conf["tickSize"]
                        min_quantity = agent_conf["minQuantity"]
                        max_quantity = agent_conf["maxQuantity"]
                        if type_.lower() == "randomnormal":
                            a = RandomNormal(
                                marketId=market_id,
                                agentId=agent_id,
                                symbol=symbol,
                                initialPrice=initial_price,
                                minPrice=min_price,
                                maxPrice=max_price,
                                tickSize=tick_size,
                                minQuantity=min_quantity,
                                maxQuantity=max_quantity,
                                queue=self._queues[market_id],
                                wait=5,
                            )
                            self._agents[market_id][a.id] = a
                        elif type_.lower() == "randomuniform":
                            a = RandomUniform(
                                marketId=market_id,
                                agentId=agent_id,
                                symbol=symbol,
                                initialPrice=initial_price,
                                minPrice=min_price,
                                maxPrice=max_price,
                                tickSize=tick_size,
                                minQuantity=min_quantity,
                                maxQuantity=max_quantity,
                                queue=self._queues[market_id],
                                wait=5,
                            )
                            self._agents[market_id][a.id] = a
                        else:
                            logging.warning(f"{__class__.__name__}.__init__ unsupported agent type: {type_}")
                    except Exception as e:
                        logging.error(
                            f"{__class__.__name__}.__init__ market id: {market_id} symbol: {symbol} error creating agent: {agent_conf} e: {e}"
                        )

                self._transactions[market_id] = Transactions(agents=self._agents[market_id])
                self._orderbooks[market_id] = OrderBook(
                    marketId=market_id,
                    symbol=symbol,
                    transactions=self._transactions[market_id],
                    wait=5,
                    queue=self._queues[market_id],
                )
                self._markets[market_id] = Market(orderbook=self._orderbooks[market_id])
            except Exception as e:
                logging.error(
                    f"{__class__.__name__}.__init__ market id: {market_id} symbol: {symbol} error creating market: {market_conf} e: {e}"
                )

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def start(self):
        for _, market in self._markets.items():
            market.start()

    def stop(self):
        for _, market in self._markets.items():
            market.stop()

    def best_bid(self, symbol) -> float:
        retval = 0.0
        if symbol in self._symbol_to_market_id.keys():
            market_id = self._symbol_to_market_id[symbol]
            assert market_id in self._markets.keys()
            market = self._markets[market_id]
            retval = market.get_buy_price()
        else:
            logging.error(f"{__class__.__name__}.orderbook {symbol} not found")
        return retval

    def symbols(self) -> list:
        return list(self._symbol_to_market_id.keys())

    def best_ask(self, symbol) -> float:
        retval = 0.0
        if symbol in self._symbol_to_market_id.keys():
            market_id = self._symbol_to_market_id[symbol]
            assert market_id in self._markets.keys()
            market = self._markets[market_id]
            retval = market.get_sell_price()
        else:
            logging.error(f"{__class__.__name__}.orderbook {symbol} not found")
        return retval

    def orderbook(self, symbol, depth: int = -1) -> dict:
        retval = {}
        if symbol in self._symbol_to_market_id.keys():
            market_id = self._symbol_to_market_id[symbol]
            assert market_id in self._markets.keys()
            market = self._markets[market_id]
            retval = market.orderbook(depth=depth)
        else:
            logging.error(f"{__class__.__name__}.orderbook {symbol} not found")
        return retval
