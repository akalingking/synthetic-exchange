import itertools
import logging

from synthetic_exchange import classproperty
from synthetic_exchange.order import Order


class Transaction:
    _counter = itertools.count()
    _history = {}
    _history_list = {}
    _history_market_agent = {}
    _transaction_counter = 0

    def __init__(self, buyOrder, sellOrder, marketId, price, quantity):
        assert buyOrder.market_id == marketId
        assert sellOrder.market_id == marketId
        __class__._transaction_counter += 1
        self._id = next(__class__._counter)
        self._datetime = max(buyOrder.datetime, sellOrder.datetime)
        self._market_id = marketId
        self._buy_order = buyOrder
        self._sell_order = sellOrder
        self._price = price
        self._quantity = quantity

        # If first transaction by agent at market --> initialize values
        if marketId not in buyOrder.agent.position:
            buyOrder.agent.position[marketId] = 0
            buyOrder.agent.value_bought[marketId] = 0
            buyOrder.agent.quantity_bought[marketId] = 0
            buyOrder.agent.value_sold[marketId] = 0
            buyOrder.agent.quantity_sold[marketId] = 0

        if marketId not in sellOrder.agent.position.keys():
            sellOrder.agent.position[marketId] = 0
            sellOrder.agent.value_bought[marketId] = 0
            sellOrder.agent.quantity_bought[marketId] = 0
            sellOrder.agent.value_sold[marketId] = 0
            sellOrder.agent.quantity_sold[marketId] = 0

        if marketId not in __class__._history.keys():
            __class__._history[marketId] = []
            __class__._history_list[marketId] = []

        if (marketId, buyOrder.agent.name) not in __class__._history_market_agent.keys():
            __class__._history_market_agent[marketId, buyOrder.agent.name] = []
        if not (marketId, sellOrder.agent.name) in __class__._history_market_agent.keys():
            __class__._history_market_agent[marketId, sellOrder.agent.name] = []

        # Update values agents at market
        buyOrder.agent.position[marketId] += quantity
        sellOrder.agent.position[marketId] -= quantity
        buyOrder.agent.value_bought[marketId] += price * quantity
        buyOrder.agent.quantity_bought[marketId] += quantity
        sellOrder.agent.value_sold[marketId] += price * quantity
        sellOrder.agent.quantity_sold[marketId] += quantity

        logging.info(
            f"{__class__.__name__} adding new transaction: {self.id} for "
            f"orders (buy: {buyOrder.id} sell: {sellOrder,id})"
        )

        # Add to transaction history
        __class__._history[marketId].append(self)
        __class__._history_list[marketId].append([self.id, self._datetime.time(), self._price])

        # Add to history agent at market
        __class__.history_market_agent[marketId, buyOrder.agent.name].append(
            [self.id, buyOrder.agent.position[marketId], __class__.calculate_profit(buyOrder.agent, marketId)]
        )
        __class__.history_market_agent[marketId, sellOrder.agent.name].append(
            [self.id, sellOrder.agent.position[marketId], __class__.calculate_profit(sellOrder.agent, marketId)]
        )

    @property
    def id(self) -> int:
        return self._id

    @property
    def price(self) -> float:
        return self._price

    @classproperty
    def history(cls):
        return cls._history

    # classproperty
    def transaction_counter(cls):
        return cls._transaction_counter

    @staticmethod
    def history_list(marketId):
        retval = []
        if marketId in __class__._history_list:
            retval = __class__._history_list[marketId]
        else:
            logging.info(f"{__class__.__name__}.history_list market id: {marketId}")
        return retval

    @staticmethod
    def history_market_agent(marketId, agentName):
        retval = []
        if marketId in __class__._history_market_agent:
            agents = __class__._history_market_agent[marketId]
            if agentName in agents:
                retval = agents[agentName]
            else:
                logging.info(f"{__class__.__name__}.history_market_agent missing agent: {agentName}")
        else:
            logging.info(f"{__class__.__name__}.history_market_agent missing market id: {marketId}")
        return retval

    def __str__(self):
        return "{} \t {} \t {} \t {} \t {} \t {} \t {}".format(
            self._id,
            self._datetime.time(),
            self._market_id,
            self._buy_order.agent.name,
            self._sell_order.agent.name,
            self._price,
            self._quantity,
        )

    @staticmethod
    def calculate_profit(agent, marketId):
        if agent.quantity_sold[marketId] > 0:
            askVwap = agent.value_sold[marketId] / agent.quantity_sold[marketId]
        else:
            askVwap = 0
        if agent.quantity_bought[marketId] > 0:
            bidVwap = agent.value_bought[marketId] / agent.quantity_bought[marketId]
        else:
            bidVwap = 0

        q = min(agent.quantity_sold[marketId], agent.quantity_bought[marketId])
        rp = q * (askVwap - bidVwap)
        return rp

    def transaction_description(bid: Order, offer: Order, marketId: int, price: float, quantity: float) -> str:
        return "At market {} - Best bid: {} ({}) Best offer: {} ({}) --> Transaction at: {} ({})".format(
            marketId, bid.price, bid.quantity, offer.price, offer.quantity, price, quantity
        )
