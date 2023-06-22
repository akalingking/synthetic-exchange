import logging
import signal
import sys

from synthetic_exchange import util
from synthetic_exchange.app import Application
from synthetic_exchange.market import Market


class Constants:
    name = "marketapp"
    config = "synthetic_exchange/config.json"
    tracemalloc = False


application = None


def signal_handler(sig, frame):
    print(f"Ctrl+C, stopping {Constants.name} application!")
    if application is not None:
        application.stop()
    if Constants.tracemalloc:
        util.tracemalloc_stop()
    sys.exit(0)


class MarketApplication(Application):
    # Single market exchange application

    def __init__(self):
        self._currency = "SQNC-RSCH"
        self._market = Market(
            symbol=self._currency, minPrice=100, maxPrice=200, tickSize=1, minQuantity=25, maxQuantity=50
        )
        self._wait = 30
        Application.__init__(self)
        self._market.start()

    def run(self):
        Application.run(self)

    def _do_work(self):
        bid_p = self._market.get_buy_price()
        ask_p = self._market.get_sell_price()
        spread = self._market.get_spread()
        print(f"{__class__.__name__}._do_work {self._currency} bid: {bid_p} ask: {ask_p} spread: {spread}")


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)

    application = MarketApplication()
    application.start()
    application.wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if Constants.tracemalloc:
        util.tracemalloc_start()
        main()
        util.tracemalloc_stop()
    else:
        main()
