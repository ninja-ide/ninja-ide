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

from PyQt5.QtCore import (
    QThread,
    QTimer,
    # Qt,
    pyqtSignal
)
from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.dependencies import pycodestyle
from ninja_ide.gui.editor.checkers import (
    register_checker,
    remove_checker,
)
from ninja_ide.tools import ui_tools
# from ninja_ide.gui.editor.checkers import errors_lists  # lint:ok

# TODO: limit results for performance


class Pep8Checker(QThread):
    checkerCompleted = pyqtSignal()

    def __init__(self, editor):
        super(Pep8Checker, self).__init__()
        self._editor = editor
        self._path = ''
        self._encoding = ''
        self.checks = {}

        self.checker_icon = None

        # ninjaide = IDE.get_service('ide')
        # self.connect(ninjaide,
        #             SIGNAL("ns_preferences_editor_checkStyle(PyQt_PyObject)"),
        #             lambda: remove_pep8_checker())
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
            QTimer.singleShot(500, self.start)

    def reset(self):
        self.checks.clear()

    def run(self):
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
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
            # for lineno, offset, code, text, doc in temp_data:
            for lineno, col, code, text in temp_data:
                message = '[PEP8] %s: %s' % (code, text)
                self.checks[lineno - 1] = (message, col)
        self.checkerCompleted.emit()

    def message(self, index):
        if index in self.checks and settings.CHECK_HIGHLIGHT_LINE:
            return self.checks[index]
        return None

    def refresh_display(self):
        # error_list = IDE.get_service('tab_errors')
        # error_tree = IDE.get_service('errors_tree')
        # error_tree.refresh(self.checks, self._path)
        """
        if error_list:
            error_list.refresh_pep8_list(self.checks)
        """


class CustomReport(pycodestyle.StandardReport):

    def get_file_results(self):
        data = []
        for line_number, offset, code, text, doc in self._deferred_print:
            # row = self.line_offset + line_number
            col = offset + 1
            data.append((line_number, col, code, text))
        return data
        # return sorted(self._deferred_print)


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
