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
from __future__ import absolute_import
from __future__ import unicode_literals

from PyQt4.QtCore import QThread

from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide.dependencies import pep8mod


class Pep8Checker(QThread):

    def __init__(self, editor):
        QThread.__init__(self)
        self._editor = editor
        self._path = ''
        self._encoding = ''
        self.pep8checks = {}

    def check_style(self):
        if not self.isRunning():
            self._path = self._editor.ID
            self._encoding = self._editor.encoding
            self.start()

    def reset(self):
        self.pep8checks = {}

    def run(self):
        self.sleep(1)
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            self.reset()
            source = self._editor.get_text()
            tempData = pep8mod.run_check(self._path, source)
            i = 0
            while i < len(tempData):
                lineno = -1
                try:
                    offset = 2 + len(file_ext)
                    startPos = tempData[i].find('.%s:' % file_ext) + offset
                    endPos = tempData[i].find(':', startPos)
                    lineno = int(tempData[i][startPos:endPos]) - 1
                    error = tempData[i][tempData[i].find(
                        ':', endPos + 1) + 2:]
                    line = '\n'.join(
                        [error, tempData[i + 1], tempData[i + 2]])
                except Exception:
                    line = ''
                finally:
                    i += 3
                if line and lineno > -1:
                    if lineno not in self.pep8checks:
                        self.pep8checks[lineno] = [line]
                    else:
                        message = self.pep8checks[lineno]
                        message += [line]
                        self.pep8checks[lineno] = message
        else:
            self.reset()
