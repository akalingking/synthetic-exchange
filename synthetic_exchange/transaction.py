import datetime as dt
import itertools
import logging
import multiprocessing as mp

from synthetic_exchange.order import Order


class Transaction:
    _count = 0
    _last_id = itertools.count()

    def __init__(self, buyOrder, sellOrder, marketId, price, quantity):
        assert buyOrder.market_id == marketId
        assert sellOrder.market_id == marketId
        __class__._count += 1
        self.id = next(__class__._last_id)
        self.timestamp = max(buyOrder.timestamp, sellOrder.timestamp)
        self.market_id = marketId
        self.buy_order = buyOrder
        self.sell_order = sellOrder
        self.price = price
        self.quantity = quantity

    def __str__(self):
        retval = {}
        for k, v in self.__dict__.items():
            if k.lower() == "timestamp":
                assert isinstance(v, float)
                retval[k] = v
            else:
                retval[k] = v
        return str(retval)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def calculate_profit(agent, marketId):
        if agent.quantity_sold > 0:
            askVwap = agent.value_sold / agent.quantity_sold
        else:
            askVwap = 0
        if agent.quantity_bought > 0:
            bidVwap = agent.value_bought / agent.quantity_bought
        else:
            bidVwap = 0

        q = min(agent.quantity_sold, agent.quantity_bought)
        rp = q * (askVwap - bidVwap)
        return rp

    def transaction_description(bid: Order, offer: Order, marketId: int, price: float, quantity: float) -> str:
        return "At market {} - Best bid: {} ({}) Best offer: {} ({}) --> Transaction at: {} ({})".format(
            marketId, bid.price, bid.quantity, offer.price, offer.quantity, price, quantity
        )


class Transactions:
    def __init__(self, agents: dict):
        assert agents is not None
        self._history = mp.Manager().list()
        self._history_list = mp.Manager().list()
        self._history_market_agent = mp.Manager().dict()
        self._transactions = mp.Manager().dict()
        self._agents = agents

    @property
    def agents(self):
        return self._agents

    @agents.setter
    def agents(self, value):
        self._agents = value

    @property
    def transactions(self):
        return self._transactions

    @property
    def size(self) -> int:
        return len(self._transactions)

    def create(self, buyOrder, sellOrder, marketId, price, quantity) -> Transaction:
        buy_order_agent = self._agents.get(buyOrder.agent_id)
        sell_order_agent = self._agents.get(sellOrder.agent_id)
        assert buy_order_agent is not None
        assert sell_order_agent is not None

        transaction = Transaction(buyOrder, sellOrder, marketId, price, quantity)

        # Register order agents
        logging.debug(
            f"{__class__.__name__}.create history: {self._history_market_agent} "
            f"bid: {buyOrder.agent_id} sid: {sellOrder.agent_id}"
        )
        if buyOrder.agent_id not in self._history_market_agent:
            self._history_market_agent[buyOrder.agent_id] = []
        if sellOrder.agent_id not in self._history_market_agent:
            self._history_market_agent[sellOrder.agent_id] = []
        assert len(self._history_market_agent) > 0

        # Record history
        self._history.append(transaction)
        self._history_list.append([transaction.id, transaction.timestamp, transaction.price])
        buy_history = [
            [
                transaction.id,
                buy_order_agent.position,
                Transaction.calculate_profit(buy_order_agent, marketId),
            ],
        ]
        assert buyOrder.agent_id in self._history_market_agent
        self._history_market_agent[buyOrder.agent_id].append(buy_history)
        self._history_market_agent[buyOrder.agent_id] += buy_history
        sell_history = [
            [
                transaction.id,
                sell_order_agent.position,
                Transaction.calculate_profit(sell_order_agent, marketId),
            ],
        ]
        assert sellOrder.agent_id in self._history_market_agent
        self._history_market_agent[sellOrder.agent_id] += sell_history

        buy_order_agent.position += quantity
        sell_order_agent.position -= quantity
        buy_order_agent.value_bought += price * quantity
        buy_order_agent.quantity_bought += quantity
        sell_order_agent.value_sold += price * quantity
        sell_order_agent.quantity_sold += quantity

        # Register transaction
        self._transactions[transaction.id] = transaction
        logging.debug(f"{__class__.__name__}.create {transaction} size: {len(self._transactions)}")
        return transaction

    def remove(self, transactionId):
        if transactionId in self._transactions:
            del self._transactions[transactionId]
        else:
            logging.error(f"{__class__.__name__}.remove id: {transactionId} not found")

    @property
    def history(self):
        return self._history

    @property
    def history_list(self):
        return self._history_list

    def history_market_agent(self, agentId, agentName) -> list:
        retval = []
        if len(self._history_market_agent) > 0:
            if agentId in self._history_market_agent:
                agents = self._history_market_agent[agentId]
                if agentName in agents:
                    retval = agents[agentName]
                else:
                    logging.debug(f"{__class__.__name__}.history_market_agent missing agent: {agentName}")
            else:
                logging.debug(f"{__class__.__name__}.history_market_agent missing agent id: {agentId}")
        else:
            logging.warning(f"{__class__.__name__}.history_market_agent empty history market agent")
        return retval
