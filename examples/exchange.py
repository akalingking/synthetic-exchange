import logging
import multiprocessing as mp
import sys
import time

from synthetic_exchange import OrderBook, Transactions
from synthetic_exchange.exchange import Exchange
from synthetic_exchange.market import Market
from synthetic_exchange.order import Order
from synthetic_exchange.strategy import RandomNormal, RandomUniform

_config = {
    "exchangeId": 0,
    "exchange": "sqncrsch",
    "api_enable": True,
    "markets": [
        {
            "marketId": 0,
            "symbol": "SMBL0",
            "initialPrice": 100.0,
            "minPrice": 100.0,
            "maxPrice": 115.0,
            "tickSize": 1,
            "minQuantity": 0.5,
            "maxQuantity": 1.0,
            "agents": {
                "agent_0": {
                    "agentId": 0,
                    "type": "randomnormal",
                    "initialPrice": 50.0,
                    "minPrice": 50.0,
                    "maxPrice": 53.0,
                    "tickSize": 1,
                    "minQuantity": 1.0,
                    "maxQuantity": 5.0,
                },
                "agent_1": {
                    "agentId": 1,
                    "type": "randomnormal",
                    "initialPrice": 50.0,
                    "minPrice": 50.0,
                    "maxPrice": 53.0,
                    "tickSize": 1,
                    "minQuantity": 1.0,
                    "maxQuantity": 5.0,
                },
            },
        },
        {
            "marketId": 1,
            "symbol": "SMBL1",
            "initialPrice": 50.0,
            "minPrice": 50.0,
            "maxPrice": 53.0,
            "tickSize": 1,
            "minQuantity": 1.0,
            "maxQuantity": 5.0,
            "agents": {
                "agent_0": {
                    "agentId": 0,
                    "type": "randomnormal",
                    "initialPrice": 100.0,
                    "minPrice": 100.0,
                    "maxPrice": 115.0,
                    "tickSize": 1,
                    "minQuantity": 1.0,
                    "maxQuantity": 5.0,
                },
                "agent_1": {
                    "agentId": 1,
                    "type": "randomuniform",
                    "initialPrice": 100.0,
                    "minPrice": 100.0,
                    "maxPrice": 115.0,
                    "tickSize": 1,
                    "minQuantity": 1.0,
                    "maxQuantity": 5.0,
                },
            },
        },
    ],
}


def main():
    print(f"{sys.argv[0]} starting..")
    exchange = Exchange(config=_config)
    exchange.start()

    time.sleep(60)

    exchange.stop()
    symbols = exchange.symbols()
    for symbol in symbols:
        print(f"******exchange: {exchange.name} symbol: {symbol} orderbook*******")
        ob_ = exchange.orderbook(symbol=symbol)
        print(ob_)
        assert all([i in ob_ for i in ["symbol", "bids", "asks"]])
        print(f"******exchange: {exchange.name} symbol: {symbol} orderbook*******")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
