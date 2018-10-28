# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.


import logging
from ninja_ide import resources


LOG_FORMAT = "[%(asctime)s] %(name)s:%(funcName)-4s %(levelname)-8s %(message)s"
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Logger(object):
    """
        General logger
    """

    def __init__(self):
        self._loggers = {}
        self._default_level = logging.NOTSET
        self._handler = None
        logging.basicConfig(format=LOG_FORMAT)

    def __call__(self, modname):
        if not self._handler:
            self.add_handler(
                resources.LOG_FILE_PATH, 'w', LOG_FORMAT, TIME_FORMAT)
        if modname not in self._loggers:
            logger = logging.getLogger(modname)
            self._loggers[modname] = logger
            logger.setLevel(self._default_level)
            logger.addHandler(self._handler)

        return self._loggers[modname]

    def dissable(self):
        for each_log in list(self._loggers.values()):
            each_log.setLevel(logging.NOTSET)

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
            if log_level in ('debug', 'info', 'warning', 'error', 'critical'):
                log_level = getattr(logging, log_level.upper())
                self.setLevel(log_level)


NinjaLogger = Logger()
