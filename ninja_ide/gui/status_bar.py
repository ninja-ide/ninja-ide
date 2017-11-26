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

from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.tools import ui_tools
from ninja_ide.tools.locator import locator_widget
from ninja_ide.gui import actions
from ninja_ide.gui.ide import IDE
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.status_bar')
DEBUG = logger.debug


_STATUSBAR_STATE_SEARCH = "SEARCH"
_STATUSBAR_STATE_REPLACE = "REPLACE"
_STATUSBAR_STATE_LOCATOR = "LOCATOR"
_STATUSBAR_STATE_FILEOPENER = "FILEOPENER"


class _StatusBar(QWidget):

    """StatusBar widget to be used in the IDE for several purposes."""

    def __init__(self):
        super(_StatusBar, self).__init__()
        self.current_status = _STATUSBAR_STATE_SEARCH

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        if settings.IS_MAC_OS:
            vbox.setSpacing(0)
        else:
            vbox.setSpacing(3)
        #Search Layout
        self._searchWidget = SearchWidget()
        vbox.addWidget(self._searchWidget)
        #Replace Layout
        self._replaceWidget = ReplaceWidget()
        vbox.addWidget(self._replaceWidget)
        self._replaceWidget.setVisible(False)
        #File system completer
        self._fileSystemOpener = FileSystemOpener()
        vbox.addWidget(self._fileSystemOpener)
        self._fileSystemOpener.setVisible(False)

        # Not Configurable Shortcuts
        shortEscStatus = QShortcut(QKeySequence(Qt.Key_Escape), self)

        shortEscStatus.activated.connect(self.hide_status)
        self._searchWidget._btnClose.clicked['bool'].connect(lambda s: self.hide_status())
        self._replaceWidget._btnCloseReplace.clicked['bool'].connect(lambda s: self._replaceWidget.setVisible(False))
        self._fileSystemOpener.btnClose.clicked['bool'].connect(lambda s: self.hide_status())
        self._fileSystemOpener.requestHide.connect(self.hide_status)

        #Register signals connections
        connections = (
            {'target': 'main_container',
             'signal_name': 'updateLocator',#(QString)
             'slot': self._explore_file_code},
            {'target': 'filesystem',
             'signal_name': 'projectOpened',#(QString)
             'slot': self._explore_code},
            {'target': 'filesystem',
             'signal_name': 'projectClosed',#(QString)
             'slot': self._explore_code},
            )

        IDE.register_signals('status_bar', connections)
        IDE.register_service('status_bar', self)

    def install(self):
        """Install StatusBar as a service."""
        self.hide()
        ide = IDE.getInstance()
        self._codeLocator = locator_widget.LocatorWidget(ide)

        ui_tools.install_shortcuts(self, actions.ACTIONS_STATUS, ide)

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

        if editor and editor.hasSelectedText():
            text = editor.selectedText()
            self._searchWidget._line.setText(text)
            self._searchWidget.find()
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
            self._searchWidget.find()

    def show_locator(self):
        """Show the status bar with the locator widget."""
        if not self._codeLocator.isVisible():
            self._codeLocator.show()

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
        self._fileSystemOpener.setVisible(False)
        main_container = IDE.get_service("main_container")
        widget = None
        if main_container:
            widget = main_container.get_current_editor()
        if widget:
            widget.setFocus()
            if widget == main_container.get_current_editor():
                widget.highlight_selected_word(reset=True)


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
        self.btnPrevious.setToolTip(
            self.tr("Press %s") %
            resources.get_shortcut("Find-previous").toString(
                QKeySequence.NativeText))
        self.btnNext = QPushButton(
            self.style().standardIcon(QStyle.SP_ArrowRight), '')
        self.btnNext.setIconSize(QSize(16, 16))
        self.btnNext.setToolTip(
            self.tr("Press %s") %
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

        self._btnFind.clicked['bool'].connect(self.find)
        self.btnNext.clicked['bool'].connect(self.find_next)
        self.btnPrevious.clicked['bool'].connect(self.find_previous)
        self._checkSensitive.stateChanged[int].connect(self._states_changed)
        self._checkWholeWord.stateChanged[int].connect(self._states_changed)

        IDE.register_service('status_search', self)

    def install(self):
        """Install SearchWidget as a service and its shortcuts."""
        self.hide()
        ide = IDE.getInstance()

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

    def _states_changed(self):
        """Checkboxs state changed, update search."""
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            editor.setCursorPosition(0, 0)
            self.find()

    def find(self, forward=True):
        """Collect flags and execute search in the editor."""
        reg = False
        cs = self.sensitive_checked
        wo = self.wholeword_checked
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            index, matches = editor.find_match(
                self.search_text, reg, cs, wo, forward=forward)
            self._line.counter.update_count(index, matches,
                                            len(self.search_text) > 0)

    def find_next(self):
        """Find the next occurrence of the word to search."""
        self.find()
        if self.totalMatches > 0 and self.index < self.totalMatches:
            self.index += 1
        elif self.totalMatches > 0:
            self.index = 1
        self._line.counter.update_count(self.index, self.totalMatches)

    def find_previous(self):
        """Find the previous occurrence of the word to search."""
        self.find(forward=False)
        if self.totalMatches > 0 and self.index > 1:
            self.index -= 1
        elif self.totalMatches > 0:
            self.index = self.totalMatches
            main_container = IDE.get_service("main_container")
            editor = None
            if main_container:
                editor = main_container.get_current_editor()
            if editor:
                self.find(forward=False)
        self._line.counter.update_count(self.index, self.totalMatches)


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
        self._btnReplace = QPushButton(self.tr("Replace"))
        self._btnReplaceAll = QPushButton(self.tr("Replace All"))
        self._btnReplaceSelection = QPushButton(
            self.tr("Replace Selection"))
        hReplace.addWidget(self._btnCloseReplace)
        hReplace.addWidget(self._lineReplace)
        hReplace.addWidget(self._btnReplace)
        hReplace.addWidget(self._btnReplaceAll)
        hReplace.addWidget(self._btnReplaceSelection)

        self._btnReplace.clicked['bool'].connect(self.replace)
        self._btnReplaceAll.clicked['bool'].connect(self.replace_all)
        self._btnReplaceSelection.clicked['bool'].connect(self.replace_selected)

    def replace(self):
        """Replace one occurrence of the word."""
        status_search = IDE.get_service("status_search")
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            editor.replace_match(status_search.search_text,
                                 self._lineReplace.text())
            status_search.find()

    def replace_selected(self):
        """Replace the occurrences of the word in the selected blocks."""
        self.replace_all(True)

    def replace_all(self, selected=False):
        """Replace all the occurrences of the word."""
        status_search = IDE.get_service("status_search")
        main_container = IDE.get_service("main_container")
        editor = None
        if main_container:
            editor = main_container.get_current_editor()
        if editor:
            editor.replace_match(status_search.search_text,
                                 self._lineReplace.text(), True,
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
            status_search.find()
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
                status_search.find()


class FileSystemOpener(QWidget):

    """Widget to handle opening files through path write with completion."""
    requestHide = pyqtSignal()
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
        hbox.addWidget(QLabel(self.tr("Path:")))
        hbox.addWidget(self.pathLine)
        hbox.addWidget(self.btnOpen)

        self.pathLine.returnPressed.connect(self._open_file)
        self.btnOpen.clicked['bool'].connect(self._open_file)

    def _open_file(self):
        """Open the file selected."""
        path = self.pathLine.text()
        main_container = IDE.get_service("main_container")
        if main_container:
            main_container.open_file(path)
            self.requestHide.emit()

    def showEvent(self, event):
        """Show the FileSystemOpener widget and select all the text."""
        super(FileSystemOpener, self).showEvent(event)
        self.pathLine.selectAll()


#Register StatusBar
status = _StatusBar()
