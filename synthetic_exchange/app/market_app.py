import logging
import multiprocessing
import multiprocessing as mp
import signal
import sys

from synthetic_exchange import util
from synthetic_exchange.app.application import Application
from synthetic_exchange.app.web.application import WebApplication
from synthetic_exchange.market import Market
from synthetic_exchange.util import get_config_from_file


class Constants:
    app_name = "marketapp"
    config_file = f"synthetic_exchange/app/{app_name}.json"
    log_file = f"synthetic_exchange/app/{app_name}.log"
    tracemalloc = False


application = None


def signal_handler(sig, frame):
    try:
        print(f"{Constants.app_name}.signal_handler Ctrl+C, stopping {Constants.app_name} application!")
        if application is not None:
            application.stop()
        if Constants.tracemalloc:
            util.tracemalloc_stop()
    except Exception as e:
        print(f"{Constants.app_name}.signal_handler error: {e}!")
    sys.exit(0)


class MarketApplication(Application):
    # Single market exchange application

    # def __init__(self, markets: multiprocessing.managers.DictProxy, *args, **kwargs):
    def __init__(self, markets, *args, **kwargs):
        print(f"{__class__.__name__}.__init__")
        assert markets is not None
        self._currencies = kwargs.get("currencies")
        assert self._currencies is not None
        print(self._currencies)
        self._markets = markets
        # single market
        # self._market = Market(
        #    symbol=self._currency, minPrice=100, maxPrice=200, tickSize=1, minQuantity=25, maxQuantity=50
        # )
        # for currency, values in self._currencies.items():
        #    self._markets[currency] = Market(currency, **values)

        Application.__init__(self, **kwargs)
        # for currency, market in self._markets.items():
        #    market.start()
        # self._market.start()
        # self._web = WebApplication(**kwargs)
        # self._web.start()

    def termimate(self):
        print(f"{__class__.__name__}.terminate entry")
        self._web.stop()
        self._web.wait()
        Application.terminate(self)
        print(f"{__class__.__name__}.terminate exit")

    def run(self):
        Application.run(self)

    def _do_work(self):
        pass
        """for currency, market in self._markets:
            bid_p = market.get_buy_price()
            ask_p = market.get_sell_price()
            spread = market.get_spread()
            logging.info(f"{__class__.__name__}._do_work {currency} bid: {bid_p} ask: {ask_p} spread: {spread}")
            #self.show_transactions()
            #self.show_orderbook()
        """

    def show_transactions(self):
        self._market.show_transactions()

    def show_orderbook(self):
        self._market.show_orderbook()


def main():
    global application
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)

    config = get_config_from_file(Constants.config_file)
    if config is not None:
        app_conf = config["application"]
        log_level_name = app_conf.get("loglevel", "info").upper()
        log_level = logging.getLevelName(log_level_name)
        log_to_file = True if app_conf.get("logtofile", "false").upper() == "TRUE" else False
        # enable_api = True if app_conf.get("enableapi", "false").upper() == "TRUE" else False
        if log_to_file:
            log_file = app_conf.get("logfile", f"./{Constants.app_name}.log")
            logging.basicConfig(
                filename=log_file,
                filemode="a",
                # format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(funcName)s %(message)s",
                format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                datefmt="%H:%M:%S",
                level=log_level,
            )
        else:
            logging.basicConfig(
                format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                datefmt="%H:%M:%S",
                level=log_level,
            )
        logging.basicConfig(level=logging.DEBUG)

        # markets: multiprocessing.managers.DictProxy = mp.Manager().dict()
        markets = mp.Manager().dict()
        currencies = config["currencies"]
        for currency, values in currencies.items():
            market = Market(currency, **values)
            market.start()
            markets[currency] = market
        print(type(markets))
        assert markets is not None
        application = MarketApplication(markets, **config)
        # application.start()
        # application.wait()
    else:
        print(f"{Constants.config_file} not found!")


if __name__ == "__main__":
    try:
        if Constants.tracemalloc:
            util.tracemalloc_start()
            main()
            util.tracemalloc_stop()
        else:
            main()
    except Exception as e:
        print(f"{Constants.app_name} error: {e}!")
