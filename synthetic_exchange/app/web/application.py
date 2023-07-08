import logging
import os

import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from flask_restful import Api
from waitress import serve

from synthetic_exchange.app.application import Application
from synthetic_exchange.app.web.api.orderbook_endpoint import OrderbookEndpoint
from synthetic_exchange.market import Market


class WebApplication(Application):
    _app_name = "synthetic-exchange"

    def __init__(self, *args, **kwargs):
        templates_dir = os.path.dirname(os.path.realpath(__file__)) + "/templates"
        static_dir = os.path.dirname(os.path.realpath(__file__)) + "/static"
        logging.info(f"{__class__.__name__} templates dir: '{templates_dir}' static: '{static_dir}'")
        self._flask = Flask(__class__._app_name, template_folder=templates_dir, static_folder=static_dir)
        self._api = Api(self._flask)

        app_config = kwargs["application"]
        assert app_config is not None
        self._debug = True if app_config.get("debug", "false") == "true" else False
        self._host = app_config.get("host", "0.0.0.0")
        self._port = app_config.get("port", "8080")
        try:
            self._init_endpoints()
        except Exception as e:
            print(f"{__class__.__name__}.__init__ e: {e}")
        # self._markets = kwargs.get("markets", None)
        self._markets = Market._markets
        Application.__init__(self)

    def _init_endpoints(self):
        print(f"{__class__.__name__}._init_endpoints")
        self._api.add_resource(
            OrderbookEndpoint,
            "/orderbook",
            endpoint="orderbook",
            resource_class_kwargs={
                "post_request_allowed": True,
                "get_request_allowed": True,
            },
        )
        """

        self._api.add_resource(
            TransactionEndpoint,
            "/transactions",
            endpoint="transactions",
            resource_class_kwargs={
                "post_request_allowed": True,
                "get_request_allowed": True,
            },
        )

        self._api.add_resource(
            ChartEndpoint,
            "/chart",
            endpoint="risk",
            resource_class_kwargs={
                "post_request_allowed": True,
                "get_request_allowed": True,
            },
        )
        """

    @property
    def flask(self):
        return self._flask

    def run(self):
        logging.info(f"{__class__.__name__}.run flask STARTING...")

        with self._lock:
            self._run = True

        while True:
            self._lock.acquire()
            if self._run:
                self._lock.release()
                try:
                    # TODO: This is not stoppping after self cleanup, how to stop flask programmatically?
                    # self._flask.before_first_request(None)
                    self._flask.run(host=self._host, port=self._port, threaded=True, debug=self._debug)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logging.error(f"{__class__.__name__}.run e: {e}")
            else:
                self._lock.release()
            with self._lock:
                if not self._run:
                    break
        logging.info(f"{__class__.__name__}.run flask STOPPED!")
