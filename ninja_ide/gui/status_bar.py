# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QFileSystemModel
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QShortcut
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.tools import locator
from ninja_ide.tools import ui_tools
from ninja_ide.gui.main_panel import main_container


__statusBarInstance = None


def StatusBar(*args, **kw):
    global __statusBarInstance
    if __statusBarInstance is None:
        __statusBarInstance = __StatusBar(*args, **kw)
    return __statusBarInstance


class __StatusBar(QStatusBar):

    def __init__(self, parent=None):
        QStatusBar.__init__(self, parent)

        self._widgetStatus = QWidget()
        vbox = QVBoxLayout(self._widgetStatus)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        #Search Layout
        self._searchWidget = SearchWidget(self)
        vbox.addWidget(self._searchWidget)
        #Replace Layout
        self._replaceWidget = ReplaceWidget(self)
        vbox.addWidget(self._replaceWidget)
        self._replaceWidget.setVisible(False)
        #Code Locator
        self._codeLocator = locator.CodeLocatorWidget(self)
        vbox.addWidget(self._codeLocator)
        self._codeLocator.setVisible(False)
        #File system completer
        self._fileSystemOpener = FileSystemOpener()
        vbox.addWidget(self._fileSystemOpener)
        self._fileSystemOpener.setVisible(False)

        self.addWidget(self._widgetStatus)

        self._shortEsc = QShortcut(QKeySequence(Qt.Key_Escape), self)

        self.connect(self, SIGNAL("messageChanged(QString)"), self.message_end)
        self.connect(self._replaceWidget._btnCloseReplace, SIGNAL("clicked()"),
            lambda: self._replaceWidget.setVisible(False))
        self.connect(self._replaceWidget._btnReplace, SIGNAL("clicked()"),
            self.replace)
        self.connect(self._replaceWidget._btnReplaceAll, SIGNAL("clicked()"),
            self.replace_all)
        self.connect(self._shortEsc, SIGNAL("activated()"), self.hide_status)
        self.connect(self._fileSystemOpener.btnClose, SIGNAL("clicked()"),
            self.hide_status)
        self.connect(self._fileSystemOpener, SIGNAL("requestHide()"),
            self.hide_status)

    def explore_code(self):
        self._codeLocator.explore_code()

    def explore_file_code(self, path):
        self._codeLocator.explore_file_code(path)

    def show(self):
        self.clearMessage()
        QStatusBar.show(self)
        if self._widgetStatus.isVisible():
            self._searchWidget._line.setFocus()
            self._searchWidget._line.selectAll()

    def show_replace(self):
        self.clearMessage()
        self.show()
        editor = main_container.MainContainer().get_actual_editor()
        if editor:
            if editor.textCursor().hasSelection():
                word = editor.textCursor().selectedText()
                self._searchWidget._line.setText(word)
        self._replaceWidget.setVisible(True)

    def show_with_word(self):
        self.clearMessage()
        editor = main_container.MainContainer().get_actual_editor()
        if editor:
            word = editor._text_under_cursor()
            self._searchWidget._line.setText(word)
            editor = main_container.MainContainer().get_actual_editor()
            editor.moveCursor(QTextCursor.WordLeft)
            self._searchWidget.find_matches(editor)
            self.show()

    def show_locator(self):
        self.clearMessage()
        self._searchWidget.setVisible(False)
        self.show()
        self._codeLocator.setVisible(True)
        self._codeLocator._completer.setFocus()
        self._codeLocator.show_suggestions()

    def show_file_opener(self):
        self.clearMessage()
        self._searchWidget.setVisible(False)
        self._fileSystemOpener.setVisible(True)
        self.show()
        self._fileSystemOpener.pathLine.setFocus()

    def hide_status(self):
        self._searchWidget._checkSensitive.setCheckState(Qt.Unchecked)
        self._searchWidget._checkWholeWord.setCheckState(Qt.Unchecked)
        self.hide()
        self._searchWidget.setVisible(True)
        self._replaceWidget.setVisible(False)
        self._codeLocator.setVisible(False)
        self._fileSystemOpener.setVisible(False)
        widget = main_container.MainContainer().get_actual_widget()
        if widget:
            widget.setFocus()

    def replace(self):
        s = 0 if not self._searchWidget._checkSensitive.isChecked() \
            else QTextDocument.FindCaseSensitively
        w = 0 if not self._searchWidget._checkWholeWord.isChecked() \
            else QTextDocument.FindWholeWords
        flags = 0 + s + w
        editor = main_container.MainContainer().get_actual_editor()
        if editor:
            editor.replace_match(unicode(self._searchWidget._line.text()),
                unicode(self._replaceWidget._lineReplace.text()), flags)
        if not editor.textCursor().hasSelection():
            self.find()

    def replace_all(self):
        s = 0 if not self._searchWidget._checkSensitive.isChecked() \
            else QTextDocument.FindCaseSensitively
        w = 0 if not self._searchWidget._checkWholeWord.isChecked() \
            else QTextDocument.FindWholeWords
        flags = 0 + s + w
        editor = main_container.MainContainer().get_actual_editor()
        if editor:
            editor.replace_match(unicode(self._searchWidget._line.text()),
                unicode(self._replaceWidget._lineReplace.text()), flags, True)

    def find(self):
        s = 0 if not self._searchWidget._checkSensitive.isChecked() \
            else QTextDocument.FindCaseSensitively
        w = 0 if not self._searchWidget._checkWholeWord.isChecked() \
            else QTextDocument.FindWholeWords
        flags = s + w
        editor = main_container.MainContainer().get_actual_editor()
        if editor:
            editor.find_match(unicode(self._searchWidget._line.text()), flags)

    def find_next(self):
        s = 0 if not self._searchWidget._checkSensitive.isChecked() \
            else QTextDocument.FindCaseSensitively
        w = 0 if not self._searchWidget._checkWholeWord.isChecked() \
            else QTextDocument.FindWholeWords
        flags = 0 + s + w
        editor = main_container.MainContainer().get_actual_editor()
        if editor:
            editor.find_match(unicode(self._searchWidget._line.text()),
                flags, True)

    def find_previous(self):
        s = 0 if not self._searchWidget._checkSensitive.isChecked() \
            else QTextDocument.FindCaseSensitively
        w = 0 if not self._searchWidget._checkWholeWord.isChecked() \
            else QTextDocument.FindWholeWords
        flags = 1 + s + w
        editor = main_container.MainContainer().get_actual_editor()
        if editor:
            editor.find_match(unicode(self._searchWidget._line.text()),
            flags, True)

    def showMessage(self, message, timeout):
        self._widgetStatus.hide()
        self._replaceWidget.setVisible(False)
        self.show()
        QStatusBar.showMessage(self, message, timeout)

    def message_end(self, message):
        if message == '':
            self.hide()
            QStatusBar.clearMessage(self)
            self._widgetStatus.show()
            widget = main_container.MainContainer().get_actual_widget()
            if widget:
                widget.setFocus()


class SearchWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self._parent = parent
        hSearch = QHBoxLayout(self)
        hSearch.setContentsMargins(0, 0, 0, 0)
        self._checkSensitive = QCheckBox(self.tr("Respect Case Sensitive"))
        self._checkWholeWord = QCheckBox(self.tr("Find Whole Words"))
        self._line = TextLine(self)
        self._line.setMinimumWidth(250)
        self._btnClose = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self._btnFind = QPushButton(QIcon(resources.IMAGES['find']), '')
        self.btnPrevious = QPushButton(
            self.style().standardIcon(QStyle.SP_ArrowLeft), '')
        self.btnPrevious.setToolTip(self.tr("Press (%1 + Left Arrow)").arg(
            settings.OS_KEY))
        self.btnNext = QPushButton(
            self.style().standardIcon(QStyle.SP_ArrowRight), '')
        self.btnNext.setToolTip(self.tr("Press (%1 + Right Arrow)").arg(
            settings.OS_KEY))
        hSearch.addWidget(self._btnClose)
        hSearch.addWidget(self._line)
        hSearch.addWidget(self._btnFind)
        hSearch.addWidget(self.btnPrevious)
        hSearch.addWidget(self.btnNext)
        hSearch.addWidget(self._checkSensitive)
        hSearch.addWidget(self._checkWholeWord)

        self.totalMatches = 0
        self.index = 0
        self._line.counter.update_count(self.index, self.totalMatches)

        self.connect(self._btnClose, SIGNAL("clicked()"),
            self._parent.hide_status)
        self.connect(self._btnFind, SIGNAL("clicked()"),
            self.find_next)
        self.connect(self.btnNext, SIGNAL("clicked()"),
            self.find_next)
        self.connect(self.btnPrevious, SIGNAL("clicked()"),
            self.find_previous)

    def find_next(self):
        self._parent.find_next()
        if self.totalMatches > 0 and self.index < self.totalMatches:
            self.index += 1
        elif self.totalMatches > 0:
            self.index = 1
        self._line.counter.update_count(self.index, self.totalMatches)

    def find_previous(self):
        self._parent.find_previous()
        if self.totalMatches > 0 and self.index > 1:
            self.index -= 1
        elif self.totalMatches > 0:
            self.index = self.totalMatches
            editor = main_container.MainContainer().get_actual_editor()
            editor.moveCursor(QTextCursor.End)
            self._parent.find_previous()
        self._line.counter.update_count(self.index, self.totalMatches)

    def find_matches(self, editor):
        text = unicode(editor.toPlainText())
        search = unicode(self._line.text())
        hasSearch = len(search) > 0
        if self._checkSensitive.isChecked():
            self.totalMatches = text.count(search)
        else:
            self.totalMatches = text.lower().count(search.lower())
        if hasSearch and self.totalMatches > 0:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.WordLeft)
            cursor.movePosition(QTextCursor.Start,
                QTextCursor.KeepAnchor)
            text = unicode(cursor.selectedText())
            self.index = text.count(search) + 1
        else:
            self.index = 0
            self.totalMatches = 0
        self._line.counter.update_count(self.index, self.totalMatches,
            hasSearch)
        if hasSearch:
            self._parent.find()


class ReplaceWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        hReplace = QHBoxLayout(self)
        hReplace.setContentsMargins(0, 0, 0, 0)
        self._lineReplace = QLineEdit()
        self._lineReplace.setMinimumWidth(250)
        self._btnCloseReplace = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self._btnReplace = QPushButton(self.tr("Replace"))
        self._btnReplaceAll = QPushButton(self.tr("Replace All"))
        hReplace.addWidget(self._btnCloseReplace)
        hReplace.addWidget(self._lineReplace)
        hReplace.addWidget(self._btnReplace)
        hReplace.addWidget(self._btnReplaceAll)


class TextLine(QLineEdit):

    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self._parent = parent
        self.counter = ui_tools.LineEditCount(self)

    def keyPressEvent(self, event):
        editor = main_container.MainContainer().get_actual_editor()
        if editor is None:
            super(TextLine, self).keyPressEvent(event)
            return
        if editor and event.key() in \
        (Qt.Key_Enter, Qt.Key_Return):
            self._parent.find_next()
            return
        elif event.modifiers() == Qt.ControlModifier and \
        event.key() == Qt.Key_Right:
            self._parent.find_next()
            return
        elif event.modifiers() == Qt.ControlModifier and \
        event.key() == Qt.Key_Left:
            self._parent.find_previous()
            return
        super(TextLine, self).keyPressEvent(event)
        if int(event.key()) in range(32, 162) or \
        event.key() == Qt.Key_Backspace:
            has_replace = self._parent._parent._replaceWidget.isVisible()
            if not has_replace:
                self._parent.find_matches(editor)


class FileSystemOpener(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.btnClose = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self.completer = QCompleter(self)
        self.pathLine = ui_tools.LineEditTabCompleter(self.completer)
        fileModel = QFileSystemModel(self.completer)
        fileModel.setRootPath("")
        self.completer.setModel(fileModel)
        self.pathLine.setCompleter(self.completer)
        self.btnOpen = QPushButton(
            self.style().standardIcon(QStyle.SP_ArrowRight), 'Open!')
        hbox.addWidget(self.btnClose)
        hbox.addWidget(QLabel(self.tr("Path:")))
        hbox.addWidget(self.pathLine)
        hbox.addWidget(self.btnOpen)

        self.connect(self.pathLine, SIGNAL("returnPressed()"),
            self._open_file)
        self.connect(self.btnOpen, SIGNAL("clicked()"),
            self._open_file)

    def _open_file(self):
        path = unicode(self.pathLine.text())
        main_container.MainContainer().open_file(path)
        self.emit(SIGNAL("requestHide()"))

    def showEvent(self, event):
        super(FileSystemOpener, self).showEvent(event)
        self.pathLine.selectAll()
