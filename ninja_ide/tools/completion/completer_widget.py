# -*- coding: utf-8 *-*

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QStackedLayout
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QListWidget

from ninja_ide.tools.completion import code_completion


class CodeCompletionWidget(QFrame):

    def __init__(self, editor):
        super(CodeCompletionWidget, self).__init__(
            None, Qt.FramelessWindowHint | Qt.ToolTip)
        self._editor = editor
        self.stack_layout = QStackedLayout(self)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        self.stack_layout.setSpacing(0)
        self.completion_list = QListWidget()
        self.completion_list.setMinimumHeight(200)
        self.completion_list.setAlternatingRowColors(True)
        self._list_index = self.stack_layout.addWidget(self.completion_list)

        self.cc = code_completion.CodeCompletion()
        self._completion_results = []
        self._prefix = u''
        self.setVisible(False)
        self.source = ''

        self._key_operations = {
            Qt.Key_Up: self._select_previous_row,
            Qt.Key_Down: self._select_next_row,
            Qt.Key_Right: lambda: None,
            Qt.Key_Left: lambda: None,
        }

        desktop = QApplication.instance().desktop()
        self._desktop_geometry = desktop.availableGeometry()

        self.connect(self._editor.document(), SIGNAL("blockCountChanged(int)"),
            self.update_metadata)

    def _select_next_row(self):
        new_row = self.completion_list.currentRow() + 1
        if new_row < self.completion_list.count():
            self.completion_list.setCurrentRow(new_row)
        else:
            self.completion_list.setCurrentRow(0)

    def _select_previous_row(self):
        new_row = self.completion_list.currentRow() - 1
        if new_row >= 0:
            self.completion_list.setCurrentRow(new_row)
        else:
            self.completion_list.setCurrentRow(
                self.completion_list.count() - 1)

    def update_metadata(self):
        source = self._editor.get_text()
        source = source.encode(self._editor.encoding)
        self.cc.analyze_file('', source)

    def insert_completion(self, insert):
        if insert != self._prefix:
            extra = len(self._prefix) - len(insert)
            self._editor.textCursor().insertText(insert[extra:])
        self.hide_completer()

    def _get_geometry(self):
        cr = self._editor.cursorRect()
        point = self._editor.mapToGlobal(cr.topLeft())
        cr.moveTopLeft(point)
        #Check new position according desktop geometry
        width = (self.completion_list.sizeHintForColumn(0) + \
            self.completion_list.verticalScrollBar().sizeHint().width() + 10)
        height = 200
        orientation = (point.y() + height) < self._desktop_geometry.height()
        if orientation:
            cr.moveTop(cr.bottom())
        cr.setWidth(width)
        cr.setHeight(height)
        if not orientation:
            cr.moveBottom(cr.top())
        xpos = self._desktop_geometry.width() - (point.x() + width)
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
            self.completion_list.addItem(QListWidgetItem(p))

    def set_completion_prefix(self, prefix):
        self._prefix = prefix
        proposals = [item for item in self.completion_results \
            if item.startswith(prefix)]
        if proposals:
            self.complete(proposals)
        else:
            self.hide_completer()

    def fill_completer(self):
        source = self._editor.get_text()
        source = source.encode(self._editor.encoding)
        offset = self._editor.textCursor().position()
        results = self.cc.get_completion(source, offset)
        results.sort()
        self.completion_results = results
        prefix = self._editor._text_under_cursor()
        if prefix:
            self.set_completion_prefix(prefix)
        else:
            self.complete(results)

    def hide_completer(self):
        self._prefix = ''
        self.hide()

    def process_pre_key_event(self, event):
        skip = False
        if not self.isVisible():
            return skip
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
            insert = unicode(self.completion_list.currentItem().text())
            self.insert_completion(insert)
            event.ignore()
            self.hide_completer()
            skip = True
        elif event.key() in (Qt.Key_Space, Qt.Key_Escape, Qt.Key_Backtab):
            self.hide_completer()
        elif event.key() in self._key_operations:
            self._key_operations[event.key()]()
            skip = True
        return skip

    def process_post_key_event(self, event):
        if self.isVisible():
            prefix = self._editor._text_under_cursor()
            self.set_completion_prefix(prefix)
            self.completion_list.setCurrentRow(0)
        if event.key() == Qt.Key_Period  or (event.key() == Qt.Key_Space and \
        event.modifiers() == Qt.ControlModifier):
            self.fill_completer()


class CompleterWidget(QCompleter):

    def __init__(self, editor):
        QCompleter.__init__(self, [], editor)
        self._editor = editor

        self.setWidget(editor)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)

        self.cc = code_completion.CodeCompletion()
        self.completion_results = []

        self.connect(self, SIGNAL("activated(const QString&)"),
            self.insert_completion)

    def insert_completion(self, insert):
        extra = insert.length() - self.completionPrefix().length()
        self.widget().textCursor().insertText(insert.right(extra))
        self.popup().hide()

    def complete(self, cr, results):
        self.model().setStringList(results)
        self.popup().setCurrentIndex(self.model().index(0, 0))
        cr.setWidth(self.popup().sizeHintForColumn(0) \
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
        if event.key() == Qt.Key_Period  or (event.key() == Qt.Key_Space and \
        event.modifiers() == Qt.ControlModifier):
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
