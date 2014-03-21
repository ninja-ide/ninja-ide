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

import re

from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QFileSystemModel
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QShortcut
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.tools import locator
from ninja_ide.tools import ui_tools
from ninja_ide.gui import actions
from ninja_ide.gui.ide import IDE
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.status_bar')
DEBUG = logger.debug


_STATUSBAR_STATE_SEARCH = "SEARCH"
_STATUSBAR_STATE_REPLACE = "REPLACE"
_STATUSBAR_STATE_LOCATOR = "LOCATOR"
_STATUSBAR_STATE_FILEOPENER = "FILEOPENER"


class _StatusBar(QStatusBar):

    """StatusBar widget to be used in the IDE for several purposes."""

    def __init__(self):
        super(_StatusBar, self).__init__()
        self.current_status = _STATUSBAR_STATE_SEARCH

        self._widgetStatus = QWidget()
        vbox = QVBoxLayout(self._widgetStatus)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        #Search Layout
        self._searchWidget = SearchWidget()
        vbox.addWidget(self._searchWidget)
        #Replace Layout
        self._replaceWidget = ReplaceWidget()
        vbox.addWidget(self._replaceWidget)
        self._replaceWidget.setVisible(False)
        #Code Locator
        self._codeLocator = locator.CodeLocatorWidget()
        vbox.addWidget(self._codeLocator)
        self._codeLocator.setVisible(False)
        #File system completer
        self._fileSystemOpener = FileSystemOpener()
        vbox.addWidget(self._fileSystemOpener)
        self._fileSystemOpener.setVisible(False)

        self.addWidget(self._widgetStatus)
        # Not Configurable Shortcuts
        shortEscStatus = QShortcut(QKeySequence(Qt.Key_Escape), self)

        self.connect(shortEscStatus, SIGNAL("activated()"), self.hide_status)
        self.connect(self._searchWidget._btnClose, SIGNAL("clicked()"),
            self.hide_status)
        self.connect(self._replaceWidget._btnCloseReplace, SIGNAL("clicked()"),
            lambda: self._replaceWidget.setVisible(False))
        self.connect(self._fileSystemOpener.btnClose, SIGNAL("clicked()"),
            self.hide_status)
        self.connect(self._fileSystemOpener, SIGNAL("requestHide()"),
            self.hide_status)
        self.connect(self._codeLocator, SIGNAL("hidden()"),
            self.hide_status)

        #Register signals connections
        connections = (
            {'target': 'main_container',
            'signal_name': 'currentEditorChanged(QString)',
            'slot': self._handle_tab_changed},
            {'target': 'main_container',
            'signal_name': 'updateLocator(QString)',
            'slot': self._explore_file_code},
            {'target': 'projects_explorer',
            'signal_name': 'updateLocator()',
            'slot': self._explore_code},
            )

        IDE.register_signals('status_bar', connections)
        IDE.register_service('status_bar', self)

    def install(self):
        """Install StatusBar as a service."""
        self.hide()
        ide = IDE.get_service('ide')
        ide.setStatusBar(self)

        ui_tools.install_shortcuts(self, actions.ACTIONS_STATUS, ide)

    def _handle_tab_changed(self, new_tab):
        """
        Re-run search if tab changed, we use the find of search widget because
        we want the widget to be updated.
        """
        main_container = IDE.get_service("main_container")
        if main_container:
            editor = main_container.get_current_editor()
        else:
            return

        if editor:
            if self._searchWidget.isVisible():
                self._searchWidget.find_matches(editor)
            if editor:
                self.disconnect(editor, SIGNAL("textChanged()"),
                            self._notify_editor_changed)
                self.connect(editor, SIGNAL("textChanged()"),
                            self._notify_editor_changed)

    def _notify_editor_changed(self):
        """
        Lets search widget know that the editor contents changed and find
        needs to be re-run
        """
        if self._searchWidget.isVisible():
            main_container = IDE.get_service("main_container")
            if main_container:
                editor = main_container.get_current_editor()
            else:
                return

            if editor:
                self._searchWidget.contents_changed(editor)

    def _explore_code(self):
        """Update locator metadata for the current projects."""
        self._codeLocator.explore_code()

    def _explore_file_code(self, path):
        """Update locator metadata for the file in path."""
        self._codeLocator.explore_file_code(path)

    def show_search(self):
        """Show the status bar with the search widget."""
        self.current_status = _STATUSBAR_STATE_SEARCH
        self._searchWidget.setVisible(True)
        self.show()
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()

        if editor and editor.textCursor().hasSelection():
            text = editor.textCursor().selectedText()
            self._searchWidget._line.setText(text)
            self._searchWidget.find_matches(editor, True)
        if self._widgetStatus.isVisible():
            self._searchWidget._line.setFocus()
            self._searchWidget._line.selectAll()

    def show_replace(self):
        """Show the status bar with the search/replace widget."""
        self.current_status = _STATUSBAR_STATE_REPLACE
        self._replaceWidget.setVisible(True)
        self.show_search()

    def show_with_word(self):
        """Show the status bar with search widget using word under cursor."""
        self.show_search()
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            word = editor._text_under_cursor()
            self._searchWidget._line.setText(word)
            editor.moveCursor(QTextCursor.WordLeft)
            self._searchWidget.find_matches(editor)

    def show_locator(self):
        """Show the status bar with the locator widget."""
        self.current_status = _STATUSBAR_STATE_LOCATOR
        if not self._codeLocator.isVisible():
            self._codeLocator.setVisible(True)
            self.show()
            self._codeLocator.show_suggestions()

    def show_file_opener(self):
        """Show the status bar with the file opener completer widget."""
        self.current_status = _STATUSBAR_STATE_FILEOPENER
        self._fileSystemOpener.setVisible(True)
        self.show()
        self._fileSystemOpener.pathLine.setFocus()

    def hide_status(self):
        """Hide the Status Bar and its widgets."""
        self.hide()
        self._searchWidget._checkSensitive.setCheckState(Qt.Unchecked)
        self._searchWidget._checkWholeWord.setCheckState(Qt.Unchecked)
        self._searchWidget.setVisible(False)
        self._replaceWidget.setVisible(False)
        self._codeLocator.setVisible(False)
        self._fileSystemOpener.setVisible(False)
        main_container = IDE.get_service("main_container")
        widget = None
        if main_container:
            widget = main_container.get_current_widget()
        if widget:
            widget.setFocus()


class SearchWidget(QWidget):

    """Search widget component, search for text inside the editor."""

    def __init__(self, parent=None):
        super(SearchWidget, self).__init__(parent)
        hSearch = QHBoxLayout(self)
        hSearch.setContentsMargins(0, 0, 0, 0)
        self._checkSensitive = QCheckBox(translations.TR_SEARCH_CASE_SENSITIVE)
        self._checkWholeWord = QCheckBox(translations.TR_SEARCH_WHOLE_WORDS)
        self._line = TextLine(self)
        self._line.setMinimumWidth(250)
        self._btnClose = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self._btnClose.setIconSize(QSize(16, 16))
        self._btnFind = QPushButton(QIcon(":img/find"), '')
        self._btnFind.setIconSize(QSize(16, 16))
        self.btnPrevious = QPushButton(
            self.style().standardIcon(QStyle.SP_ArrowLeft), '')
        self.btnPrevious.setIconSize(QSize(16, 16))
        self.btnPrevious.setToolTip(self.trUtf8("Press %s") %
                resources.get_shortcut("Find-previous").toString(
                    QKeySequence.NativeText))
        self.btnNext = QPushButton(
            self.style().standardIcon(QStyle.SP_ArrowRight), '')
        self.btnNext.setIconSize(QSize(16, 16))
        self.btnNext.setToolTip(self.trUtf8("Press %s") %
                resources.get_shortcut("Find-next").toString(
                    QKeySequence.NativeText))
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

        self.connect(self._btnFind, SIGNAL("clicked()"),
            self.find_next)
        self.connect(self.btnNext, SIGNAL("clicked()"),
            self.find_next)
        self.connect(self.btnPrevious, SIGNAL("clicked()"),
            self.find_previous)
        self.connect(self._checkSensitive, SIGNAL("stateChanged(int)"),
            self._checks_state_changed)
        self.connect(self._checkWholeWord, SIGNAL("stateChanged(int)"),
            self._checks_state_changed)

        IDE.register_service('status_search', self)

    def install(self):
        """Install SearchWidget as a service and its shortcuts."""
        self.hide()
        ide = IDE.get_service('ide')

        ui_tools.install_shortcuts(self, actions.ACTIONS_STATUS_SEARCH, ide)

    @property
    def search_text(self):
        """Return the text entered by the user."""
        return self._line.text()

    @property
    def sensitive_checked(self):
        """Return the value of the sensitive checkbox."""
        return self._checkSensitive.isChecked()

    @property
    def wholeword_checked(self):
        """Return the value of the whole word checkbox."""
        return self._checkWholeWord.isChecked()

    def _checks_state_changed(self):
        """Checkboxs state changed, update search."""
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            editor.moveCursor(QTextCursor.Start)
            self.find_matches(editor)

    def contents_changed(self, editor):
        """Editor content changed, update search."""
        #TODO: Find where the cursor is when finding to position the index
        current_index = self.find_matches(editor, True)
        if self.totalMatches >= current_index:
            self.index = current_index
        self._line.counter.update_count(self.index, self.totalMatches)

    def find(self, direction=0, findNext=False):
        """Collect flags and execute search in the editor."""
        s = 0 if not self.sensitive_checked \
            else QTextDocument.FindCaseSensitively
        w = 0 if not self.wholeword_checked else QTextDocument.FindWholeWords
        flags = s + w + direction
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            editor.find_match(self.search_text, flags, findNext)

    def find_next(self):
        """Find the next occurrence of the word to search."""
        self.find(findNext=True)
        if self.totalMatches > 0 and self.index < self.totalMatches:
            self.index += 1
        elif self.totalMatches > 0:
            self.index = 1
        self._line.counter.update_count(self.index, self.totalMatches)

    def find_previous(self):
        """Find the previous occurrence of the word to search."""
        self.find(direction=1, findNext=True)
        if self.totalMatches > 0 and self.index > 1:
            self.index -= 1
        elif self.totalMatches > 0:
            self.index = self.totalMatches
            main_container = IDE.get_service("main_container")
            editor = None
            if main_container:
                editor = main_container.get_current_editor()
            if editor:
                editor.moveCursor(QTextCursor.End)
                self.find(direction=1, findNext=True)
        self._line.counter.update_count(self.index, self.totalMatches)

    def find_matches(self, editor, in_place=False):
        """Check the matches for the word and update the counter and text."""
        if editor is None:
            return
        text = editor.toPlainText()
        search = self._line.text()
        hasSearch = len(search) > 0
        current_index = 0
        if self._checkWholeWord.isChecked():
            pattern = r'\b%s\b' % search
            temp_text = ' '.join(re.findall(pattern, text, re.IGNORECASE))
            text = temp_text if temp_text != '' else text
        if self._checkSensitive.isChecked():
            self.totalMatches = text.count(search)
        else:
            self.totalMatches = text.lower().count(search.lower())
        if hasSearch and self.totalMatches > 0:
            cursor = editor.textCursor()
            cursor_position = cursor.position()

            cursor.movePosition(QTextCursor.WordLeft)
            cursor.movePosition(QTextCursor.Start,
                QTextCursor.KeepAnchor)
            current_index = text[:cursor_position].count(search)
            text = cursor.selectedText()
            if current_index <= self.totalMatches:
                self.index = current_index
            else:
                self.index = text.count(search) + 1
        else:
            self.index = 0
            self.totalMatches = 0
        self._line.counter.update_count(self.index, self.totalMatches,
            hasSearch)
        if hasSearch and not in_place:
            self.find()
        return current_index


class ReplaceWidget(QWidget):

    """Replace widget to find and replace occurrences of words in editor."""

    def __init__(self, parent=None):
        super(ReplaceWidget, self).__init__(parent)
        hReplace = QHBoxLayout(self)
        hReplace.setContentsMargins(0, 0, 0, 0)
        self._lineReplace = QLineEdit()
        self._lineReplace.setMinimumWidth(250)
        self._btnCloseReplace = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self._btnCloseReplace.setIconSize(QSize(16, 16))
        self._btnReplace = QPushButton(self.trUtf8("Replace"))
        self._btnReplaceAll = QPushButton(self.trUtf8("Replace All"))
        self._btnReplaceSelection = QPushButton(
            self.trUtf8("Replace Selection"))
        hReplace.addWidget(self._btnCloseReplace)
        hReplace.addWidget(self._lineReplace)
        hReplace.addWidget(self._btnReplace)
        hReplace.addWidget(self._btnReplaceAll)
        hReplace.addWidget(self._btnReplaceSelection)

        self.connect(self._btnReplace, SIGNAL("clicked()"),
            self.replace)
        self.connect(self._btnReplaceAll, SIGNAL("clicked()"),
            self.replace_all)
        self.connect(self._btnReplaceSelection, SIGNAL("clicked()"),
            self.replace_selected)

    def replace(self):
        """Replace one occurrence of the word."""
        status_search = IDE.get_service("status_search")
        s = 0 if not status_search.sensitive_checked \
            else QTextDocument.FindCaseSensitively
        w = 0 if not status_search.wholeword_checked \
            else QTextDocument.FindWholeWords
        flags = 0 + s + w
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            editor.replace_match(status_search.search_text,
                self._lineReplace.text(), flags)
        if editor and not editor.textCursor().hasSelection():
            status_search.find()

    def replace_selected(self):
        """Replace the occurrences of the word in the selected blocks."""
        self.replace_all(True)

    def replace_all(self, selected=False):
        """Replace all the occurrences of the word."""
        status_search = IDE.get_service("status_search")
        s = 0 if not status_search.sensitive_checked \
            else QTextDocument.FindCaseSensitively
        w = 0 if not status_search.wholeword_checked \
            else QTextDocument.FindWholeWords
        flags = 0 + s + w
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            editor.replace_match(status_search.search_text,
                self._lineReplace.text(), flags, True,
                selected)


class TextLine(QLineEdit):

    """Special Line Edit component for handle searches."""

    def __init__(self, parent=None):
        super(TextLine, self).__init__(parent)
        self.counter = ui_tools.LineEditCount(self)

    def keyPressEvent(self, event):
        """Handle keyPressEvent for this special QLineEdit."""
        main_container = IDE.get_service("main_container")
        if main_container:
            editor = main_container.get_current_editor()

        if main_container is None or editor is None:
            super(TextLine, self).keyPressEvent(event)
            return

        status_search = IDE.get_service("status_search")
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            status_search.find_next()
            return
        super(TextLine, self).keyPressEvent(event)
        if (int(event.key()) in range(32, 162) or
                event.key() == Qt.Key_Backspace):
            status_bar = IDE.get_service("status_bar")
            in_replace_mode = False
            if status_bar:
                in_replace_mode = (status_bar.current_status ==
                                   _STATUSBAR_STATE_REPLACE)
            if not in_replace_mode:
                status_search.find_matches(editor)


class FileSystemOpener(QWidget):

    """Widget to handle opening files through path write with completion."""

    def __init__(self):
        super(FileSystemOpener, self).__init__()
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.btnClose = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self.btnClose
        self.completer = QCompleter(self)
        self.pathLine = ui_tools.LineEditTabCompleter(self.completer)
        fileModel = QFileSystemModel(self.completer)
        fileModel.setRootPath("")
        self.completer.setModel(fileModel)
        self.pathLine.setCompleter(self.completer)
        self.btnOpen = QPushButton(
            self.style().standardIcon(QStyle.SP_ArrowRight), 'Open!')
        hbox.addWidget(self.btnClose)
        hbox.addWidget(QLabel(self.trUtf8("Path:")))
        hbox.addWidget(self.pathLine)
        hbox.addWidget(self.btnOpen)

        self.connect(self.pathLine, SIGNAL("returnPressed()"),
            self._open_file)
        self.connect(self.btnOpen, SIGNAL("clicked()"),
            self._open_file)

    def _open_file(self):
        """Open the file selected."""
        path = self.pathLine.text()
        main_container = IDE.get_service("main_container")
        if main_container:
            main_container.open_file(path)
            self.emit(SIGNAL("requestHide()"))

    def showEvent(self, event):
        """Show the FileSystemOpener widget and select all the text."""
        super(FileSystemOpener, self).showEvent(event)
        self.pathLine.selectAll()


#Register StatusBar
status = _StatusBar()
