# -*- coding: utf-8 *-*

from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QListWidget

from ninja_ide.tools.completion import code_completion


class CompleterWidget(QCompleter):

    def __init__(self, editor):
        QCompleter.__init__(self, [], editor)
        self._editor = editor

        self.setWidget(editor)
        self.popupView = QListWidget()
        self.popupView.setAlternatingRowColors(True)
        self.popupView.setWordWrap(False)
        self.setPopup(self.popupView)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)

        self.cc = code_completion.CodeCompletion()
        self.completion_results = []

        self.connect(self, SIGNAL("activated(const QString&)"),
            self.insert_completion)

    def update_metadata(self):
        source = self._editor.get_text()
        source = source.encode(self._editor.encoding)
        self.cc.analyze_file('', source)

    def insert_completion(self, insert):
        extra = insert.length() - self.completionPrefix().length()
        self.widget().textCursor().insertText(insert.right(extra))
        self.popup().hide()

    def complete(self, cr, results):
        self.popupView.clear()
        self.completion_results = results
        model = self.obtain_model_items(results)
        self.setModel(model)
        self.popup().setCurrentIndex(model.index(0, 0))
        cr.setWidth(self.popup().sizeHintForColumn(0) \
            + self.popup().verticalScrollBar().sizeHint().width() + 10)
        self.popupView.updateGeometries()
        QCompleter.complete(self, cr)

    def obtain_model_items(self, proposals):
        for p in proposals:
            self.popupView.addItem(QListWidgetItem(p))
        return self.popupView.model()

    def set_completion_prefix(self, prefix):
        self.setCompletionPrefix(prefix)
        proposals = [item for item in self.completion_results \
            if item.startswith(prefix)]
        cr = self._editor.cursorRect()
        self.complete(cr, proposals)

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
            self.set_completion_prefix(prefix)
            self.popup().setCurrentIndex(
                self.completionModel().index(0, 0))
            self.setCurrentRow(0)
        if event.key() == Qt.Key_Period:
            self.fill_completer()

    def fill_completer(self):
        source = self._editor.get_text()
        source = source.encode(self._editor.encoding)
        self.cc.analyze_file('', source)
        offset = self._editor.textCursor().position()
        results = self.cc.get_completion(source, offset)
        results.sort()
        cr = self._editor.cursorRect()
        self.complete(cr, results)
