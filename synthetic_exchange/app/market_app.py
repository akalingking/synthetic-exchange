import logging
import multiprocessing
import multiprocessing as mp
import signal
import sys
import time

from synthetic_exchange import util
from synthetic_exchange.app.application import Application
from synthetic_exchange.app.web.application import WebApplication
from synthetic_exchange.exchange import Exchange
from synthetic_exchange.util import get_config_from_file


class Constants:
	app_name = "marketapp"
	config_file = f"synthetic_exchange/app/{app_name}.json"
	log_file = f"synthetic_exchange/app/{app_name}.log"
	tracemalloc = False
	exchange_config_files = [
		"synthetic_exchange/app/conf/exchange_0.json",
		"synthetic_exchange/app/conf/exchange_1.json",
	]


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


class ExchangeApplication(Application):
	def __init__(self, exchanges: dict, *args, **kwargs):
		self._exchanges = exchanges
		Application.__init__(self, **kwargs)

	def terminate(self):
		Application.terminate(self)

	def run(self):
		Application.run(self)

	def _do_work(self):
		try:
			for exchange in self._exchanges.values():
				symbols = exchange.symbols()
				for symbol in symbols:
					logging.info(">>>ExchangeApplication.do_work exchange: {} symbol: {} bid: {} ask: {}".format(
						exchange.name, symbol, exchange.best_bid(symbol), exchange.best_ask(symbol)
					))
		except Exception as e:
			logging.error(f"{__class__.__name__}._do_work error: {e}")

	def show_transactions(self):
		self._market.show_transactions()

	def show_orderbook(self):
		self._market.show_orderbook()


def main():
	print(f"{sys.argv[0]} starting...")
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
		logging.basicConfig(level=logging.INFO)

		# markets: multiprocessing.managers.DictProxy = mp.Manager().dict()
		"""
		"""
		#exchanges = mp.Manager().dict()
		exchanges = {}
		for config_file in Constants.exchange_config_files:
			config = get_config_from_file(config_file)
			exchange_id = config["exchangeId"]
			exchange = Exchange(config=config)
			exchange.start()
			exchanges[exchange_id] = exchange

		time.sleep(30)
			
		if len(exchanges) > 0:
			application = ExchangeApplication(exchanges)
			application.start()
			application.wait()
			for exchange in exchanges:
				exchange.stop()
	else:
		print(f"{Constants.config_file} not found!")
	print(f"{sys.argv[0]} stopped!")


if __name__ == "__main__":
	if Constants.tracemalloc:
		util.tracemalloc_start()
		main()
		util.tracemalloc_stop()
	else:
		main()
