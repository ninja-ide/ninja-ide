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

from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QShortcut
# from PyQt5.QtWidgets import QCheckBox

from PyQt5.QtGui import QKeySequence

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt

from ninja_ide import translations
from ninja_ide.core import settings
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

# FIXME: translations


class _StatusBar(QWidget):
    """StatusBar widget to used in the IDE for several purposes"""

    def __init__(self):
        super().__init__()
        self.current_status = _STATUSBAR_STATE_SEARCH
        vbox = QVBoxLayout(self)
        title = QLabel(translations.TR_SEARCH_TITLE)
        font = title.font()
        font.setPointSize(9)
        title.setFont(font)
        vbox.addWidget(title)
        spacing = 3
        if settings.IS_MAC_OS:
            spacing = 0
        vbox.setSpacing(spacing)
        # Search Layout
        self._search_widget = SearchWidget()
        vbox.addWidget(self._search_widget)
        # Replace Layout
        self._replace_widget = ReplaceWidget()
        self._replace_widget.hide()
        vbox.addWidget(self._replace_widget)
        # Not configurable shortcuts
        short_esc_status = QShortcut(QKeySequence(Qt.Key_Escape), self)
        short_esc_status.activated.connect(self.hide_status_bar)

        IDE.register_service("status_bar", self)

    def install(self):
        """Install StatusBar as a service"""

        self.hide()
        ide = IDE.get_service("ide")
        ui_tools.install_shortcuts(self, actions.ACTIONS_STATUS, ide)

    def hide_status_bar(self):
        """Hide the Status Bar and its widgets"""

        self.hide()
        self._search_widget.setVisible(False)
        main_container = IDE.get_service("main_container")
        editor = main_container.get_current_editor()
        if editor is not None:
            editor.extra_selections.remove("find")
            editor.scrollbar().remove_marker("find")

    def show_search(self):
        """Show the status bar with search widget"""

        main_container = IDE.get_service("main_container")
        editor = main_container.get_current_editor()
        if editor is not None:
            self.current_status = _STATUSBAR_STATE_SEARCH
            self._search_widget.setVisible(True)
            self.show()
            text = editor.selected_text()
            if not text:
                text = editor.word_under_cursor().selectedText()
            self._search_widget._line_search.setText(text)
            self._search_widget.find()
        self._search_widget._line_search.setFocus()
        self._search_widget._line_search.selectAll()

    def show_replace(self):
        """Show the status bar with search/replace widget"""
        self.current_status = _STATUSBAR_STATE_REPLACE
        self._replace_widget.setVisible(True)
        self.show_search()
        if self._search_widget._line_search.text():
            self._replace_widget._line_replace.setFocus()


class SearchWidget(QWidget):
    """Search widget component, search for text inside the editor"""

    highlightResultsRequested = pyqtSignal("PyQt_PyObject")

    def __init__(self, parent=None):
        super().__init__(parent)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(5, 0, 5, 0)
        # Toggle Buttons
        self._btn_case_sensitive = QPushButton("Aa")
        self._btn_case_sensitive.setToolTip(
            translations.TR_SEARCH_CASE_SENSITIVE)
        self._btn_case_sensitive.setCheckable(True)
        self._btn_case_sensitive.setObjectName("status")
        self._btn_whole_word = QPushButton("WO")
        self._btn_whole_word.setToolTip(translations.TR_SEARCH_WHOLE_WORDS)
        self._btn_whole_word.setCheckable(True)
        self._btn_whole_word.setObjectName("status")
        self._btn_regex = QPushButton(".*")
        self._btn_regex.setToolTip(translations.TR_SEARCH_REGEX)
        self._btn_regex.setCheckable(True)
        self._btn_regex.setObjectName("status")
        self._btn_highlight = QPushButton("\u25A3")
        self._btn_highlight.setCheckable(True)
        self._btn_highlight.setChecked(True)
        self._btn_highlight.setObjectName("status")
        hbox.addWidget(self._btn_case_sensitive)
        hbox.addWidget(self._btn_whole_word)
        hbox.addWidget(self._btn_regex)
        hbox.addWidget(self._btn_highlight)
        # Search line
        self._line_search = TextLine(self)
        self._line_search.setPlaceholderText(translations.TR_LINE_FIND)
        hbox.addWidget(self._line_search)
        # Previous and next search buttons
        self._btn_find_previous = QPushButton(translations.TR_FIND_PREVIOUS)
        hbox.addWidget(self._btn_find_previous)
        self._btn_find_next = QPushButton(translations.TR_FIND_NEXT)
        hbox.addWidget(self._btn_find_next)
        # Connections
        self._line_search.textChanged.connect(self.find)
        self._line_search.returnPressed.connect(self.find_next)
        self._btn_case_sensitive.toggled.connect(self.find)
        self._btn_whole_word.toggled.connect(self.find)
        self._btn_find_next.clicked.connect(self.find_next)
        self._btn_highlight.toggled.connect(self._toggle_highlighting)
        self._btn_find_previous.clicked.connect(self.find_previous)

        IDE.register_service("status_search", self)

    @property
    def search_text(self):
        """Return the text entered by the user"""

        return self._line_search.text()

    @property
    def search_flags(self):
        return (
            self._btn_case_sensitive.isChecked(),
            self._btn_whole_word.isChecked(),
            self._btn_highlight.isChecked()
        )

    def find_next(self):
        self.find(forward=True, rehighlight=False)

    def find_previous(self):
        self.find(backward=True, rehighlight=False)

    def _toggle_highlighting(self, state):
        main_container = IDE.get_service("main_container")
        editor = main_container.get_current_editor()
        if editor is not None:
            cs, wo, _ = self.search_flags
            if state:
                editor.highlight_found_results(self.search_text, cs, wo)
            else:
                editor.clear_found_results()

    @pyqtSlot()
    def find(self, backward=False, forward=False, rehighlight=True):
        """Collect flags and execute search in the editor"""
        main_container = IDE.get_service("main_container")
        editor = main_container.get_current_editor()
        if editor is None:
            return
        cs, wo, highlight = self.search_flags
        index, matches = 0, 0
        found = editor.find_match(self.search_text, cs, wo, backward, forward)
        if found:
            if rehighlight:
                editor.clear_found_results()
                index, matches = editor.highlight_found_results(
                    self.search_text, cs, wo)
        else:
            editor.clear_found_results()
        if matches == 0 and found:
            index, matches = editor._get_find_index_results(
                self.search_text, cs, wo)
            matches = len(matches)
            if index == 1:
                ide = IDE.get_service("ide")
                ide.show_message(translations.TR_SEARCH_FROM_TOP)
        self._line_search.counter.update_count(
            index, matches, len(self.search_text) > 0)


class ReplaceWidget(QWidget):
    """Replace widget to find and replace occurrences of words in editor"""

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(5, 0, 5, 0)
        self._line_replace = TextLine()
        self._line_replace.setPlaceholderText(translations.TR_LINE_REPLACE)
        self._line_replace._mode = _STATUSBAR_STATE_REPLACE
        hbox.addWidget(self._line_replace)
        self._btn_replace = QPushButton(translations.TR_LINE_REPLACE)
        hbox.addWidget(self._btn_replace)
        self._btn_replace_all = QPushButton(translations.TR_REPLACE_ALL)
        hbox.addWidget(self._btn_replace_all)
        self._btn_replace_selection = QPushButton(
            translations.TR_REPLACE_SELECTION)
        hbox.addWidget(self._btn_replace_selection)

        self._btn_replace.clicked.connect(self._replace)
        self._btn_replace_all.clicked.connect(self._replace_all)
        self._btn_replace_selection.clicked.connect(self._replace_selection)
        self._line_replace.returnPressed.connect(self._replace)

        IDE.register_service("status_replace", self)

    def _replace(self):
        """Replace one occurrence of the word"""

        status_search = IDE.get_service("status_search")
        cs, wo, highlight = status_search.search_flags
        main_container = IDE.get_service("main_container")
        editor_widget = main_container.get_current_editor()
        editor_widget.replace_match(
            status_search.search_text, self._line_replace.text(), cs, wo)

    def _replace_selection(self):
        """Replace the occurrences of the word in the selected blocks"""
        self._replace_all(selected=True)

    def _replace_all(self, selected=False):
        """Replace all the occurrences of the word"""

        status_search = IDE.get_service("status_search")
        cs, wo, highlight = status_search.search_flags
        main_container = IDE.get_service("main_container")
        editor_widget = main_container.get_current_editor()
        editor_widget.replace_all(
            status_search.search_text, self._line_replace.text(), cs, wo)
        editor_widget.extra_selections.remove("find")


'''
class _StatusBar(ui_tools.StyledBar):
    """StatusBar widget to be used in the IDE for several purposes"""

    def __init__(self):
        QWidget.__init__(self)
        self.current_status = _STATUSBAR_STATE_SEARCH

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(5, 5, 5, 5)
        title = QLabel(translations.TR_SEARCH_TITLE)
        font = title.font()
        font.setPointSize(9)
        title.setFont(font)
        vbox.addWidget(title)
        spacing = 3
        if settings.IS_MAC_OS:
            spacing = 0
        vbox.setSpacing(spacing)
        # Search Layout
        self._search_widget = SearchWidget()
        vbox.addWidget(self._search_widget)
        # Replace Layout
        self._replace_widget = ReplaceWidget()
        vbox.addWidget(self._replace_widget)
        self._replace_widget.setVisible(False)

        # Not Configurable Shortcuts
        short_esc_status = QShortcut(QKeySequence(Qt.Key_Escape), self)
        short_esc_status.activated.connect(self.hide_status_bar)

        IDE.register_service("status_bar", self)

    def install(self):
        """ Install Status Bar as a service """

        self.hide()
        ide = IDE.get_service("ide")
        ui_tools.install_shortcuts(self, actions.ACTIONS_STATUS, ide)

    def show_search(self):
        """Show the status bar with search widget"""

        self.current_status = _STATUSBAR_STATE_SEARCH
        self._search_widget.setVisible(True)
        self.show()
        line = self._search_widget._line
        line.setFocus()
        main_container = IDE.get_service("main_container")
        # if main_container is not None:
        editor = main_container.get_current_editor()
        if editor is not None:
            text = editor.selected_text()
            line.setText(text)
            line.selectAll()

    def show_replace(self):
        """ Show the status bar with search/replace widget """

        self.current_status = _STATUSBAR_STATE_REPLACE
        self._replace_widget.setVisible(True)
        self.show_search()

    def hide_status_bar(self):
        """ Hide the Status Bar and its widgets """

        self.hide()
        self._search_widget.setVisible(False)
        self._replace_widget.setVisible(False)


class SearchWidget(QWidget):
    """Search widget component, search for text inside the editor"""

    MAX_HIGHLIGHTED_OCCURRENCES = 500

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(5, 0, 5, 0)
        self._line = TextLine(self)
        self._line.setPlaceholderText(translations.TR_LINE_FIND)
        self._line.textChanged.connect(self._request_search)
        hbox.addWidget(self._line)
        self._btn_find_previous = QToolButton(self)
        self._btn_find_previous.setText("Find Previous")
        hbox.addWidget(self._btn_find_previous)
        self._btn_find_next = QToolButton(self)
        self._btn_find_next.setText("Find Next")
        hbox.addWidget(self._btn_find_next)
        self._check_sensitive = QCheckBox(
            translations.TR_SEARCH_CASE_SENSITIVE)
        hbox.addWidget(self._check_sensitive)
        self._check_whole_word = QCheckBox(
            translations.TR_SEARCH_WHOLE_WORDS)
        hbox.addWidget(self._check_whole_word)
        self._btn_find_previous.clicked.connect(self.find_previous)
        self._btn_find_next.clicked.connect(self.find_next)
        self._check_sensitive.stateChanged.connect(self._states_changed)
        self._check_whole_word.stateChanged.connect(self._states_changed)

        IDE.register_service("status_search", self)

    def install(self):
        """ Install SearchWidget as a service and its shortcuts """

        ide = IDE.get_service("ide")
        ui_tools.install_shortcuts(self, actions.ACTIONS_STATUS_SEARCH, ide)

    @property
    def search_text(self):
        """ Return the text entered by the user """

        return self._line.text()

    def _request_search(self):
        cs = self._check_sensitive.isChecked()
        wo = self._check_whole_word.isChecked()
        self._execute_search(self.search_text, (cs, wo))

    def _execute_search(self, text, flags):
        main_container = IDE.get_service("main_container")
        editor = main_container.get_current_editor()
        if editor is not None:
            cs, wo = flags
            index, matches = editor.find_matches(
                text,
                case_sensitive=cs,
                whole_word=wo,
                backward=False,
                find_next=False
            )
            self._line.counter.update_count(index, len(matches), len(text) > 0)

    def find(self, backward=False, find_next=False):
        """Collect flags and execute search in the editor"""

        cs = self._check_sensitive.isChecked()
        wo = self._check_whole_word.isChecked()
        main_container = IDE.get_service("main_container")
        if main_container is not None:
            editor = main_container.get_current_editor()
            if editor is not None:
                search = self.search_text
                # if not search:
                #    return
                index, matches = editor.find_matches(search,
                                                     case_sensitive=cs,
                                                     whole_word=wo,
                                                     backward=backward,
                                                     find_next=find_next)
                self._line.counter.update_count(index, len(matches),
                                                len(search) > 0)

    def find_next(self):
        """ Find the next occurence of the word to search """

        self.find(find_next=True)

    def find_previous(self):
        """ Find the previous occurence of the word to search """

        self.find(backward=True)

    def _states_changed(self):
        """ Checkboxs state changed, update search """

        main_container = IDE.get_service("main_container")
        if main_container is not None:
            editor = main_container.get_current_editor()
            if editor is not None:
                editor.cursor_position = (0, 0)
                self.find()


class ReplaceWidget(QWidget):
    """ Replace widget to find and replace occurrences of words in editor """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(5, 0, 5, 0)
        self._line_replace = TextLine()
        self._line_replace.setPlaceholderText(translations.TR_LINE_REPLACE)
        self._line_replace._mode = _STATUSBAR_STATE_REPLACE
        hbox.addWidget(self._line_replace)
        self._btn_replace = QToolButton(self)
        self._btn_replace.setText(translations.TR_LINE_REPLACE)
        hbox.addWidget(self._btn_replace)
        self._btn_replace_all = QToolButton(self)
        self._btn_replace_all.setText(translations.TR_REPLACE_ALL)
        hbox.addWidget(self._btn_replace_all)
        self._btn_replace_selection = QToolButton(self)
        self._btn_replace_selection.setText(translations.TR_REPLACE_SELECTION)
        hbox.addWidget(self._btn_replace_selection)

        self._btn_replace.clicked.connect(self.replace)
        self._btn_replace_all.clicked.connect(self.replace_all)
        self._btn_replace_selection.clicked.connect(self.replace_selection)

    def replace(self):
        """ Replace one occurrence of the word """

        status_search = IDE.get_service("status_search")
        main_container = IDE.get_service("main_container")
        if main_container is not None:
            editor = main_container.get_current_editor()
            editor.replace_match(status_search.search_text,
                                 self._line_replace.text())
            status_search.find_next()

    def replace_selection(self):
        """ Replace the occurrences of the word in the selected blocks """

        self.replace_all(True)

    def replace_all(self, selected=False):
        """ Replace all the occurences of the word """

        status_search = IDE.get_service("status_search")
        cs = status_search._check_sensitive.isChecked()
        wo = status_search._check_whole_word.isChecked()
        main_container = IDE.get_service("main_container")
        if main_container is not None:
            editor = main_container.get_current_editor()
            editor.replace_match(status_search.search_text,
                                 self._line_replace.text(),
                                 cs=cs, wo=wo, all_words=True,
                                 selection=selected)

'''


class TextLine(QLineEdit):
    """ Special Line Edit component for handle searches """

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self.counter = ui_tools.LineEditCount(self)
        self._mode = _STATUSBAR_STATE_SEARCH
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if self._mode == _STATUSBAR_STATE_SEARCH:
                status_replace = IDE.get_service("status_replace")
                if event.key() == Qt.Key_Tab and status_replace.isVisible():
                    status_replace._line_replace.setFocus()
                    return True
        return super().eventFilter(obj, event)

    """
    def keyPressEvent(self, event):
        # Handle keyPressEvent for this special QLineEdit

        # FIXME: handle key tab
        if self._mode != _STATUSBAR_STATE_SEARCH:
            QLineEdit.keyPressEvent(self, event)
            return
        main_container = IDE.get_service("main_container")
        if main_container is not None:
            editor = main_container.get_current_editor()

            if editor is None:
                QLineEdit.keyPressEvent(self, event)
                return

            status_search = IDE.get_service("status_search")
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                status_search.find_next()
                return

            QLineEdit.keyPressEvent(self, event)
            if event.key() in range(32, 162) or \
                    event.key() == Qt.Key_Backspace:
                status_bar = IDE.get_service("status_bar")
                in_replace_mode = False
                if status_bar is not None:
                    in_replace_mode = (status_bar.current_status ==
                                       _STATUSBAR_STATE_REPLACE)
                if not in_replace_mode:
                    status_search.find()
    """


# Register StatusBar
status_bar = _StatusBar()

'''
class _StatusBar(QWidget):

    """StatusBar widget to be used in the IDE for several purposes."""

    def __init__(self):
        super(_StatusBar, self).__init__()
        self.current_status = _STATUSBAR_STATE_SEARCH

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(5, 5, 5, 5)
        if settings.IS_MAC_OS:
            vbox.setSpacing(0)
        else:
            vbox.setSpacing(3)
        # Search Layout
        self._searchWidget = SearchWidget()
        vbox.addWidget(self._searchWidget)
        # Replace Layout
        self._replaceWidget = ReplaceWidget()
        vbox.addWidget(self._replaceWidget)
        self._replaceWidget.setVisible(False)
        # File system completer
        self._fileSystemOpener = FileSystemOpener()
        vbox.addWidget(self._fileSystemOpener)
        self._fileSystemOpener.setVisible(False)

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

        # Register signals connections
        connections = (
            {'target': 'main_container',
             'signal_name': 'updateLocator(QString)',
             'slot': self._explore_file_code},
            {'target': 'filesystem',
             'signal_name': 'projectOpened(QString)',
             'slot': self._explore_code},
            {'target': 'filesystem',
             'signal_name': 'projectClosed(QString)',
             'slot': self._explore_code},
            )

        IDE.register_signals('status_bar', connections)
        IDE.register_service('status_bar', self)

    def install(self):
        """Install StatusBar as a service."""
        self.hide()
        ide = IDE.get_service('ide')
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

        if editor and editor.selected_text():
            text = editor.selected_text()
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
            widget = main_container.get_current_widget()
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
        # self._btnClose = QPushButton(
        #    self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        # self._btnClose.setIconSize(QSize(16, 16))
        self._btnClose = QToolButton(self)
        self._btnClose.setIcon(
            self.style().standardIcon(QStyle.SP_DialogCloseButton))
        # self._btnFind = QPushButton(QIcon(":img/find"), '')
        # self._btnFind.setIconSize(QSize(14, 14))
        # self._btnFind = QToolButton(self)
        # self._btnFind.setText("Find")
        # self.btnPrevious = QPushButton(
        #    self.style().standardIcon(QStyle.SP_ArrowLeft), '')
        # self.btnPrevious.setIconSize(QSize(16, 16))
        # self.btnPrevious.setToolTip(
        #    self.trUtf8("Press %s") %
        #    resources.get_shortcut("Find-previous").toString(
        #        QKeySequence.NativeText))
        self.btnPrevious = QToolButton(self)
        self.btnPrevious.setText("Find Previous")
        # self.btnNext = QPushButton(
        #    self.style().standardIcon(QStyle.SP_ArrowRight), '')
        # self.btnNext.setIconSize(QSize(16, 16))
        # self.btnNext.setToolTip(
        #    self.trUtf8("Press %s") %
        #    resources.get_shortcut("Find-next").toString(
        #        QKeySequence.NativeText))
        self.btnNext = QToolButton(self)
        self.btnNext.setText("Find Next")
        hSearch.addWidget(self._btnClose)
        hSearch.addWidget(self._line)
        # hSearch.addWidget(self._btnFind)
        hSearch.addWidget(self.btnPrevious)
        hSearch.addWidget(self.btnNext)
        hSearch.addWidget(self._checkSensitive)
        hSearch.addWidget(self._checkWholeWord)

        self.totalMatches = 0
        self.index = 0
        self._line.counter.update_count(self.index, self.totalMatches)

        # self.connect(self._btnFind, SIGNAL("clicked()"),
        #             self.find)
        self.connect(self.btnNext, SIGNAL("clicked()"),
                     self.find_next)
        self.connect(self.btnPrevious, SIGNAL("clicked()"),
                     self.find_previous)
        self.connect(self._checkSensitive, SIGNAL("stateChanged(int)"),
                     self._states_changed)
        self.connect(self._checkWholeWord, SIGNAL("stateChanged(int)"),
                     self._states_changed)

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
            c = editor.textCursor()
            f = editor.find(self.search_text)
            if not f:
                c.movePosition(c.Start)
                editor.setTextCursor(c)
            # index, matches = editor.find_match(
            #    self.search_text, reg, cs, wo, forward=forward)
            # self._line.counter.update_count(index, matches,
            #                                len(self.search_text) > 0)

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
'''
