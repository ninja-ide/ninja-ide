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

from PyQt4.QtGui import QStyle
from PyQt4.QtCore import QThread

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.dependencies import pep8mod
from ninja_ide.gui.editor.checkers import (
    register_checker,
    remove_checker,
)
from ninja_ide.gui.editor.checkers import errors_lists  # lint:ok


class Pep8Checker(QThread):

    def __init__(self, editor):
        QThread.__init__(self)
        self._editor = editor
        self._path = ''
        self._encoding = ''
        self.checks = {}

        self.checker_icon = QStyle.SP_MessageBoxWarning

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
            self.start()

    def reset(self):
        self.checks = {}

    def run(self):
        self.sleep(1)
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            self.reset()
            source = self._editor.get_text()
            tempData = pep8mod.run_check(self._path, source)
            for result in tempData:
                message = "\n".join(("%s %s" % (result["code"], result["text"]),
                           result["line"],
                           result["pointer"]))
                if result["line_number"] not in self.checks:
                    self.checks[result["line_number"]] = [message]
                else:
                    original = self.checks[result["line_number"]]
                    original += [message]
                    self.checks[result["line_number"]] = original
        else:
            self.reset()
        self.refresh_display()

    def message(self, index):
        if index in self.checks and settings.CHECK_HIGHLIGHT_LINE:
            return self.checks[index][0]
        return None

    def refresh_display(self):
        error_list = IDE.get_service('tab_errors')
        if error_list:
            error_list.refresh_pep8_list(self.checks)


def remove_pep8_checker():
    _default_color = resources.COLOR_SCHEME['pep8-underline']
    checker = (Pep8Checker,
               resources.CUSTOM_SCHEME.get('pep8-underline', _default_color), 2)
    remove_checker(checker)


if settings.CHECK_STYLE:
    register_checker(checker=Pep8Checker,
        color=resources.CUSTOM_SCHEME.get('pep8-underline',
        resources.COLOR_SCHEME['pep8-underline']), priority=2)