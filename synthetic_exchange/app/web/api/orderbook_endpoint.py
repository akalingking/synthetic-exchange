import asyncio
import logging

import pandas as pd
from flask import make_response, render_template, request
from flask_restful import Resource, reqparse

from synthetic_exchange.market import Market


class OrderbookEndpoint(Resource):
    def __init__(self, **kwargs):
        self.get_request_allowed = kwargs.get("get_request_allowed", False)
        self.post_request_allowed = kwargs.get("post_request_allowed", False)
        self._markets = kwargs.get("markets", None)

    def get(self):
        retval = {"error": "empty"}
        err_msg = None
        try:
            headers = {"Content-Type": "text/html"}
            args = request.args.to_dict()
            logging.debug(f"{__class__.__name__}.get parameters {args}")
            retval_ = self._fetch_ob(**args)
            if all([i in retval_ for i in ["header", "report"]]):
                title = args.get("model", "report").title()
                retval = make_response(
                    render_template("orderbook.html", title=title, header=retval_["header"], data=retval_["orderbook"]),
                    200,
                    headers,
                )
            else:
                retval = make_response(retval_, 200, headers)
        except Exception as e:
            err_msg = f"{e}"
            logging.error(f"{__class__.__name__}.post e: {err_msg}")
            retval = {"error": err_msg}
        logging.debug(f"{__class__.__name__}.post out: {retval}")
        return retval

    def post(self):
        retval = {"error": "empty"}
        try:
            args = request.get_json(force=True)
            err_msg = None
            if "model" not in args:
                err_msg = "missing model"
            if err_msg is not None:
                logging.warning(f"{__class__.__name__}.post {err_msg}")
                return {"error": err_msg}
            logging.debug(f"{__class__.__name__}.post parameters {args}")
            retval = self._fetch_ob(**args)
        except Exception as e:
            err_msg = f"{e}"
            logging.error(f"{__class__.__name__}.post e: {err_msg}")
            retval = {"error": err_msg}
        logging.debug(f"{__class__.__name__}.post out: {retval}")
        return retval

    def _fetch_ob(self, *args, **kwargs) -> dict:
        logging.debug(f"{__class__.__name__}._fetch_ob kwargs: {kwargs}")
        retval = {"error": "empty"}
        err_msg = None
        # df = None
        currency = kwargs.get("currency", None)
        if currency is not None:
            currency = currency.upper()  # Stored in upper case
            print(f">>>{currency} {self._markets}")

            if currency in self._markets:
                market = self._markets[currency]
                if market is not None:
                    ob = market.orderbook()
                    print(f"{__class__.__name__}._fetch_ob ob: {ob}")
            else:
                err_msg = f"No ob for {currency}"
                logging.error(f"{__class__.__name__}._fetch_ob {err_msg}")

        if err_msg is not None:
            logging.error(f"{__class__.__name__}.post {err_msg}")
            retval = {"error": err_msg}

        logging.debug(f"{__class__.__name__}._fetch_report out: {retval}")

        return retval
