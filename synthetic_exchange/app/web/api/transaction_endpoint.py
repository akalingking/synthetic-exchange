import asyncio
import logging
import pandas as pd
from flask import make_response, render_template, request
from flask_restful import Resource, reqparse
from synthetic_exchange.market import Market


class TransactionEndpoint(Resource):
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

    def _fetch_ob(self, symbol: str) -> dict:
        logging.debug(f"{__class__.__name__}._fetch_ob symbol: {symbol}")
        retval = {"error": "empty"}
        # err_msg = None
        # df = None
        if symbol is not None:
            symbol = symbol.upper()  # Stored in upper case

        return retval
