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
import sys
import os
from PyQt5.QtCore import (
    QObject,
    pyqtSignal
)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ninja_ide.intellisensei import jedi
sys.path.pop(0)
jedi.settings.case_insensitive_completion = False


class CodeCompletion(QObject):

    completionsReady = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QObject.__init__(self)
        self.__proposals = []

    @property
    def proposals(self):
        return self.__proposals

    def prepare(self, source, line, offset):
        self._source = source
        self._lineno = line
        self._offset = offset

    def clean_up(self):
        self.__proposals.clear()
        self._source = None
        self._lineno = None
        self._offset = None

    def collect_completions(self):
        try:
            script = jedi.Script(self._source, self._lineno + 1, self._offset)
            completions = script.completions()
        except jedi.NotFoundError:
            completions = []
        for completion in completions:
            self.__proposals.append({
                'type': completion.type,
                'name': completion.name,
                'desc': ' '.join(completion.docstring().split()[:3])
                # 'docstring': completion.docstring().split('\n')
            })
        self.completionsReady.emit(self.__proposals)

    def get_definition(self):
        script = jedi.Script(self._source, self._lineno + 1, self._offset)
        defs = script.goto_definitions()
        print(defs)
