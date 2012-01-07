# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.main_panel import main_container


ERRORS_TEXT = "Static Errors: %1"
PEP8_TEXT = "PEP8 Errors: %1"


class ErrorsWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.pep8 = None
        self._outRefresh = True

        vbox = QVBoxLayout(self)
        self.listErrors = QListWidget()
        self.listPep8 = QListWidget()
        self.errorsLabel = QLabel(self.tr(ERRORS_TEXT).arg(0))
        vbox.addWidget(self.errorsLabel)
        vbox.addWidget(self.listErrors)
        self.pep8Label = QLabel(self.tr(PEP8_TEXT).arg(0))
        vbox.addWidget(self.pep8Label)
        vbox.addWidget(self.listPep8)

        self.connect(self.listErrors, SIGNAL("itemSelectionChanged()"),
            self.errors_selected)
        self.connect(self.listPep8, SIGNAL("itemSelectionChanged()"),
            self.pep8_selected)

    def errors_selected(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget and self._outRefresh:
            index = self.listErrors.currentItem().data(Qt.UserRole).toInt()[0]
            editorWidget.jump_to_line(
                editorWidget.errors.errorsLines[index] - 1)
            editorWidget.setFocus()

    def pep8_selected(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget and self._outRefresh:
            index = self.listPep8.currentItem().data(Qt.UserRole).toInt()[0]
            editorWidget.jump_to_line(
                editorWidget.pep8.pep8lines[index] - 1)
            editorWidget.setFocus()

    def refresh_lists(self, errors, pep8):
        self._outRefresh = False
        self.listErrors.clear()
        self.listPep8.clear()
        for index, data in enumerate(errors.errorsLines):
            lineno = 'l: %s\t' % str(errors.errorsLines.get(index, 'n/a'))
            item = QListWidgetItem(lineno + errors.errorsSummary[data])
            item.setData(Qt.UserRole, index)
            self.listErrors.addItem(item)
        self.errorsLabel.setText(self.tr(ERRORS_TEXT).arg(
            len(errors.errorsLines)))
        for index, data in enumerate(pep8.pep8checks):
            lineno = 'l: %s,\t' % str(pep8.pep8lines.get(index, 'n/a'))
            item = QListWidgetItem(lineno + data.split('\n')[0])
            item.setData(Qt.UserRole, index)
            self.listPep8.addItem(item)
        self.pep8Label.setText(self.tr(PEP8_TEXT).arg(
            len(pep8.pep8checks)))
        self._outRefresh = True
