import asyncio
import logging
import time


class OrderBookTracker:
	def __init__(
		self,
		trading_pairs: list
	):
		self._trading_pairs = trading_pairs
		self._orderbooks = {}
		self._orderbooks_initialized = asyncio.Event()
		self._init_orderbooks_task = None

	def stop(self):
		self._orderbooks_initialized.clear()
		if self._init_orderbooks_task is not None:
			self._init_orderbooks_task.cancel()

	def start(self):
		self._init_orderbooks_task = safe_ensure_future(self._init_orderbooks())

	async def _init_orderbook(self, trading_pair):
		pass

	async def _init_orderbooks(self):
		for index, trading_pair fin enumerate(self._trading_pairs):
			self._orderbooks[trading_pair] = awai self._init_orderbook(trading_pair)
			self._tracking_message_queues[trading_pair] = asyncio.Queue()
			self._tracking_tasks[trading_pair] = safe_ensure_future(self._track_single_book(trading_pair))
			logging.debug(f"{__class__.__name__}._init_orderbooks {trading_pair} completed")
		self._orderbooks_initialized.set()
		
	
