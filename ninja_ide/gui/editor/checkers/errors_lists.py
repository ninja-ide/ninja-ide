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
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QListWidgetItem
)
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    Qt
)
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide import translations
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer


class ErrorsWidget(QDialog):

    dockWidget = pyqtSignal('PyQt_PyObject')
    undockWidget = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)
        # PEP8
        self._list_pep8 = QListWidget()
        self._list_pep8.setWordWrap(True)
        self._list_pep8.setSortingEnabled(True)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(5, 3, 5, 3)
        if settings.CHECK_STYLE:
            self._btn_pep8 = QPushButton("PEP8: ON")
        else:
            self._btn_pep8 = QPushButton("PEP8: OFF")
        self._pep8_label = QLabel("PEP8 Errors: %s" % 0)
        hbox.addWidget(self._pep8_label)
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox.addWidget(self._btn_pep8)
        box.addLayout(hbox)
        box.addWidget(self._list_pep8)

        # Connections
        self._list_pep8.clicked.connect(self.__on_pep8_item_selected)
        self._btn_pep8.clicked.connect(self._turn_on_off_pep8)
        # Register service
        IDE.register_service("tab_errors", self)
        # ExplorerContainer.register_tab(translations.TR_TAB_ERRORS, self)

    @pyqtSlot()
    def __on_pep8_item_selected(self):
        main_container = IDE.get_service("main_container")
        neditor = main_container.get_current_editor()
        if neditor is not None:
            lineno = self._list_pep8.currentItem().data(Qt.UserRole)
            neditor.go_to_line(lineno)
            neditor.setFocus()

    @pyqtSlot()
    def _turn_on_off_pep8(self):
        """Change the status of the lint checker state"""
        settings.CHECK_STYLE = not settings.CHECK_STYLE
        if settings.CHECK_STYLE:
            self._btn_pep8.setText("PEP8: ON")
            self._list_pep8.show()
        else:
            self._btn_pep8.setText("PEP8: OFF")
            self._list_pep8.hide()
        # TODO: emit a singal to main container

    def refresh_pep8_list(self, errors):
        self._list_pep8.clear()
        for lineno, message in errors.items():
            lineno_str = 'L%s\t' % str(lineno + 1)
            item = QListWidgetItem(lineno_str + message.split('\n')[0])
            item.setData(Qt.UserRole, lineno)
            self._list_pep8.addItem(item)
        self._pep8_label.setText("PEP8 Errors: %s" % len(errors))

    def reject(self):
        if self.parent() is None:
            self.dockWidget.emit(self)

    def closeEvent(self, event):
        self.dockWidget.emit(self)
        event.ignore()

"""
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
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer


class ErrorsWidget(QDialog):

###############################################################################
# ERRORS WIDGET SIGNALS
###############################################################################
    pep8Activated(bool)
    lintActivated(bool)
###############################################################################

    def __init__(self, parent=None):
        super(ErrorsWidget, self).__init__(parent, Qt.WindowStaysOnTopHint)
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

        IDE.register_service('tab_errors', self)
        ExplorerContainer.register_tab(translations.TR_TAB_ERRORS, self)

    def install_tab(self):
        ide = IDE.get_service('ide')
        self.connect(ide, SIGNAL("goingDown()"), self.close)

    def _turn_on_off_lint(self):
        # Change the status of the lint checker state
        settings.FIND_ERRORS = not settings.FIND_ERRORS
        if settings.FIND_ERRORS:
            self.btn_lint_activate.setText(self.tr("Lint: ON"))
            self.listErrors.show()
        else:
            self.btn_lint_activate.setText(self.tr("Lint: OFF"))
            self.listErrors.hide()
        self.emit(SIGNAL("lintActivated(bool)"), settings.FIND_ERRORS)

    def _turn_on_off_pep8(self):
        # Change the status of the lint checker state
        settings.CHECK_STYLE = not settings.CHECK_STYLE
        if settings.CHECK_STYLE:
            self.btn_pep8_activate.setText(self.tr("PEP8: ON"))
            self.listPep8.show()
        else:
            self.btn_pep8_activate.setText(self.tr("PEP8: OFF"))
            self.listPep8.hide()
        self.emit(SIGNAL("pep8Activated(bool)"), settings.CHECK_STYLE)

    def errors_selected(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            editorWidget = main_container.get_current_editor()
            if editorWidget and self._outRefresh:
                lineno = int(self.listErrors.currentItem().data(Qt.UserRole))
                editorWidget.jump_to_line(lineno)
                editorWidget.setFocus()

    def pep8_selected(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            editorWidget = main_container.get_current_editor()
            if editorWidget and self._outRefresh:
                lineno = int(self.listPep8.currentItem().data(Qt.UserRole))
                editorWidget.jump_to_line(lineno)
                editorWidget.setFocus()

    def refresh_pep8_list(self, pep8):
        self._outRefresh = False
        self.listPep8.clear()
        for lineno in pep8:
            linenostr = 'L%s\t' % str(lineno + 1)
            for data in pep8[lineno]:
                item = QListWidgetItem(linenostr + data.split('\n')[0])
                item.setToolTip(linenostr + data.split('\n')[0])
                item.setData(Qt.UserRole, lineno)
                self.listPep8.addItem(item)
        self.pep8Label.setText(self.tr("PEP8 Errors: %s") %
                               len(pep8))
        self._outRefresh = True

    def refresh_error_list(self, errors):
        self._outRefresh = False
        self.listErrors.clear()
        for lineno in errors:
            linenostr = 'L%s\t' % str(lineno + 1)
            for data in errors[lineno]:
                item = QListWidgetItem(linenostr + data)
                item.setToolTip(linenostr + data)
                item.setData(Qt.UserRole, lineno)
                self.listErrors.addItem(item)
        self.errorsLabel.setText(self.tr("Static Errors: %s") %
                                 len(errors))
        self._outRefresh = True

    def clear(self):
        # Clear the widget
        self.listErrors.clear()
        self.listPep8.clear()

    def reject(self):
        if self.parent() is None:
            self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)

    def closeEvent(self, event):
        self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)
        event.ignore()

"""

if settings.SHOW_ERRORS_LIST:
    errorsWidget = ErrorsWidget()
else:
    errorsWidget = None
