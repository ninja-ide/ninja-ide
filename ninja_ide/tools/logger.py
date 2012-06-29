# -*- coding: utf-8 *-*
import logging
import sys


class Logger(object):
    """
        General logger
    """

    def __getattr__(self, name):
        """
            Method missing delegates on self.logger
        """

        def decorator(*args, **kwargs):

            return getattr(self.logger, name)(*args, **kwargs)

        return decorator

    def __init__(self, module):

        self._initialize(module)

    def _initialize(self, module):

        self.logger = logging.getLogger(module)
        self.logger.setLevel(logging.DEBUG)

    def add_handler(self, file, mode, log_format, time_format):

        handler = logging.FileHandler(file, mode)
        formatter = logging.Formatter(log_format, time_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def basicConfig(self):

        logging.basicConfig()

    def debug(self, *a, **k):
        self.logger.debug(*a, **k)

    def info(self, *a, **k):
        self.logger.info(*a, **k)

    def warning(self, *a, **k):
        self.logger.warning(*a, **k)

    def error(self, *a, **k):
        self.logger.error(*a, **k)

    def critical(self, *a, **k):
        self.logger.critical(*a, **k)


class DummyLogger(Logger):

    def debug(self, *a, **k):
        pass

    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass

    def critical(self, *a, **k):
        pass


if not getattr(sys, 'frozen', False):
    NinjaLogger = DummyLogger
else:
    NinjaLogger = Logger

