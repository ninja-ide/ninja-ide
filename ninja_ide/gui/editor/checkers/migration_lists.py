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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer


class MigrationWidget(QDialog):
    """2to3 Migration Assistance Widget Class"""

    def __init__(self, parent=None):
        super(MigrationWidget, self).__init__(parent, Qt.WindowStaysOnTopHint)
        self._migration, vbox, hbox = {}, QVBoxLayout(self), QHBoxLayout()
        lbl_title = QLabel(translations.TR_CURRENT_CODE)
        lbl_suggestion = QLabel(translations.TR_SUGGESTED_CHANGES)
        self.current_list, self.suggestion = QListWidget(), QPlainTextEdit()
        self.suggestion.setReadOnly(True)
        self.btn_apply = QPushButton(translations.TR_APPLY_CHANGES + " !")
        self.suggestion.setToolTip(translations.TR_SAVE_BEFORE_APPLY + " !")
        self.btn_apply.setToolTip(translations.TR_SAVE_BEFORE_APPLY + " !")
        # pack up all widgets
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox.addWidget(self.btn_apply)
        vbox.addWidget(lbl_title)
        vbox.addWidget(self.current_list)
        vbox.addWidget(lbl_suggestion)
        vbox.addWidget(self.suggestion)
        vbox.addLayout(hbox)
        # connections
        self.connect(
            self.current_list, SIGNAL("itemClicked(QListWidgetItem*)"),
            self.load_suggestion)
        self.connect(self.btn_apply, SIGNAL("clicked()"), self.apply_changes)
        # registers
        IDE.register_service('tab_migration', self)
        ExplorerContainer.register_tab(translations.TR_TAB_MIGRATION, self)

    def install_tab(self):
        """Install the Tab on the IDE."""
        ide = IDE.get_service('ide')
        self.connect(ide, SIGNAL("goingDown()"), self.close)

    def apply_changes(self):
        """Apply the suggested changes on the Python code."""
        lineno = int(self.current_list.currentItem().data(Qt.UserRole))
        lines = self._migration[lineno][0].split('\n')
        remove, code = -1, ""
        for line in lines:
            if line.startswith('-'):
                remove += 1  # line to remove
            elif line.startswith('+'):
                code += '{line_to_add}\n'.format(line_to_add=line[1:])
        # get and apply changes on editor
        main_container = IDE.get_service('main_container')
        if main_container:
            editorWidget = main_container.get_current_editor()
            position = editorWidget.SendScintilla(
                editorWidget.SCI_POSITIONFROMLINE, lineno)
            curpos = editorWidget.SendScintilla(editorWidget.SCI_GETCURRENTPOS)
            if curpos != position:
                editorWidget.SendScintilla(editorWidget.SCI_GOTOPOS, position)
            endpos = editorWidget.SendScintilla(
                editorWidget.SCI_GETLINEENDPOSITION, lineno)
            editorWidget.SendScintilla(editorWidget.SCI_SETCURRENTPOS, endpos)
            editorWidget.replaceSelectedText(code[:-1])

    def load_suggestion(self, item):
        """Take an argument item and load the suggestion."""
        lineno, code = int(item.data(Qt.UserRole)), ""
        lines = self._migration[lineno][0].split('\n')
        for line in lines:
            if line.startswith('+'):
                code += '{line_to_add}\n'.format(line_to_add=line[1:])
        self.suggestion.setPlainText(code)
        main_container = IDE.get_service('main_container')
        if main_container:
            editorWidget = main_container.get_current_editor()
            if editorWidget:
                editorWidget.jump_to_line(lineno)
                editorWidget.setFocus()

    def refresh_lists(self, migration):
        """Refresh the list of code suggestions."""
        self._migration, base_lineno = migration, -1
        self.current_list.clear()
        for lineno in sorted(migration.keys()):
            linenostr = 'L{line_number}\n'.format(line_number=str(lineno + 1))
            data = migration[lineno]
            lines = data[0].split('\n')
            if base_lineno == data[1]:
                continue
            base_lineno = data[1]
            message = ''
            for line in lines:
                if line.startswith('-'):
                    message += '{line_to_load}\n'.format(line_to_load=line)
            item = QListWidgetItem(linenostr + message)
            item.setToolTip(linenostr + message)
            item.setData(Qt.UserRole, lineno)
            self.current_list.addItem(item)

    def clear(self):
        """Clear the widget."""
        self.current_list.clear()
        self.suggestion.clear()

    def reject(self):
        """Reject"""
        if self.parent() is None:
            self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)

    def closeEvent(self, event):
        """Close"""
        self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)
        event.ignore()


migrationWidget = MigrationWidget() if settings.SHOW_MIGRATION_LIST else None
