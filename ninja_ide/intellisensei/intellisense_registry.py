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

import time
import abc
from collections import namedtuple
from collections import Callable

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

from ninja_ide.gui.ide import IDE
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)

CodeInfo = namedtuple("CodeInfo", "pservice source line col path")


class IntelliSenseWorker(QThread):

    workerFailed = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.__result = None

    def request(self, runnable, *args, **kwargs):
        self.__runnable = runnable
        self.__args = args
        self.__kwargs = kwargs
        self.start()

    @property
    def result(self):
        return self.__result

    def run(self):
        try:
            self.__result = self.__runnable(*self.__args, **self.__kwargs)
        except Exception as reason:
            self.workerFailed.emit(str(reason))


class IntelliSense(QObject):

    resultAvailable = pyqtSignal("PyQt_PyObject")

    services = ("completions", "calltips")

    def __init__(self):
        QObject.__init__(self)
        self.__providers = {}
        self.__thread = None
        # self._main_container = IDE.get_service("main_container")

        # Register service
        IDE.register_service("intellisense", self)

    def providers(self):
        return self.__providers.keys()

    def register_provider(self, provider):
        provider_object = provider()
        self.__providers[provider.language] = provider_object
        provider_object.load()

    def provider(self, language):
        return self.__providers.get(language)

    def _code_info(self, editor, kind):
        line, col = editor.cursor_position
        return CodeInfo(
            kind,
            editor.text,
            line + 1,
            col,
            editor.file_path
        )

    def process(self, kind, neditor):
        """Handle request from IntelliSense Assistant"""
        if self.__thread is not None:
            if self.__thread.isRunning():
                logger.debug("Waiting...")
                return
        code_info = self._code_info(neditor, kind)
        logger.debug("Running '{}'".format(code_info.pservice))
        provider = self.__providers.get(neditor.neditable.language())
        setattr(provider, "_code_info", code_info)
        provider_service = getattr(provider, kind, None)
        if isinstance(provider_service, Callable):
            self.__thread = IntelliSenseWorker(self)
            self.__thread.finished.connect(self._on_worker_finished)
            self.__thread.finished.connect(self.__thread.deleteLater)
            self.__thread.request(provider_service)

    def _on_worker_finished(self):
        if self.__thread is None:
            return
        result = self.__thread.result
        self.__thread = None
        self.resultAvailable.emit(result)

    def provider_services(self, language):
        """Returns the services available for a provider"""

        return [service for service in dir(self.provider(language))
                if service in IntelliSense.services]


class Provider(abc.ABC):
    """
    Any IntelliSense Provider defined should inherit from this class
    The only mandatory method is Provider.completions.
    """

    language = "python"
    triggers = ["."]  # FIXME: only works with one char

    @classmethod
    def register(cls):
        """Register this provider in the IntelliSense service"""

        intellisense = IDE.get_service("intellisense")
        intellisense.register_provider(cls)

    def load(self):
        """This will load things before it is used."""
        pass

    @abc.abstractmethod
    def completions(self):
        """
        Here we expect you to return a list of dicts.

        The dict must have the following structure:
        {
            "text": "completion_name",
            "type": "completion_type",
            "detail": "completion_detail"
        }
        The "text" key is the text that will be displayed in the list.
        The "type" key can be: function, class, instance.
        The "detail" key is a text that will be displayed next to the list
        as a tool tip.
        """

    def calltips(self):
        pass


# Register service
IntelliSense()
