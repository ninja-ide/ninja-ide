# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL


class FromImportDialog(QDialog):

    def __init__(self, fromSection, editorWidget, parent=None):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setModal(True)
        self.setWindowTitle('from ... import ...')
        self._editorWidget = editorWidget
        self._fromSection = fromSection

        hbox = QHBoxLayout(self)
        hbox.addWidget(QLabel('from'))
        self._lineFrom = QLineEdit()
        self._completer = QCompleter(fromSection)
        self._lineFrom.setCompleter(self._completer)
        hbox.addWidget(self._lineFrom)
        hbox.addWidget(QLabel('import'))
        self._lineImport = QLineEdit()
        hbox.addWidget(self._lineImport)
        self._btnAdd = QPushButton(self.tr('Add'))
        hbox.addWidget(self._btnAdd)

        self.connect(self._lineImport, SIGNAL("returnPressed()"),
            self._add_import)
        self.connect(self._btnAdd, SIGNAL("clicked()"),
            self._add_import)

    def _add_import(self):
        fromItem = unicode(self._lineFrom.text())
        importItem = unicode(self._lineImport.text())
        if fromItem in self._fromSection:
            cursor = self._editorWidget.document().find(fromItem)
        elif self._fromSection:
            cursor = self._editorWidget.document().find(self._fromSection[-1])
        else:
            cursor = self._editorWidget.textCursor()
            cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.EndOfLine)
        if fromItem:
            importLine = '\nfrom {0} import {1}'.format(fromItem, importItem)
        else:
            importLine = '\nimport {0}'.format(importItem)
        if self._editorWidget.document().find(
        importLine[1:]).position() == -1:
            cursor.insertText(importLine)
        self.close()
