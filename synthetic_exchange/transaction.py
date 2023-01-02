import itertools
import logging

from synthetic_exchange import classproperty


class Transaction:
    _counter = itertools.count()
    _history = {}
    _history_list = {}
    _history_market_agent = {}

    def __init__(self, buyOrder, sellOrder, market, price, quantity):
        market.transaction_counter += 1
        self._id = next(__class__._counter)
        self._datetime = max(buyOrder.datetime, sellOrder.datetime)
        self._market = market
        self._buy_order = buyOrder
        self._sell_order = sellOrder
        self._price = price
        self._quantity = quantity

        # If first transaction by agent at market --> initialize values
        if market.id not in buyOrder.agent.position:
            buyOrder.agent.position[market.id] = 0
            buyOrder.agent.value_bought[market.id] = 0
            buyOrder.agent.quantity_bught[market.id] = 0
            buyOrder.agent.value_sold[market.id] = 0
            buyOrder.agent.quantity_sold[market.id] = 0

        if market.id not in sellOrder.agent.position.keys():
            sellOrder.agent.position[market.id] = 0
            sellOrder.agent.value_bought[market.id] = 0
            sellOrder.agent.quantity_bought[market.id] = 0
            sellOrder.agent.value_sold[market.id] = 0
            sellOrder.agent.quantity_sold[market.id] = 0

        if market.id not in __class__._history.keys():
            __class__._history[market.id] = []
            __class__._history_list[market.id] = []

        if not (market.id, buyOrder.agent.name) in __class__._history_market_agent.keys():
            __class__._history_market_agent[market.id, buyOrder.agent.name] = []
        if not (market.id, sellOrder.agent.name) in __class__._history_market_agent.keys():
            __class__._history_market_agent[market.id, sellOrder.agent.name] = []

        # Update values agents at market
        buyOrder.agent.position[market.id] += quantity
        sellOrder.agent.position[market.id] -= quantity
        buyOrder.agent.value_bought[market.id] += price * quantity
        buyOrder.agent.quantity_bought[market.id] += quantity
        sellOrder.agent.value_sold[market.id] += price * quantity
        sellOrder.agent.quantity_sold[market.id] += quantity

        # Add to transaction history
        __class__._history[market.id].append(self)
        __class__._history_list[market.id].append([self.id, self._datetime.time(), self._price])

        # Add to history agent at market
        __class__.history_market_agent[market.id, buyOrder.agent.name].append(
            [self.id, buyOrder.agent.position[market.id], __class__.calculate_profit(buyOrder.agent, market)]
        )
        __class__.history_market_agent[market.id, sellOrder.agent.name].append(
            [self.id, sellOrder.agent.position[market.id], __class__.calculate_profit(sellOrder.agent, market)]
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
            self._market,
            self._buy_order.agent.name,
            self._sell_order.agent.name,
            self._price,
            self._quantity,
        )

    @staticmethod
    def calculate_profit(agent, market):
        if agent.quantity_sold[market.id] > 0:
            askVwap = agent.value_sold[market.id] / agent.quantity_sold[market.id]
        else:
            askVwap = 0
        if agent.quantity_bought[market.id] > 0:
            bidVwap = agent.value_bought[market.id] / agent.quantity_bought[market.id]
        else:
            bidVwap = 0

        q = min(agent.quantity_sold[market.id], agent.quantity_bought[market.id])
        rp = q * (askVwap - bidVwap)
        return rp

    def transaction_description(bid, offer, market, price, quantity) -> str:
        return "At market {} - Best bid: {} ({}) Best offer: {} ({}) --> Transaction at: {} ({})".format(
            market.id, bid.price, bid.quantity, offer.price, offer.quantity, price, quantity
        )
