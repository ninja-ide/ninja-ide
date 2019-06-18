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

from PyQt5.QtCore import QThread
from PyQt5.QtCore import QTimer

from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide.dependencies import pycodestylemod


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
            QTimer.singleShot(1000, self.start)
            # self.start()

    def reset(self):
        self.pep8checks = {}

    def run(self):
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            try:
                self.reset()
                source = self._editor.get_text()
                pep8_style = pycodestylemod.StyleGuide(parse_argv=False, config_file='', checker_class=CustomChecker)
                temp_data = pep8_style.input_file(self._path, lines=source.splitlines(True))
                # source_lines = source.split('\n')
                for line, col, code, text in temp_data:
                    message = '[PEP8]: %s' % text
                    self.pep8checks[line - 1] = [message]
                    # print(source_lines[line - 1])
            except Exception as reason:
                print("Checker not finished: {}".format(reason))
            # self.reset()
            # source = self._editor.get_text()
            # # tempData = pycodestylemod.run_check(self._path, source)
            # pep8 = pycodestylemod.StyleGuide(parse_argv=False, config_file='')
            # tempData = pep8.input_file(self._path, lines=source.splitlines(True))
            # i = 0
            # while i < len(tempData):
            #     lineno = -1
            #     try:
            #         offset = 2 + len(file_ext)
            #         startPos = tempData[i].find('.%s:' % file_ext) + offset
            #         endPos = tempData[i].find(':', startPos)
            #         lineno = int(tempData[i][startPos:endPos]) - 1
            #         error = tempData[i][tempData[i].find(
            #             ':', endPos + 1) + 2:]
            #         line = '\n'.join(
            #             [error, tempData[i + 1], tempData[i + 2]])
            #     except Exception:
            #         line = ''
            #     finally:
            #         i += 3
            #     if line and lineno > -1:
            #         if lineno not in self.pep8checks:
            #             self.pep8checks[lineno] = [line]
            #         else:
            #             message = self.pep8checks[lineno]
            #             message += [line]
            #             self.pep8checks[lineno] = message
        else:
            self.reset()


class CustomReport(pycodestylemod.StandardReport):

    def get_file_results(self):
        data = []
        for line_number, offset, code, text, doc in self._deferred_print:
            col = offset + 1
            data.append((line_number, col, code, text))
        return data


class CustomChecker(pycodestylemod.Checker):

    def __init__(self, *args, **kw):
        super().__init__(*args, report=CustomReport(kw.pop("options")), **kw)
