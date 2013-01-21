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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QTextCursor
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.main_panel import main_container


class MigrationWidget(QWidget):

    def __init__(self):
        super(MigrationWidget, self).__init__()
        self._migration = {}
        vbox = QVBoxLayout(self)
        lbl_title = QLabel(self.tr("Current code:"))
        self.current_list = QListWidget()
        lbl_suggestion = QLabel(self.tr("Suggested changes:"))
        self.suggestion = QPlainTextEdit()
        self.suggestion.setReadOnly(True)

        self.btn_apply = QPushButton(self.tr("Apply change!"))
        hbox = QHBoxLayout()
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox.addWidget(self.btn_apply)

        vbox.addWidget(lbl_title)
        vbox.addWidget(self.current_list)
        vbox.addWidget(lbl_suggestion)
        vbox.addWidget(self.suggestion)
        vbox.addLayout(hbox)

        self.connect(self.current_list,
            SIGNAL("itemClicked(QListWidgetItem*)"), self.load_suggestion)
        self.connect(self.btn_apply, SIGNAL("clicked()"), self.apply_changes)

    def apply_changes(self):
        lineno = int(self.current_list.currentItem().data(Qt.UserRole))
        lines = self._migration.migration_data[lineno][0].split('\n')
        remove = -1
        code = ''
        for line in lines:
            if line.startswith('-'):
                remove += 1
            elif line.startswith('+'):
                code += '%s\n' % line[1:]

        editorWidget = main_container.MainContainer().get_actual_editor()
        block_start = editorWidget.document().findBlockByLineNumber(lineno)
        block_end = editorWidget.document().findBlockByLineNumber(
            lineno + remove)
        cursor = editorWidget.textCursor()
        cursor.setPosition(block_start.position())
        cursor.setPosition(block_end.position(), QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.insertText(code[:-1])

    def load_suggestion(self, item):
        lineno = int(item.data(Qt.UserRole))
        lines = self._migration.migration_data[lineno][0].split('\n')
        code = ''
        for line in lines:
            if line.startswith('+'):
                code += '%s\n' % line[1:]
        self.suggestion.setPlainText(code)
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.jump_to_line(lineno)
            editorWidget.setFocus()

    def refresh_lists(self, migration):
        self._migration = migration
        self.current_list.clear()
        base_lineno = -1
        for lineno in sorted(migration.migration_data.keys()):
            linenostr = 'L%s\n' % str(lineno + 1)
            data = migration.migration_data[lineno]
            lines = data[0].split('\n')
            if base_lineno == data[1]:
                continue
            base_lineno = data[1]
            message = ''
            for line in lines:
                if line.startswith('-'):
                    message += '%s\n' % line
            item = QListWidgetItem(linenostr + message)
            item.setToolTip(linenostr + message)
            item.setData(Qt.UserRole, lineno)
            self.current_list.addItem(item)

    def clear(self):
        """
        Clear the widget
        """
        self.current_list.clear()
        self.suggestion.clear()
