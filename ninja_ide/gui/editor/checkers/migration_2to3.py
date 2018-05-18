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

import os
import subprocess

from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.editor.checkers import (
    register_checker,
    remove_checker,
)
from ninja_ide.gui.editor.checkers import migration_lists  # lint:ok


class MigrationTo3(QThread):

    def __init__(self, editor):
        super(MigrationTo3, self).__init__()
        self._editor = editor
        self._path = ''
        self.dirty = False
        self.checks = {}
        if settings.IS_WINDOWS and settings.PYTHON_EXEC_CONFIGURED_BY_USER:
            tool_path = os.path.join(os.path.dirname(settings.PYTHON_EXEC),
                                     'Tools', 'Scripts', '2to3.py')
            self._command = [settings.PYTHON_EXEC, tool_path]
        else:
            self._command = ['2to3']

        self.checker_icon = None

        ninjaide = IDE.get_service('ide')
        self.connect(
            ninjaide,
            SIGNAL("ns_preferences_editor_showMigrationTips(PyQt_PyObject)"),
            lambda: remove_migration_checker())
        self.connect(self, SIGNAL("checkerCompleted()"), self.refresh_display)

    def run_checks(self):
        if not self.isRunning() and settings.VALID_2TO3:
            self._path = self._editor.file_path
            self.start()

    def run(self):
        self.sleep(1)
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._path)
        if file_ext in exts:
            self.checks = {}
            lineno = 0
            lines_to_remove = []
            lines_to_add = []
            parsing_adds = False
            try:
                output = subprocess.check_output(self._command + [self._path])
                output = output.decode('utf-8').split('\n')
            except OSError:
                settings.VALID_2TO3 = False
                return
            for line in output[2:]:
                if line.startswith('+'):
                    lines_to_add.append(line)
                    parsing_adds = True
                    continue

                if parsing_adds:
                    # Add in migration
                    removes = '\n'.join([liner
                                        for _, liner in lines_to_remove])
                    adds = '\n'.join(lines_to_add)
                    message = self.tr(
                        'The actual code looks like this:\n%s\n\n'
                        'For Python3 support, it should look like:\n%s' %
                        (removes, adds))
                    lineno = -1
                    for nro, _ in lines_to_remove:
                        if lineno == -1:
                            lineno = nro
                        self.checks[nro] = (message, lineno, "")
                    parsing_adds = False
                    lines_to_add = []
                    lines_to_remove = []

                if line.startswith('-'):
                    lines_to_remove.append((lineno, line))
                lineno += 1

                if line.startswith('@@'):
                    lineno = int(line[line.index('-') + 1:line.index(',')]) - 1
            self.emit(SIGNAL("checkerCompleted()"))

    def refresh_display(self):
        tab_migration = IDE.get_service('tab_migration')
        if tab_migration:
            tab_migration.refresh_lists(self.checks)

    def message(self, index):
        if index in self.checks:
            return self.checks[index][0]
        return None


def remove_migration_checker():
    checker = (MigrationTo3,
               resources.CUSTOM_SCHEME.get(
                   'MigrationUnderline',
                   resources.COLOR_SCHEME['MigrationUnderline']), 1)
    remove_checker(checker)


if settings.SHOW_MIGRATION_TIPS:
    register_checker(checker=MigrationTo3,
                     color=resources.CUSTOM_SCHEME.get(
                         'MigrationUnderline',
                         resources.COLOR_SCHEME['MigrationUnderline']))
