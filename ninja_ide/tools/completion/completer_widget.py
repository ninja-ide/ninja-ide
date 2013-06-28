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
from __future__ import unicode_literals

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QStackedLayout
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QListWidget

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.tools.completion import code_completion


class CodeCompletionWidget(QFrame):

    def __init__(self, editor):
        super(CodeCompletionWidget, self).__init__(
            None, Qt.FramelessWindowHint | Qt.ToolTip)
        self._editor = editor
        self._revision = 0
        self._block = 0
        self.stack_layout = QStackedLayout(self)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        self.stack_layout.setSpacing(0)
        self.completion_list = QListWidget()
        self.completion_list.setMinimumHeight(200)
        self.completion_list.setAlternatingRowColors(True)
        self._list_index = self.stack_layout.addWidget(self.completion_list)

        self._icons = {'a': resources.IMAGES['attribute'],
                       'f': resources.IMAGES['function'],
                       'c': resources.IMAGES['class'],
                       'm': resources.IMAGES['module']}

        self.cc = code_completion.CodeCompletion()
        self._completion_results = {}
        self._prefix = ''
        self.setVisible(False)
        self.source = ''
        self._key_operations = {
            Qt.Key_Up: self._select_previous_row,
            Qt.Key_Down: self._select_next_row,
            Qt.Key_PageUp: (lambda: self._select_previous_row(6)),
            Qt.Key_PageDown: (lambda: self._select_next_row(6)),
            Qt.Key_Right: lambda: None,
            Qt.Key_Left: lambda: None,
            Qt.Key_Enter: self.pre_key_insert_completion,
            Qt.Key_Return: self.pre_key_insert_completion,
            Qt.Key_Tab: self.pre_key_insert_completion,
            Qt.Key_Space: self.hide_completer,
            Qt.Key_Escape: self.hide_completer,
            Qt.Key_Backtab: self.hide_completer,
            Qt.NoModifier: self.hide_completer,
            Qt.ShiftModifier: self.hide_completer,
        }

        self.desktop = QApplication.instance().desktop()

        self.connect(self.completion_list,
                     SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.pre_key_insert_completion)
        self.connect(self._editor.document(),
                     SIGNAL("cursorPositionChanged(QTextCursor)"),
                     self.update_metadata)

    def _select_next_row(self, move=1):
        new_row = self.completion_list.currentRow() + move
        if new_row < self.completion_list.count():
            self.completion_list.setCurrentRow(new_row)
        else:
            self.completion_list.setCurrentRow(0)
        return True

    def _select_previous_row(self, move=1):
        new_row = self.completion_list.currentRow() - move
        if new_row >= 0:
            self.completion_list.setCurrentRow(new_row)
        else:
            self.completion_list.setCurrentRow(
                self.completion_list.count() - move)
        return True

    def update_metadata(self, cursor):
        if settings.CODE_COMPLETION:
            if self._editor.document().revision() != self._revision and \
               cursor.block().blockNumber() != self._block:
                source = self._editor.get_text()
                source = source.encode(self._editor.encoding)
                self.cc.analyze_file(self._editor.ID, source,
                                     self._editor.indent, self._editor.useTabs)
                self._revision = self._editor.document().revision()
                self._block = cursor.block().blockNumber()

    def insert_completion(self, insert, type_=ord('a')):
        if insert != self._prefix:
            closing = ''
            if type_ in (ord('f'), ord('c')):
                closing = '()'
            extra = len(self._prefix) - len(insert)
            insertion = '%s%s' % (insert[extra:], closing)
            self._editor.textCursor().insertText(insertion)
        self.hide_completer()

    def _get_geometry(self):
        cr = self._editor.cursorRect()
        desktop_geometry = self.desktop.availableGeometry(self._editor)
        point = self._editor.mapToGlobal(cr.topLeft())
        cr.moveTopLeft(point)
        #Check new position according desktop geometry
        width = (self.completion_list.sizeHintForColumn(0) +
                 self.completion_list.verticalScrollBar().sizeHint().width() +
                 10)
        height = 200
        orientation = (point.y() + height) < desktop_geometry.height()
        if orientation:
            cr.moveTop(cr.bottom())
        cr.setWidth(width)
        cr.setHeight(height)
        if not orientation:
            cr.moveBottom(cr.top())
        xpos = desktop_geometry.width() - (point.x() + width)
        if xpos < 0:
            cr.moveLeft(cr.left() + xpos)
        return cr

    def complete(self, results):
        self.add_list_items(results)
        self.completion_list.setCurrentRow(0)
        cr = self._get_geometry()
        self.setGeometry(cr)
        self.completion_list.updateGeometries()
        self.show()

    def add_list_items(self, proposals):
        self.completion_list.clear()
        for p in proposals:
            self.completion_list.addItem(
                QListWidgetItem(
                    QIcon(
                        self._icons.get(p[0], resources.IMAGES['attribute'])),
                    p[1], type=ord(p[0])))

    def set_completion_prefix(self, prefix, valid=True):
        self._prefix = prefix
        proposals = []
        proposals += [('m', item)
                      for item in self._completion_results.get('modules', [])
                      if item.startswith(prefix)]
        proposals += [('c', item)
                      for item in self._completion_results.get('classes', [])
                      if item.startswith(prefix)]
        proposals += [('a', item)
                      for item in self._completion_results.get(
                          'attributes', [])
                      if item.startswith(prefix)]
        proposals += [('f', item)
                      for item in self._completion_results.get('functions', [])
                      if item.startswith(prefix)]
        if proposals and valid:
            self.complete(proposals)
        else:
            self.hide_completer()

    def _invalid_completion_position(self):
        result = False
        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine,
                            QTextCursor.KeepAnchor)
        selection = cursor.selectedText()[:-1].split(' ')
        if len(selection) == 0 or selection[-1] == '' or \
           selection[-1].isdigit():
            result = True
        return result

    def fill_completer(self, force_completion=False):
        if not force_completion and (self._editor.cursor_inside_string() or
           self._editor.cursor_inside_comment() or
           self._invalid_completion_position()):
            return
        source = self._editor.get_text()
        source = source.encode(self._editor.encoding)
        offset = self._editor.textCursor().position()
        results = self.cc.get_completion(source, offset)
        self._completion_results = results
        if force_completion:
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.StartOfWord,
                                QTextCursor.KeepAnchor)
            prefix = cursor.selectedText()
        else:
            prefix = self._editor._text_under_cursor()
        self.set_completion_prefix(prefix)

    def hide_completer(self):
        self._prefix = ''
        self.hide()

    def pre_key_insert_completion(self):
        type_ = ord('a')
        current = self.completion_list.currentItem()
        insert = current.text()
        if not insert.endswith(')'):
            type_ = current.type()
        self.insert_completion(insert, type_)
        self.hide_completer()
        return True

    def process_pre_key_event(self, event):
        if not self.isVisible() or self._editor.lang != "python":
            return False
        skip = self._key_operations.get(event.key(), lambda: False)()
        self._key_operations.get(event.modifiers(), lambda: False)()
        if skip is None:
            skip = False
        return skip

    def process_post_key_event(self, event):
        if not settings.CODE_COMPLETION or self._editor.lang != "python":
            return
        if self.isVisible():
            source = self._editor.get_text()
            source = source.encode(self._editor.encoding)
            offset = self._editor.textCursor().position()
            prefix, valid = self.cc.get_prefix(source, offset)
            self.set_completion_prefix(prefix, valid)
            self.completion_list.setCurrentRow(0)
        force_completion = (event.key() == Qt.Key_Space and
                            event.modifiers() == Qt.ControlModifier)
        if event.key() == Qt.Key_Period or force_completion:
            self.fill_completer(force_completion)


class CompleterWidget(QCompleter):

    def __init__(self, editor):
        QCompleter.__init__(self, [], editor)
        self._editor = editor

        self.setWidget(editor)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)

        self.cc = code_completion.CodeCompletion()
        self.completion_results = {}

        self.connect(self, SIGNAL("activated(const QString&)"),
                     self.insert_completion)

    def insert_completion(self, insert):
        self.widget().textCursor().insertText(
            insert[len(self.completionPrefix()):])
        self.popup().hide()

    def complete(self, cr, results):
        proposals = []
        proposals += results.get('modules', [])
        proposals += results.get('classes', [])
        proposals += results.get('attributes', [])
        proposals += results.get('functions', [])
        self.model().setStringList(proposals)
        self.popup().setCurrentIndex(self.model().index(0, 0))
        cr.setWidth(self.popup().sizeHintForColumn(0)
                    + self.popup().verticalScrollBar().sizeHint().width() + 10)
        QCompleter.complete(self, cr)

    def is_visible(self):
        return self.popup().isVisible()

    def process_pre_key_event(self, event):
        skip = False
        if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
            event.ignore()
            self.popup().hide()
            skip = True
        elif event.key() in (Qt.Key_Space, Qt.Key_Escape, Qt.Key_Backtab):
            self.popup().hide()
        return skip

    def process_post_key_event(self, event):
        if self.popup().isVisible():
            prefix = self._editor._text_under_cursor()
            self.setCompletionPrefix(prefix)
            self.popup().setCurrentIndex(
                self.completionModel().index(0, 0))
            self.setCurrentRow(0)
        if event.key() == Qt.Key_Period or (event.key() == Qt.Key_Space and
                                            event.modifiers() ==
                                            Qt.ControlModifier):
            self.fill_completer()

    def fill_completer(self):
        source = self._editor.get_text()
        source = source.encode(self._editor.encoding)
#        self.cc.analyze_file('', source)
        offset = self._editor.textCursor().position()
        results = self.cc.get_completion(source, offset)
        results.sort()
        self.completion_results = results
        cr = self._editor.cursorRect()
        self.complete(cr, results)
