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

import _ast
from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
    QTimer
)
from ninja_ide.gui.editor.checkers import (
    register_checker,
    remove_checker
)
from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.dependencies.pyflakes_mod import checker
from ninja_ide.tools import ui_tools
from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.core.file_handling import file_manager

logger = NinjaLogger(__file__)


class ErrorsChecker(QThread):

    checkerCompleted = pyqtSignal()

    def __init__(self, neditor):
        super().__init__()
        self._neditor = neditor
        self._path = ''
        self.checks = {}

        # self.checker_icon = ui_tools.colored_icon(
        #     ":img/bicho",
        #     resources.get_color('ErrorUnderline')
        # )
        self.checker_icon = None

    def run_checks(self):
        if not self.isRunning():
            self._path = self._neditor.file_path
            QTimer.singleShot(50, self.start)

    def reset(self):
        self.checks.clear()

    def run(self):
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            self.reset()
            source = self._neditor.text
            text = "[PyFlakes] %s"
            # Compile into an AST and handle syntax errors
            try:
                tree = compile(source, self._path, "exec", _ast.PyCF_ONLY_AST)
            except SyntaxError as reason:
                if reason.text is None:
                    logger.error("Syntax error")
                else:
                    self.checks[reason.lineno - 1] = (
                                            text % reason.args[0],
                                            reason.offset - 1)
            else:
                # Okay, now check it
                lint_checker = checker.Checker(tree, self._path)
                lint_checker.messages.sort(key=lambda msg: msg.lineno)
                for message in lint_checker.messages:
                    lineno = message.lineno - 1
                    if lineno not in self.checks:
                        text = [message.message % message.message_args]
                    else:
                        text = self.checks[lineno]
                        text += (message.message % message.message_args,)
                    self.checks[lineno] = (text, message.col)
        self.checkerCompleted.emit()

    def message(self, lineno):
        if lineno in self.checks:
            return self.checks[lineno][0]
        return None

    @property
    def dirty(self):
        return self.checks != {}

    @property
    def dirty_text(self):
        return translations.TR_LINT_DIRTY_TEXT + str(len(self.checks))


def remove_error_checker():
    checker = (
        ErrorsChecker,
        resources.COLOR_SCHEME.get('editor.checker'),
        10
    )
    remove_checker(checker)


if settings.FIND_ERRORS:
    register_checker(
        checker=ErrorsChecker,
        color=resources.COLOR_SCHEME.get("editor.checker"),
        priority=10
    )

"""
import _ast
import re

from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGN            #    resources.get_color('Pep8Underline'), 2)AL

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.editor.checkers import (
    register_checker,
    remove_checker,
)
from ninja_ide.gui.editor.checkers import errors_lists  # lint:ok
from ninja_ide.dependencies.pyflakes_mod import checker


class ErrorsChecker(QThread):

    pat_disable_lint = re.compile('(\s)*#lint:disable$')
    pat_enable_lint = re.compile('(\s)*#lint:enable$')
    pat_ignore_lint = re.compile('(.)+#lint:ok$|(.)+# lint:ok$')

    def __init__(self, editor):
        super(ErrorsChecker, self).__init__()
        self._editor = editor
        self._path = ''
        self._encoding = ''
        self.checks = {}
        self.reporter = None

        self.checker_icon = ":img/bug"

        ninjaide = IDE.get_service('ide')
        self.connect(ninjaide,
                     SIGNAL("ns_preferences_editor_errors(PyQt_PyObject)"),
                     lambda: remove_error_checker())
        self.connect(self, SIGNAL("checkerCompleted()"), self.refresh_display)

    @property
    def dirty(self):
        return self.checks != {}

    @property
    def dirty_text(self):
        return translations.TR_LINT_DIRTY_TEXT + str(len(self.checks))

    def run_checks(self):
        if not self.isRunning():
            self._path = self._editor.file_path
            self._encoding = self._editor.encoding
            self._builtins = self._editor.additional_builtins
            self.start()

    def reset(self):
        self.checks = {}

    def run(self):
        self.sleep(1)
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            try:
                self.reset()
                source = self._editor.text()
                if self._encoding is not None:
                    source = source.encode(self._encoding)
                tree = compile(source, self._path, "exec", _ast.PyCF_ONLY_AST)
                #parseResult = compiler.parse(source)
                lint_checker = checker.Checker(tree, self._path,
                                               builtins=self._builtins)
                for m in lint_checker.messages:
                    lineno = m.lineno - 1
                    if lineno not in self.checks:
                        message = [m.message % m.message_args]
                    else:
                        message = self.checks[lineno]
                        message += [m.message % m.message_args]
                    self.checks[lineno] = message
            except Exception as reason:
                message = ''
                if hasattr(reason, 'msg'):
                    message = reason.msg
                else:
                    message = reason.message

                if hasattr(reason, 'lineno') and reason.lineno:
                    self.checks[reason.lineno - 1] = [message]
                else:
                    self.checks[0] = [message]
            finally:
                ignored_range, ignored_lines = self._get_ignore_range()
                to_remove = [x for x in self.checks
                             for r in ignored_range if r[0] < x < r[1]]
                to_remove += ignored_lines
                for line in to_remove:
                    self.checks.pop(line, None)
        else:
            self.reset()
        self.emit(SIGNAL("checkerCompleted()"))

    def refresh_display(self):
        error_list = IDE.get_service('tab_errors')
        if error_list:
            error_list.refresh_error_list(self.checks)

    def message(self, index):
        if index in self.checks and settings.ERRORS_HIGHLIGHT_LINE:
            return self.checks[index][0]
        return None

    def _get_ignore_range(self):
        ignored_range = []
        ignored_lines = []
        lines = self._editor.lines()
        line = 0
        while line < lines:
            if self.pat_disable_lint.match(self._editor.text(line)):
                start = line
                while line < lines:
                    line += 1
                    if self.pat_enable_lint.match(self._editor.text(line)):
                        end = line
                        ignored_range.append((start, end))
                        break
            elif self.pat_ignore_lint.match(self._editor.text(line)):
                ignored_lines.append(line)
            line += 1

        return (ignored_range, ignored_lines)


def remove_error_checker():
    checker = (ErrorsChecker,
               resources.CUSTOM_SCHEME.get(
                   'ErrorUnderline',
                   resources.COLOR_SCHEME['ErrorUnderline']), 10)
    remove_checker(checker)


if settings.FIND_ERRORS:
    register_checker(checker=ErrorsChecker,
                     color=resources.CUSTOM_SCHEME.get(
                         'ErrorUnderline',
                         resources.COLOR_SCHEME['ErrorUnderline']),
                     priority=10)
"""
