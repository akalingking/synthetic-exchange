import logging

from synthetic_exchange.market import Market


class Exchange:
    def __init__(self, config: dict):
        self._markets = {}
        currencies = config.get("currencies", {})
        for currency in currencies:
            try:
                symbol = currency["symbol"]
                min_price = currency["min_price"]
                max_price = currency["max_price"]
                tick_size = currency["tick_size"]
                min_quantity = currency["min_quantity"]
                max_quantity = currency["max_quantity"]
                self._markets[symbol] = Market(
                    symbol=symbol,
                    minPrice=min_price,
                    maxPrice=max_price,
                    tickSize=tick_size,
                    minQuantity=min_quantity,
                    maxQuantity=max_quantity,
                )
            except Exception as e:
                logging.error(f"{__class__.__name__}.__init__ e: {e}")

    def start(self):
        for _, market in self._markets.items():
            market.start()

    def stop(self):
        for _, market in self._markets.items():
            market.stop()

    def best_bid(self, symbol) -> float:
        retval = 0.0
        if symbol in self._markets.keys():
            market = self._markets[symbol]
            retval = market.get_buy_price()
        return retval

    def symbols(self) -> list:
        return list(self._markets.keys())

    def best_ask(self, symbol) -> float:
        retval = 0.0
        if symbol in self._markets.keys():
            market = self._markets[symbol]
            retval = market.get_sell_price()
        return retval

    def orderbook(self, symbol, depth: int = -1) -> dict:
        retval = {}
        if symbol in self._markets.keys():
            market = self._markets[symbol]
            retval = market.orderbook(depth=depth)
        return retval
