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
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide.core import settings
from ninja_ide.gui.main_panel import main_container


class ErrorsWidget(QWidget):

###############################################################################
# ERRORS WIDGET SIGNALS
###############################################################################
    """
    pep8Activated(bool)
    lintActivated(bool)
    """
###############################################################################

    def __init__(self):
        QWidget.__init__(self)
        self.pep8 = None
        self._outRefresh = True

        vbox = QVBoxLayout(self)
        self.listErrors = QListWidget()
        self.listErrors.setSortingEnabled(True)
        self.listPep8 = QListWidget()
        self.listPep8.setSortingEnabled(True)
        hbox_lint = QHBoxLayout()
        if settings.FIND_ERRORS:
            self.btn_lint_activate = QPushButton(self.tr("Lint: ON"))
        else:
            self.btn_lint_activate = QPushButton(self.tr("Lint: OFF"))
        self.errorsLabel = QLabel(self.tr("Static Errors: %s") % 0)
        hbox_lint.addWidget(self.errorsLabel)
        hbox_lint.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox_lint.addWidget(self.btn_lint_activate)
        vbox.addLayout(hbox_lint)
        vbox.addWidget(self.listErrors)
        hbox_pep8 = QHBoxLayout()
        if settings.CHECK_STYLE:
            self.btn_pep8_activate = QPushButton(self.tr("PEP8: ON"))
        else:
            self.btn_pep8_activate = QPushButton(self.tr("PEP8: OFF"))
        self.pep8Label = QLabel(self.tr("PEP8 Errors: %s") % 0)
        hbox_pep8.addWidget(self.pep8Label)
        hbox_pep8.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox_pep8.addWidget(self.btn_pep8_activate)
        vbox.addLayout(hbox_pep8)
        vbox.addWidget(self.listPep8)

        self.connect(self.listErrors, SIGNAL("itemSelectionChanged()"),
            self.errors_selected)
        self.connect(self.listPep8, SIGNAL("itemSelectionChanged()"),
            self.pep8_selected)
        self.connect(self.btn_lint_activate, SIGNAL("clicked()"),
            self._turn_on_off_lint)
        self.connect(self.btn_pep8_activate, SIGNAL("clicked()"),
            self._turn_on_off_pep8)

    def _turn_on_off_lint(self):
        """Change the status of the lint checker state."""
        settings.FIND_ERRORS = not settings.FIND_ERRORS
        if settings.FIND_ERRORS:
            self.btn_lint_activate.setText(self.tr("Lint: ON"))
        else:
            self.btn_lint_activate.setText(self.tr("Lint: OFF"))
        self.emit(SIGNAL("lintActivated(bool)"), settings.FIND_ERRORS)

    def _turn_on_off_pep8(self):
        """Change the status of the lint checker state."""
        settings.CHECK_STYLE = not settings.CHECK_STYLE
        if settings.CHECK_STYLE:
            self.btn_pep8_activate.setText(self.tr("PEP8: ON"))
        else:
            self.btn_pep8_activate.setText(self.tr("PEP8: OFF"))
        self.emit(SIGNAL("pep8Activated(bool)"), settings.CHECK_STYLE)

    def errors_selected(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget and self._outRefresh:
            lineno = int(self.listErrors.currentItem().data(Qt.UserRole))
            editorWidget.jump_to_line(lineno)
            editorWidget.setFocus()

    def pep8_selected(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget and self._outRefresh:
            lineno = int(self.listPep8.currentItem().data(Qt.UserRole))
            editorWidget.jump_to_line(lineno)
            editorWidget.setFocus()

    def refresh_lists(self, errors, pep8):
        self._outRefresh = False
        self.listErrors.clear()
        self.listPep8.clear()
        for lineno in errors.errorsSummary:
            linenostr = 'L%s\t' % str(lineno + 1)
            for data in errors.errorsSummary[lineno]:
                item = QListWidgetItem(linenostr + data)
                item.setToolTip(linenostr + data)
                item.setData(Qt.UserRole, lineno)
                self.listErrors.addItem(item)
        self.errorsLabel.setText(self.tr("Static Errors: %s") %
            len(errors.errorsSummary))
        for lineno in pep8.pep8checks:
            linenostr = 'L%s\t' % str(lineno + 1)
            for data in pep8.pep8checks[lineno]:
                item = QListWidgetItem(linenostr + data.split('\n')[0])
                item.setToolTip(linenostr + data.split('\n')[0])
                item.setData(Qt.UserRole, lineno)
                self.listPep8.addItem(item)
        self.pep8Label.setText(self.tr("PEP8 Errors: %s") %
            len(pep8.pep8checks))
        self._outRefresh = True

    def clear(self):
        """
        Clear the widget
        """
        self.listErrors.clear()
        self.listPep8.clear()
