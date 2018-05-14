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

from collections import Callable

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QRunnable
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

from ninja_ide.gui.ide import IDE
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)


class Signals(QObject):

    finished = pyqtSignal()
    ready = pyqtSignal("PyQt_PyObject")
    error = pyqtSignal("PyQt_PyObject")


class Worker(QRunnable):

    def __init__(self, runnable, *args, **kwargs):
        QRunnable.__init__(self)
        self.signals = Signals()
        self.__runnable = runnable
        self.__args = args
        self.__kwargs = kwargs

    @pyqtSlot()
    def run(self):
        try:
            result = self.__runnable(*self.__args, **self.__kwargs)
        except Exception as reason:
            logger.error("Error occurred: '%s'" % str(reason))
            self.signals.error.emit(reason)
        else:
            self.signals.ready.emit(result)
        finally:
            self.signals.finished.emit()


class IntelliSense(QObject):

    resultAvailable = pyqtSignal("PyQt_PyObject", "QString")

    def __init__(self):
        QObject.__init__(self)
        self.__services = {}
        self.__thread = QThreadPool()
        self._main_container = IDE.get_service("main_container")

        IDE.register_service("intellisense", self)

    def services(self):
        return self.__services.keys()

    def _code_info(self, editor):
        # word = editor.word_under_cursor(ignore=("(", ")", ".")).selectedText()
        line, col = editor.cursor_position
        # if not word:
        return {
            "source": editor.text,
            "line": line + 1,
            "column": col,
            "path": editor.file_path,
        }

    def get(self, operation, editor):
        """Handle request"""
        func_name = "get_" + operation
        language = editor.neditable.language()
        service = self.__services.get(language)
        if service is None:
            logger.warning("No IntelliSense service for '{}'".format(language))
            return
        code_info = self._code_info(editor)
        setattr(service, "_code_info", code_info)
        self._start_time = time.time()
        func = getattr(service, func_name, None)
        if isinstance(func, Callable):
            worker = Worker(func)
            worker.signals.ready.connect(
                lambda r: self._on_ready(r, operation))
            worker.signals.error.connect(self._on_error)
            worker.signals.finished.connect(self._on_finished)
            self.__thread.start(worker)

    @pyqtSlot()
    def _on_finished(self):
        logger.debug("Worker finished")

    @pyqtSlot("PyQt_PyObject", "QString")
    def _on_ready(self, result, operation):
        logger.debug("Worker finalize in %.1f" % (
            time.time() - self._start_time))
        self.resultAvailable.emit(result, operation)

    @pyqtSlot("PyQt_PyObject")
    def _on_error(self, error):
        logger.error("Error ocurred '{}'".format(error))

    def register_service(self, service):
        self.__services[service.language] = service()


class IntelliSenseService(QObject):

    """
    Any IntelliSense Service defined should inherit from this
    The only mandatory method is get_completions.
    Also, you should specify the language.
    """

    language = "python"  # Python is our priority

    def __init__(self):
        QObject.__init__(self)

    @classmethod
    def register(cls):
        intellisense = IDE.get_service("intellisense")
        intellisense.register_service(cls)

    def get_definitions(self):
        """
        Here we expect you to return a list of dicts.
        {
            "text": definition name,
            "filename": definition path,
            "line": line number,
            "column": column number
        }
        """

    def get_signatures(self):
        """Here we expect you to return a list of dicts.
        {
            "signature.name": name,
            "signature.params": list of signature params,
            "signature.index": index
        }
        """

    def get_completions(self):
        """
        Here we expect you to return a list of dicts.

        The dict must have the following structure:
        {
            "text": completion_name,
            "type": completion_type,
            "detail": detail, description of completion
        }
        >>> completions = []
        >>> c1 = {"text": "capitalize", "type": "function"}
        >>> c2 = {"text": "casefold", "type": "function"}
        >>> completions.append(c1)
        >>> completions.append(c2)

        """
        raise NotImplementedError("You should implement this")


# Register service
IntelliSense()
