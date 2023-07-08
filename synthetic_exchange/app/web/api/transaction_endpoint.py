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
            logging.info(f"{__class__.__name__}.get parameters {args}")
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
        logging.info(f"{__class__.__name__}.post out: {retval}")
        return retval

    def post(self):
        retval = {"error": "empty"}
        try:
            # Gather parameters
            args = request.get_json(force=True)
            err_msg = None
            if "model" not in args:
                err_msg = "missing model"
            if err_msg is not None:
                logging.warning(f"{__class__.__name__}.post {err_msg}")
                return {"error": err_msg}
            logging.info(f"{__class__.__name__}.post parameters {args}")
            retval = self._fetch_ob(**args)
        except Exception as e:
            err_msg = f"{e}"
            logging.error(f"{__class__.__name__}.post e: {err_msg}")
            retval = {"error": err_msg}
        logging.info(f"{__class__.__name__}.post out: {retval}")
        return retval

    def _fetch_ob(self, symbol: str) -> dict:
        logging.info(f"{__class__.__name__}._fetch_ob symbol: {symbol}")
        retval = {"error": "empty"}
        # err_msg = None
        # df = None
        if symbol is not None:
            symbol = symbol.upper()  # Stored in upper case

        """

        if model is not None:
            if model == "benford":
                report = list(self._benford_reports)
                df = pd.DataFrame(report, columns=report_headers[model])
            elif model.lower() == "cluster":
                report = list(self._cluster_reports)
                df = pd.DataFrame(report, columns=report_headers[model])
            elif model.lower() == "powerlaw":
                report = list(self._powerlaw_reports)
                df = pd.DataFrame(report, columns=report_headers[model])
            else:
                logging.error(f"{__class__.__name__}.post invalid model: {model}")

            if df is not None and len(df) > 0:
                if exchange is not None:
                    df_ = df[df["Exchange"] == exchange]
                    if len(df_) > 0:
                        if currency is not None:
                            df__ = df_[df_["Currency"] == currency]
                            if len(df__) > 0:
                                df = df__
                                retval = {"header": report_headers[model], "report": df.values.tolist()}
                            else:
                                currencies = df_["Currency"].unique()
                                err_msg = f"invalid currency: {currency}, available: {currencies}"
                                logging.error(f"{__class__.__name__}_fetch_report {err_msg}")
                        else:
                            retval = {"header": report_headers[model], "report": df_.values.tolist()}
                    else:
                        exchanges = df["Exchange"].unique()
                        err_msg = f"invalid exchange: {exchange}, available: {exchanges}"
                        logging.error(f"{__class__.__name__}_fetch_report {err_msg}")
                else:
                    retval = {"header": report_headers[model], "report": df.values.tolist()}
            else:
                err_msg = f"No record for {model}"
        else:
            # Take all reports
            if exchange is not None:
                benford = list(self._benford_reports)
                benford_df = pd.DataFrame(benford, columns=report_headers["benford"]).drop(
                    columns=[
                        "Stat",
                    ],
                    axis=1,
                )
                benford_df_ = benford_df[benford_df["Exchange"] == exchange]
                if currency is not None:
                    benford_df_ = benford_df_[benford_df_["Currency"] == currency]

                cluster = list(self._cluster_reports)
                cluster_df = pd.DataFrame(cluster, columns=report_headers["cluster"]).drop(
                    columns=["T-stat", "Crit-val"], axis=1
                )
                cluster_df_ = cluster_df[cluster_df["Exchange"] == exchange]
                if currency is not None:
                    cluster_df_ = cluster_df_[cluster_df_["Currency"] == currency]

                powerlaw = list(self._powerlaw_reports)
                powerlaw_df = pd.DataFrame(powerlaw, columns=report_headers["powerlaw"]).drop(
                    columns=["Statistic"], axis=1
                )
                powerlaw_df_ = powerlaw_df[powerlaw_df["Exchange"] == exchange]
                if currency is not None:
                    powerlaw_df_ = powerlaw_df_[powerlaw_df_["Currency"] == currency]

                df = pd.concat([benford_df_, cluster_df_, powerlaw_df_])

                retval = {"header": report_headers["all"], "report": df.values.tolist()}

        if err_msg is not None:
            logging.error(f"{__class__.__name__}.post {err_msg}")
            retval = {"error": err_msg}

        logging.info(f"{__class__.__name__}._fetch_report out: {retval}")
        """

        return retval
