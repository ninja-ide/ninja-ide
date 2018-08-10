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

from collections import defaultdict

from PyQt5.QtCore import QThread
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.dependencies import pycodestyle
from ninja_ide.gui.editor.checkers import register_checker
from ninja_ide.gui.editor.checkers import remove_checker
from ninja_ide.gui.editor import helpers
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)


class Pep8Checker(QThread):
    checkerCompleted = pyqtSignal()

    def __init__(self, editor):
        super(Pep8Checker, self).__init__()
        self._editor = editor
        self._path = ''
        self._encoding = ''
        self.checks = defaultdict(list)

        self.checker_icon = None

        self.checkerCompleted.connect(self.refresh_display)

    @property
    def dirty(self):
        return self.checks != {}

    @property
    def dirty_text(self):
        return translations.TR_PEP8_DIRTY_TEXT + str(len(self.checks))

    def run_checks(self):
        if not self.isRunning():
            self._path = self._editor.file_path
            self._encoding = self._editor.encoding
            QTimer.singleShot(0, self.start)

    def reset(self):
        self.checks.clear()

    def run(self):
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            try:
                self.reset()
                source = self._editor.text
                path = self._editor.file_path
                pep8_style = pycodestyle.StyleGuide(
                    parse_argv=False,
                    config_file='',
                    checker_class=CustomChecker
                )
                temp_data = pep8_style.input_file(
                    path,
                    lines=source.splitlines(True)
                )

                source_lines = source.split('\n')
                # for lineno, offset, code, text, doc in temp_data:
                for lineno, col, code, text in temp_data:
                    message = '[PEP8]: %s' % text
                    range_ = helpers.get_range(self._editor, lineno - 1, col)
                    self.checks[lineno - 1].append(
                        (range_, message, source_lines[lineno - 1].strip()))
            except Exception as reason:
                logger.warning("Checker not finished: {}".format(reason))
        self.checkerCompleted.emit()

    def message(self, line):
        if line in self.checks:
            return self.checks[line]
        return None

    def refresh_display(self):
        error_list = IDE.get_service('tab_errors')
        if error_list:
            error_list.refresh_pep8_list(self.checks)


class CustomReport(pycodestyle.StandardReport):

    def get_file_results(self):
        data = []
        for line_number, offset, code, text, doc in self._deferred_print:
            col = offset + 1
            data.append((line_number, col, code, text))
        return data


class CustomChecker(pycodestyle.Checker):

    def __init__(self, *args, **kw):
        super().__init__(*args, report=CustomReport(kw.pop("options")), **kw)


def remove_pep8_checker():
    checker = (Pep8Checker,
               resources.COLOR_SCHEME.get("editor.pep8"), 2)
    remove_checker(checker)


if settings.CHECK_STYLE:
    register_checker(
        checker=Pep8Checker,
        color=resources.COLOR_SCHEME.get("editor.pep8"),
        priority=2
    )
