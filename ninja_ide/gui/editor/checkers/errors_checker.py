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
from collections import defaultdict

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
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.editor import helpers
from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.core.file_handling import file_manager

logger = NinjaLogger(__file__)


class ErrorsChecker(QThread):

    checkerCompleted = pyqtSignal()

    def __init__(self, neditor):
        super().__init__()
        self._neditor = neditor
        self._path = ''
        self.checks = defaultdict(list)

        self.checker_icon = None
        self.checkerCompleted.connect(self.refresh_display)

    def run_checks(self):
        if not self.isRunning():
            self._path = self._neditor.file_path
            QTimer.singleShot(0, self.start)

    def reset(self):
        self.checks.clear()

    def run(self):
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            try:
                self.reset()
                source = self._neditor.text
                text = "[Error]: %s"
                # Compile into an AST and handle syntax errors
                try:
                    tree = compile(source, self._path, "exec", _ast.PyCF_ONLY_AST)
                except SyntaxError as reason:
                    if reason.text is None:
                        logger.error("Syntax error")
                    else:
                        text = text % reason.args[0]
                        range_ = helpers.get_range(
                            self._neditor, reason.lineno - 1, reason.offset)
                        self.checks[reason.lineno - 1].append((range_, text, ""))
                else:
                    # Okay, now check it
                    lint_checker = checker.Checker(tree, self._path)
                    lint_checker.messages.sort(key=lambda msg: msg.lineno)
                    source_lines = source.split('\n')
                    for message in lint_checker.messages:
                        lineno = message.lineno - 1
                        text = message.message % message.message_args
                        range_ = helpers.get_range(
                            self._neditor, lineno, message.col)
                        self.checks[lineno].append(
                            (range_, text, source_lines[lineno].strip()))
            except Exception as reason:
                logger.warning("Checker not finished: {}".format(reason))

        self.checkerCompleted.emit()

    def message(self, lineno):
        if lineno in self.checks:
            return self.checks[lineno]
        return None

    @property
    def dirty(self):
        return self.checks != {}

    @property
    def dirty_text(self):
        return translations.TR_LINT_DIRTY_TEXT + str(len(self.checks))

    def refresh_display(self):
        error_list = IDE.get_service('tab_errors')
        if error_list:
            error_list.refresh_error_list(self.checks)


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
