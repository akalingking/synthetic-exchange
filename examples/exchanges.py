import json
import logging
import multiprocessing as mp
import sys
import time

from synthetic_exchange import OrderBook, Transactions
from synthetic_exchange.exchange import Exchange
from synthetic_exchange.market import Market
from synthetic_exchange.order import Order
from synthetic_exchange.strategy import RandomNormal, RandomUniform

_application = "exchanges"

_exchange_configs = [
    "examples/exchange_0.json",
    "examples/exchange_1.json",
]


def get_config_from_file(fname: str) -> dict:
    config = None
    try:
        with open(fname) as f:
            config = json.load(f)
    except Exception as e:
        print(f"get_config_from_file exception: '{e}'")
    return config


def main():
    global _application
    _application = sys.argv[0]

    print(f"{_application} starting..")

    configs = {}
    exchanges = {}

    for config in _exchange_configs:
        print(f"reading {config}")
        conf = get_config_from_file(config)
        assert isinstance(conf, dict)
        configs[conf["exchangeId"]] = conf

    for exchange_id, config in configs.items():
        exchanges[exchange_id] = Exchange(config=config)

    for _, exchange in exchanges.items():
        exchange.start()

    time.sleep(60)

    for _, exchange in exchanges.items():
        exchange.stop()

    for id_, exchange in exchanges.items():
        symbols = exchange.symbols()
        for symbol in symbols:
            print(f"******exchange: {exchange.name} symbol: {symbol} orderbook*******")
            ob_ = exchange.orderbook(symbol=symbol)
            print(ob_)
            print(f"******exchange: {exchange.name} symbol: {symbol} orderbook*******")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
