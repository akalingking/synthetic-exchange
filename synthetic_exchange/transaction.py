import datetime as dt
import itertools
import logging

from synthetic_exchange import classproperty
from synthetic_exchange.order import Order


class Transaction:
    _count = 0
    _last_id = itertools.count()

    def __init__(self, buyOrder, sellOrder, marketId, price, quantity):
        assert buyOrder.market_id == marketId
        assert sellOrder.market_id == marketId
        __class__._count += 1
        self.id = next(__class__._last_id)
        self.datetime = max(buyOrder.datetime, sellOrder.datetime)
        self.market_id = marketId
        self.buy_order = buyOrder
        self.sell_order = sellOrder
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return str(self.__dict__)

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


class Transactions:
    def __init__(self, marketId, agents):
        self._market_id = marketId
        self._history = []
        self._history_list = []
        self._history_market_agent = {}
        self._transactions = {}
        self._agents = agents

    def create(self, buyOrder, sellOrder, marketId, price, quantity) -> Transaction:
        buy_order_agent = self._agents.get(buyOrder.agent_id)
        sell_order_agent = self._agents.get(sellOrder.agent_id)
        assert buy_order_agent is not None
        assert sell_order_agent is not None

        transaction = Transaction(buyOrder, sellOrder, marketId, price, quantity)

        # Register order agents
        if buyOrder.agent_id not in self._history_market_agent:
            self._history_market_agent[buyOrder.agent_id] = []
        if sellOrder.agent_id not in self._history_market_agent:
            self._history_market_agent[sellOrder.agent_id] = []

        # Record history
        self._history.append(transaction)
        self._history_list.append([transaction.id, transaction.datetime.time(), transaction.price])

        self._history_market_agent[buy_order_agent.id].append(
            [
                transaction.id,
                buy_order_agent.position[marketId],
                Transaction.calculate_profit(buy_order_agent, marketId),
            ]
        )
        self._history_market_agent[sell_order_agent.id].append(
            [
                transaction.id,
                sell_order_agent.position[marketId],
                Transaction.calculate_profit(sell_order_agent, marketId),
            ]
        )

        buy_order_agent.position[marketId] += quantity
        sell_order_agent.position[marketId] -= quantity
        buy_order_agent.value_bought[marketId] += price * quantity
        buy_order_agent.quantity_bought[marketId] += quantity
        sell_order_agent.value_sold[marketId] += price * quantity
        sell_order_agent.quantity_sold[marketId] += quantity

        # Register transaction
        self._transactions[transaction.id] = transaction
        return transaction

    def remove(self, transactionId):
        if transactionId in self._transactions:
            del self._transactions[transactionId]
        else:
            logging.error(f"{__class__.__name__}.remove id: {transactionId} not found")

    def history(self):
        return self._history

    def history_list(self, marketId):
        retval = []
        if marketId in self._history_list:
            retval = self._history_list[marketId]
        else:
            logging.info(f"{__class__.__name__}.history_list market id: {marketId}")
        return retval

    def history_market_agent(self, marketId, agentName):
        retval = []
        if marketId in self._history_market_agent:
            agents = self._history_market_agent[marketId]
            if agentName in agents:
                retval = agents[agentName]
            else:
                logging.info(f"{__class__.__name__}.history_market_agent missing agent: {agentName}")
        else:
            logging.info(f"{__class__.__name__}.history_market_agent missing market id: {marketId}")
        return retval
