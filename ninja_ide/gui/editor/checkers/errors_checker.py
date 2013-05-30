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

import re
try:
    import compiler
except ImportError:
    print('Errors checker not working in Python3')

from PyQt4.QtCore import QThread

from ninja_ide.core import file_manager
from ninja_ide.core import settings
try:
    from ninja_ide.dependencies.pyflakes_mod import checker
except ImportError:
    print('Errors checker not working in Python3')


class ErrorsChecker(QThread):

    pat_disable_lint = re.compile('(\s)*#lint:disable$')
    pat_enable_lint = re.compile('(\s)*#lint:enable$')
    pat_ignore_lint = re.compile('(.)+#lint:ok$|(.)+# lint:ok$')

    def __init__(self, editor, additional_builtins=[]):
        super(ErrorsChecker, self).__init__()
        self._editor = editor
        self._builtins = additional_builtins
        self._path = ''
        self._encoding = ''
        self.errorsSummary = {}

    def check_errors(self):
        if not self.isRunning():
            self._path = self._editor.ID
            self._encoding = self._editor.encoding
            self.start()

    def reset(self):
        self.errorsSummary = {}

    def run(self):
        self.sleep(1)
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            try:
                self.reset()
                source = self._editor.get_text()
                if self._encoding is not None:
                    source = source.encode(self._encoding)
                parseResult = compiler.parse(source)
                lint_checker = checker.Checker(parseResult, self._path,
                                               builtins=self._builtins)
                for m in lint_checker.messages:
                    lineno = m.lineno - 1
                    if lineno not in self.errorsSummary:
                        message = [m.message % m.message_args]
                    else:
                        message = self.errorsSummary[lineno]
                        message += [m.message % m.message_args]
                    self.errorsSummary[lineno] = message
            except Exception as reason:
                message = ''
                if hasattr(reason, 'msg'):
                    message = reason.msg
                else:
                    message = reason.message

                if hasattr(reason, 'lineno') and reason.lineno:
                    self.errorsSummary[reason.lineno - 1] = [message]
                else:
                    self.errorsSummary[0] = [message]
            finally:
                ignored_range, ignored_lines = self._get_ignore_range()
                to_remove = [x for x in self.errorsSummary
                             for r in ignored_range if r[0] < x < r[1]]
                to_remove += ignored_lines
                for line in to_remove:
                    self.errorsSummary.pop(line, None)
        else:
            self.reset()

    def _get_ignore_range(self):
        ignored_range = []
        ignored_lines = []
        block = self._editor.document().begin()
        while block.isValid():
            if self.pat_disable_lint.match(block.text()):
                start = block.blockNumber()
                while block.isValid():
                    block = block.next()
                    if self.pat_enable_lint.match(block.text()):
                        end = block.blockNumber()
                        ignored_range.append((start, end))
                        break
            elif self.pat_ignore_lint.match(block.text()):
                ignored_lines.append(block.blockNumber())
            block = block.next()

        return (ignored_range, ignored_lines)
