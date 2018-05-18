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
# from ninja_ide.gui.ide import IDE
from ninja_ide.dependencies import notimportchecker as nic
from ninja_ide.gui.editor.checkers import (
    register_checker,
    remove_checker,
)
from ninja_ide.gui.editor import helpers
# from ninja_ide.tools import ui_tools
# from ninja_ide.gui.editor.checkers import errors_lists  # lint:ok

# TODO: limit results for performance


class NotImporterChecker(QThread):
    checkerCompleted = pyqtSignal()

    def __init__(self, editor):
        super(NotImporterChecker, self).__init__()
        self._editor = editor
        self._path = ''
        self._encoding = ''
        self.checks = defaultdict(list)

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
        return translations.TR_NOT_IMPORT_CHECKER_TEXT + str(len(self.checks))

    def run_checks(self):
        if not self.isRunning():
            self._path = self._editor.file_path
            self._encoding = self._editor.encoding
            QTimer.singleShot(10, self.start)

    def reset(self):
        self.checks.clear()

    def run(self):
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        not_imports = dict()
        if file_ext in exts:
            self.reset()
            # source = self._editor.text
            path = self._editor.file_path
            checker = nic.Checker(path)
            not_imports = checker.get_not_imports_on_file(
                checker.get_imports())
            if not_imports is None:
                pass
            else:
                for key, values in not_imports.items():
                    if isinstance(values['mod_name'], dict):
                        for v in values['mod_name']:
                            message = '[NOTIMP] {}: Dont exist'.format(
                                v)
                    else:
                        message = '[NOTIMP] {}: Dont exist'.format(
                                values['mod_name'])
                    range_ = helpers.get_range(
                        self._editor, values['lineno'] - 1)
                    self.checks[values['lineno'] - 1].append(
                        (range_, message, ""))
        self.checkerCompleted.emit()

    def message(self, index):
        if index in self.checks:
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


def remove_nic_checker():
    checker = (NotImporterChecker,
               resources.COLOR_SCHEME.get("editor.checker"), 2)
    remove_checker(checker)


if settings.FIND_ERRORS:
    register_checker(
        checker=NotImporterChecker,
        color=resources.COLOR_SCHEME.get("editor.checker"),
        priority=2
    )
