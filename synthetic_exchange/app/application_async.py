import asyncio
import json
import logging
import pathlib
import signal
import sys


class ApplicationAsync:
    # def __init__(self, name: str, config_validator: Optional[Callable] = None):
    def __init__(self):
        self.event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        # self.name: str = name
        self.event_loop.set_debug(False)
        try:
            self.event_loop.add_signal_handler(signal.SIGINT, self._signal, signal.SIGINT)
            self.event_loop.add_signal_handler(signal.SIGTERM, self._signal, signal.SIGTERM)
        except NotImplementedError:
            # Signal handlers are only implemented on Unix
            pass
        """
        self.config = None
        config_path = pathlib.Path(name + ".json")
        if config_path.exists():
            with config_path.open("r") as config:
                self.config = json.load(config)
            if config_validator is not None and not config_validator(self.config):
                raise Exception("configuration failed validation: %s" % config_path.resolve())
        elif config_validator is not None:
            raise Exception("configuration file does not exist: %s" % str(config_path))

        logging.info("%s started with arguments={%s}", self.name, ", ".join(sys.argv))
        if self.config is not None:
            self.logger.info("configuration=%s", json.dumps(self.config, separators=(',', ':')))
        """

    def _signal(self, signum: int) -> None:
        sig_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        logging.info("%s signal received - shutting down...", sig_name)
        self.event_loop.stop()

    def run(self) -> None:
        loop = self.event_loop
        try:
            loop.run_forever()
        except Exception as e:
            logging.error("application raised an exception:", exc_info=e)
            raise
        finally:
            self.logger.info("closing event loop")
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                loop.close()
