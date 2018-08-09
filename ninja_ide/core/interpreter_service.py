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

import os
import re
import subprocess
import json

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.tools import utils
from ninja_ide.core import settings

logger = NinjaLogger(__name__)

if settings.IS_WINDOWS:
    _PYREGEX = re.compile("/^python(\d+(.\d+)?)?\.exe$/")
else:
    _PYREGEX = re.compile("^python(\d+(.\d+)?)?$")

# TODO: esto debería ser configurable
_VENV_PATHS = [".virtualenvs"]


class InterpreterService(QObject):

    foundInterpreters = pyqtSignal(list)
    currentInterpreterChanged = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.__interpreters = {}
        self.__current_interpreter = None
        self.__locator = _IntepreterLocator()

    def refresh(self):
        self.__interpreters.clear()
        # Search interpreters in background
        self._thread = QThread(self)
        self.__locator.moveToThread(self._thread)
        self._thread.started.connect(self.__locator.load_suggestions)
        self.__locator.finished.connect(self._on_finished)
        self._thread.finished.connect(self._thread.deleteLater)

        QTimer.singleShot(1000, self._thread.start)

    def _on_finished(self, list_of_interpreters):
        for interpreter in list_of_interpreters:
            self.__interpreters[interpreter.exec_path] = interpreter
        self.foundInterpreters.emit(self.get_interpreters())

    @property
    def current(self):
        return self.__current_interpreter

    def set_interpreter(self, path):
        if self.__current_interpreter is None:
            interpreter = Interpreter(path)
            interpreter.version = self.__get_version(path)
            self.__current_interpreter = interpreter
        else:
            interpreter = self.__interpreters.get(path)
            if self.__current_interpreter != interpreter:
                self.__current_interpreter = interpreter
                self.currentInterpreterChanged.emit()
        settings.PYTHON_EXEC = path

    def get_interpreter(self, path):
        return self.__interpreters.get(path)

    def get_interpreters(self):
        return list(self.__interpreters.values())

    def __get_version(self, path):
        return self.__locator.get_info(path)["versionInfo"]

    def load(self):
        self.refresh()
        self.set_interpreter(settings.PYTHON_EXEC)


class Interpreter(object):

    def __init__(self, path):
        self._path = path
        self._venv = None
        self._version = None

    @property
    def path(self):
        return utils.path_with_tilde_homepath(self._path)

    @property
    def exec_path(self):
        return self._path

    @property
    def display_name(self):
        name = "Python {}".format(self.version)
        if self.venv is not None:
            name += " ({})".format(self.venv)
        return name

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = ".".join(map(str, value[:-1]))

    @property
    def venv(self):
        return self._venv

    @venv.setter
    def venv(self, value):
        self._venv = value

    def __str__(self):
        return "Python {} - {}".format(self.version, self.path)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.display_name == other.display_name

    def __hash__(self):
        return hash(
            ("display_name", self.display_name),
        )


class _IntepreterLocator(QObject):

    finished = pyqtSignal(list)

    def __init__(self):
        QObject.__init__(self)
        self._know_paths = []
        if not settings.IS_WINDOWS:
            self._know_paths = [
                "/usr/local/bin", "/usr/bin", "/bin",
                "/usr/sbin", "/sbin", "/usr/local/sbin"
            ]

    @staticmethod
    def get_info(interp_exec):
        string = (
            "import sys\nimport json\ninfo = {}\n"
            "info['versionInfo'] = sys.version_info[:4]\n"
            "info['version'] = sys.version\n"
            "print(json.dumps(info))"
        )
        output = subprocess.check_output([interp_exec, "-c", string])
        return json.loads(output.decode())

    def load_suggestions(self):
        # FIXME: unify this
        interpreters, venvs = [], []
        for venv in _VENV_PATHS:
            venvdir = os.path.join(os.path.expanduser("~"), venv)
            if not os.path.exists(venvdir):
                continue
            subdirs = os.listdir(venvdir)
            for subdir in subdirs:
                if os.path.isdir(os.path.join(venvdir, subdir)):
                    venvpath = os.path.join(venvdir, subdir, "bin")
                    files = os.listdir(venvpath)
                    for f in files:
                        if _PYREGEX.match(f):
                            path = os.path.join(venvpath, f)
                            info = self.get_info(path)
                            interpreter = Interpreter(path)
                            interpreter.version = info["versionInfo"]
                            interpreter.venv = subdir
                            venvs.append(interpreter)

        if self._know_paths:
            for path in self._know_paths:
                if not os.path.exists(path):
                    continue
                files = os.listdir(path)
                for f in files:
                    if _PYREGEX.match(f):
                        python_path = os.path.join(path, f)
                        info = self.get_info(python_path)
                        interpreter = Interpreter(python_path)
                        interpreter.version = info["versionInfo"]
                        interpreters.append(interpreter)
        all_interpreters = list(set(interpreters + venvs))
        self.finished.emit(all_interpreters)
