from enum import Enum
import logging
import gzip
import json
from synthetic_exchange.experimental.dtype import Instrument, AssetType, ExchangeType, NameToExchangeType


def _str_to_int(str_, mult):
    return round(float(str_) * mult)


def init_row(row):
    assert isinstance(row, str)
    channel, now, event = "", 0, ""
    try:
        # set to nanosecond
        now = int(row[:16]) * 10 ** 3
        row_dict = json.loads(row[17:])
        channel = ""
        if "stream" in row_dict:
            channel =  row_dict["stream"]
        event = ""
        if "data" in row_dict:
            event = json.dumps(row_dict["data"])
        if channel == ""  or event == "":
            event = row[17:]
    except Exception as e:
        logging.error(f"init_row e: {e} now_s: '{row[:16]}' row: '{row}'")
    return channel, now, event


class Parser:
	def __init__(self):
		pass

	def parse(self, filename: str, instrument: Instrument, verbose: bool=False):
		events = []
		rows = []
		with gzip.open(filename, "rt") as f:
			rows = f.read().split("\n")
		assert len(rows) > 0
		if len(rows) > 0:
			events = self.parse_rows(rows, instrument, verbose)
		else:
			logging.error(f"Parser.parse empty rows instrument: {instrument}")
		return events

	def parse_rows(self, rows: list, instrument: Instrument, verbose: bool=False):
		events = []
		exchange_type = NameToExchangeType[instrument.exchange]
		asset_type = instrument.asset_type
		if exchange_type == ExchangeType.ExchangeType_Binance:
			if asset_type == AssetType.AssetType_Perpetual:
				events = __class__._parse_binance_perp(rows, instrument, verbose)
			elif asset_type == AssetType.AssetType_Spot:
				raise NotImplementedError()
			else:
				logging.error(f"Parser.parse_rows invalid instrument asset type: {instrument}")
		else:
			logging.error(f"Parser.parse invalid instrument: {instrument}")
		return events

	@staticmethod
	def _parse_binance_perp(rows: list, instrument: Instrument, verbose: bool=False) -> list:
		logging.debug(f"Parser._parse_binance_perp row size: {len(rows)} entry")

		events = []
		exchange = instrument.exchange
		price_mult = instrument.price_mult
		assert price_mult > 0
		size_mult = instrument.size_mult
		assert size_mult > 0
		last_depth_update_id = {}
		last_trade_id = 0
		last_agg_trade_id = 0
		last_bbo_id = 0
		channel = ''
		warning_count = 0
		ignored_event_count = 0
		exception_count = 0

		for row in rows:
			try:
				if len(row) < 16:
					if verbose:
						logging.warning(f"Parser._parse_binance_perp empty row: {row}")
					continue
				channel, now, event = init_row(row)
				assert isinstance(now, int)
				event = json.loads(event)
				time = event.get('T', 0) * 10**6
				time_e = event.get('E', 0) * 10**6
				new_event = {}
				new_event['time'] = time
				new_event['time_e'] = time_e
				new_event['now'] = now
				event['now'] = now

				if 'e' in event:
					event_type = event["e"]
					if event_type == 'trade':
						try:
							if event['X'] != 'MARKET':
								continue
							if event['t'] <= last_trade_id:
								continue
							last_trade_id = event['t']
							new_event['type'] = 'Trade'
							side = 'sell' if event['m'] else 'buy'

							new_event['side'] = side
							new_event['price'] = _str_to_int(event['p'], price_mult)
							new_event['size'] = _str_to_int(event['q'], size_mult)
							assert new_event["size"] > 0, "check size_mult"
							new_event['id'] = event['t']
						except Exception as e:
							logging.warning("error parsing {} e: {}".format(event_type, str(e)))
							exception_count += 1
							continue

					elif event_type == 'aggTrade':
						try:
							if event['l'] <= last_agg_trade_id:
								continue
							last_agg_trade_id = event['l']
							new_event['type'] = 'AggTrade'
							side = 'sell' if event['m'] else 'buy'
							new_event['side'] = side
							new_event['price'] = _str_to_int(event['p'], price_mult)
							new_event['size'] = _str_to_int(event['q'], size_mult)
							new_event['first_id'] = event['f']
							new_event['last_id'] = event['l']
						except Exception as e:
							logging.warning("Parser._parse_binance_perp error parsing {} e: {}".format(event_type, str(e)))
							exception_count += 1
							continue

					elif event_type == 'bookTicker':
						try:
							if event['u'] <= last_bbo_id:
								continue
							last_bbo_id = event['u']

							new_event['type'] = 'bbo'
							new_event['bid_price'] = _str_to_int(event['b'], price_mult)
							new_event['bid_size'] =  _str_to_int(event['B'], size_mult)
							new_event['ask_price'] = _str_to_int(event['a'], price_mult)
							new_event['ask_size'] = _str_to_int(event['A'], size_mult)
							new_event['update_id'] = event['u']
						except Exception as e:
							logging.error("Parser._parse_binance_perp error parsing {} e: {}".format(event_type, str(e)))
							exception_count += 1
							continue

					elif event_type == 'depthUpdate':
						try:
							if channel not in last_depth_update_id:
								last_depth_update_id[channel] = 0
							if event['u'] <= last_depth_update_id[channel]:
								continue
							last_depth_update_id[channel] = event['u']
							# continue
							event['asks'] = []
							for price, size in event['a']:
								event['asks'].append([_str_to_int(price, price_mult), _str_to_int(size, size_mult)])
							del event['a']

							event['bids'] = []
							for price, size in event['b']:
								event['bids'].append([_str_to_int(price, price_mult), _str_to_int(size, size_mult)])
							del event['b']
							new_event['type'] = 'depthUpdate'
							new_event['bids'] = event['bids']
							new_event['asks'] = event['asks']
							new_event['update_id'] = event['u']
							new_event['prev_update_id'] = event.get('pu', 0)
							assert "type" in new_event
						except Exception as e:
							logging.error("Parser._parse_binance_perp error parsing {} e: '{}' channel: {}".format(event_type, str(e), channel))
							exception_count += 1
							continue

					elif event_type == 'forceOrder':
						try:
							new_event['f'] = event['o']['f']
							new_event['type'] = 'forceOrder'
							new_event['side'] = event['o']['S'].lower()
							new_event['o'] = event['o']['o']
							new_event['size'] = event['o']['q']
							new_event['price'] = event['o']['p']
							new_event['aprice'] = event['o']['ap']
							new_event['X'] = event['o']['X']
							new_event['l'] = event['o']['l']
							new_event['z'] = event['o']['z']
							new_event['time'] = int(event['o']['T']) * 10**6
						except Exception as e:
							logging.error("Parser._parse_binance_perp error parsing {} e: {}".format(event_type, str(e)))
							exception_count += 1
							continue

					elif event_type == "markPriceUpdate":
						try:
							new_event["type"] = "fundingInfo"
							new_event["E"] = event["E"]
							new_event["s"] = event["s"]
							new_event["p"] = _str_to_int(event["p"], price_mult)
							new_event["P"] = _str_to_int(event["P"], price_mult)
							new_event["i"] = _str_to_int(event["i"], price_mult)
							new_event["r"] = _str_to_int(event["r"], size_mult)
							new_event["T"] = event["T"]
						except Exception as e:
							logging.error("Parser._parse_binance_perp error parsing {} e: {}".format(event_type, str(e)))
							exception_count += 1
							continue

					else:
						logging.warning("Parser._parse_binance_perp ignore event: {}".format(event))
						ignored_event_count += 1
						continue

				elif 'lastUpdateId' in event:
					try:
						ob = {'bids': dict(), 'asks': dict()}
						for price, size in event['bids']:
							ob['bids'][_str_to_int(price, price_mult)] = _str_to_int(size, size_mult)
						for price, size in event['asks']:
							ob['asks'][_str_to_int(price, price_mult)] = _str_to_int(size, size_mult)
						new_event['type'] = 'snapshot'
						new_event['asks'] = ob['asks']
						new_event['bids'] = ob['bids']
						new_event['update_id'] = event['lastUpdateId']
					except Exception as e:
						logging.error(f"Parser._parse_binance_perp parsing lastUpdateId e: {e}")
						exception_count += 1
						continue

				else:
					logging.warning("Parser._parse_binance_perp ignore row: {}".format(row))
					warning_count += 1
					continue

				if verbose:
					logging.debug(f"Parser.parse add new event: {new_event}")
				events.append(new_event)
			except Exception as e:
				logging.error(
					f"prepare_events_binancefutures e: {e} instrument: {instrument}"
					f"exchange: {exchange} perp now: {now} channel: {channel} event type: {event}.type\nrow: {row}"
				)
				break

		logging.debug(
			"Parser._parse_binance_perp row size: {} event size: {} ignored events: {} warning count: {} exception count: {}".format(
				len(rows), len(events), ignored_event_count, warning_count, exception_count
			)
		)
		return events
