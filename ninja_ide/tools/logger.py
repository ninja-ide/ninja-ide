# -*- coding: utf-8 *-*
import logging
import sys
from ninja_ide import resources


NOLOG = 100
LOG_FORMAT = "%(asctime)s %(name)s:%(lineno)-4d %(levelname)-8s %(message)s"
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Logger(object):
    """
        General logger
    """

    def __init__(self):
        self._loggers = {}
        self._default_level = NOLOG
        self._handler = None
        logging.basicConfig()
        super(Logger, self).__init__()

    def __call__(self, modname):
        if not self._handler:
            self.add_handler(resources.LOG_FILE_PATH, 'w', LOG_FORMAT,
                             TIME_FORMAT)
        if modname not in self._loggers:
            logger = logging.getLogger(modname)
            self._loggers[modname] = logger
            logger.setLevel(self._default_level)
            logger.addHandler(self._handler)

        return self._loggers[modname]

    def dissable(self):
        for each_log in list(self._loggers.values()):
            each_log.setLevel(NOLOG)

    def setLevel(self, level):
        self._default_level = level
        for each_log in list(self._loggers.values()):
            each_log.setLevel(level)

    def add_handler(self, hfile, mode, log_format, time_format, stream=None):
        formatter = logging.Formatter(log_format, time_format)
        if stream:
            handler = logging.StreamHandler(hfile)
        else:
            handler = logging.FileHandler(hfile, mode)
        handler.setFormatter(formatter)
        for each_log in list(self._loggers.values()):
            each_log.addHandler(handler)
        self._handler = handler

    def argparse(self, log_level, log_file):
        if log_level:
            if log_level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
                log_level = getattr(logging, log_level)
                self.setLevel(log_level)
        if log_file:
            if log_file == "STDOUT":
                self.add_handler(sys.stdout, None, LOG_FORMAT, TIME_FORMAT,
                                    True)
            if log_file == "STDERR":
                self.add_handler(sys.stdout, None, LOG_FORMAT, TIME_FORMAT,
                                    True)
            else:
                self.add_handler(log_file, 'w', LOG_FORMAT,
                                TIME_FORMAT)


NinjaLogger = Logger()
