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

from sys import builtin_module_names
from pkgutil import iter_modules

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide.tools import introspection


class FromImportDialog(QDialog):
    """From Import dialog class"""

    def __init__(self, editorWidget, parent=None):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle('from ... import ...')
        self._editorWidget = editorWidget

        source = self._editorWidget.get_text()
        source = source.encode(self._editorWidget.encoding)
        self._imports = introspection.obtain_imports(source)

        self._imports_names = list(self._imports["imports"].keys())
        self._imports_names += [imp for imp in self._imports['fromImports']]
        self._froms = [self._imports['fromImports'][imp]['module']
                       for imp in self._imports['fromImports']]
        self._froms += builtin_module_names
        self._froms += [module_name[1] for module_name in iter_modules()]
        self._froms = tuple(sorted(set(self._froms)))

        hbox = QHBoxLayout(self)
        hbox.addWidget(QLabel('from'))
        self._lineFrom = QLineEdit()
        self._completer = QCompleter(self._froms)
        self._lineFrom.setCompleter(self._completer)
        hbox.addWidget(self._lineFrom)
        hbox.addWidget(QLabel('import'))
        self._lineImport = QLineEdit()
        self._completerImport = QCompleter(self._imports_names)
        self._lineImport.setCompleter(self._completerImport)
        hbox.addWidget(self._lineImport)
        self._btnAdd = QPushButton(self.tr('Add'))
        hbox.addWidget(self._btnAdd)

        self.connect(self._lineImport, SIGNAL("returnPressed()"),
                     self._add_import)
        self.connect(self._btnAdd, SIGNAL("clicked()"),
                     self._add_import)

    def _add_import(self):
        """Get From item and Import item and add the import on the code"""
        fromItem = self._lineFrom.text()
        importItem = self._lineImport.text()
        if fromItem in self._froms:
            lineno = 0
            for imp in self._imports['fromImports']:
                lineno = self._imports['fromImports'][imp]['lineno'] - 1
                if self._imports['fromImports'][imp]['module'] == fromItem:
                    break
            block = self._editorWidget.document().findBlockByLineNumber(lineno)
            cursor = self._editorWidget.textCursor()
            cursor.setPosition(block.position())
        else:
            cursor = self._editorWidget.textCursor()
            cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.EndOfLine)
        if fromItem:
            importLine = '\nfrom {0} import {1}'.format(fromItem, importItem)
        else:
            importLine = '\nimport {0}'.format(importItem)
        if self._editorWidget.document().find(importLine[1:]).position() == -1:
            cursor.insertText(importLine)
        self.close()
