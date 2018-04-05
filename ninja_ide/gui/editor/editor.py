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


# import re
# import sre_constants

# from collections import OrderedDict

# from typing import Tuple
# from PyQt5.QtWidgets import (
#     QPlainTextEdit,
#     QAbstractSlider,
#     QTextEdit
# )
# from PyQt5.QtGui import (
#     QKeyEvent,
#     QTextCursor,
#     QTextBlock,
#     QTextDocument,
#     QKeySequence,
#     QColor,
#     QTextBlockUserData,

#     QFontMetrics,
#     QTextOption,
#     QTextCharFormat,
#     QPaintEvent
# )
# from PyQt5.QtCore import (
#     pyqtSignal,
#     QTimer,
#     pyqtSlot,
#     QPoint,
#     Qt
# )
# from ninja_ide.gui.ide import IDE
# from ninja_ide.gui.editor import (
#     highlighter,
#     scrollbar
# )

# from ninja_ide.gui.editor.side_area import (
#     manager,
#     line_number_widget,
#     text_change_widget,
#     marker_widget,
#     code_folding
#     # lint_area
# )
# from ninja_ide.gui.editor import extra_selection
# from ninja_ide import resources
# from ninja_ide.core import settings
# from ninja_ide.gui.editor.extensions import (
#     line_highlighter,
#     symbol_highlighter,
#     margin_line,
#     indentation_guides,
#     braces,
#     quotes
# )
# from ninja_ide.gui.editor import indenter
# from ninja_ide.tools.logger import NinjaLogger
# logger = NinjaLogger(__name__)

# # FIXME: cursor width and blinking
# # FIXME: clone editor for spliting
import re
import sre_constants
from collections import OrderedDict

from PyQt5.QtWidgets import QFrame

from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QTextDocument
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QKeySequence

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.editor import indenter
from ninja_ide.gui.editor import highlighter
from ninja_ide.gui.editor import base_editor
from ninja_ide.gui.editor import scrollbar
from ninja_ide.gui.editor import extra_selection
# Extensions
from ninja_ide.gui.editor.extensions import symbol_highlighter
from ninja_ide.gui.editor.extensions import line_highlighter
from ninja_ide.gui.editor.extensions import margin_line
from ninja_ide.gui.editor.extensions import indentation_guides
from ninja_ide.gui.editor.extensions import braces
from ninja_ide.gui.editor.extensions import quotes
# Side
from ninja_ide.gui.editor.side_area import manager
from ninja_ide.gui.editor.side_area import line_number_widget
from ninja_ide.gui.editor.side_area import text_change_widget
from ninja_ide.gui.editor.side_area import code_folding
from ninja_ide.gui.editor.side_area import marker_widget


class NEditor(base_editor.BaseEditor):

    zoomChanged = pyqtSignal(int)
    painted = pyqtSignal("PyQt_PyObject")
    keyPressed = pyqtSignal("PyQt_PyObject")
    postKeyPressed = pyqtSignal("PyQt_PyObject")
    addBackItemNavigation = pyqtSignal()
    editorFocusObtained = pyqtSignal()
    # FIXME: cambiar nombre
    cursor_position_changed = pyqtSignal(int, int)
    current_line_changed = pyqtSignal(int)

    def __init__(self, neditable):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self._neditable = neditable
        self.setMouseTracking(True)
        self.__encoding = None
        self._last_line_position = 0
        # List of word separators
        # Can be used by code completion and the link emulator
        self.word_separators = [",", ".", ":", "[", "]", "(", ")", "{", "}"]
        # Extra Selections
        self._extra_selections = OrderedDict()
        self.__link_cursor = QTextCursor()
        # Load indenter based on language
        self._indenter = indenter.load_indenter(self, neditable.language())
        # Set editor font before build lexer
        self.set_font(settings.FONT)
        # Register extensions
        self.__extensions = {}
        # Brace matching
        self._brace_matching = self.register_extension(
            symbol_highlighter.SymbolHighlighter)
        self.brace_matching = settings.BRACE_MATCHING
        # Current line highlighter
        self._line_highlighter = self.register_extension(
            line_highlighter.CurrentLineHighlighter)
        self.highlight_current_line = settings.HIGHLIGHT_CURRENT_LINE
        # Right margin line
        self._margin_line = self.register_extension(margin_line.RightMargin)
        self.margin_line = settings.SHOW_MARGIN_LINE
        self.margin_line_position = settings.MARGIN_LINE
        self.margin_line_background = settings.MARGIN_LINE_BACKGROUND
        # Indentation guides
        self._indentation_guides = self.register_extension(
            indentation_guides.IndentationGuide)
        self.show_indentation_guides(settings.SHOW_INDENTATION_GUIDES)
        # Autocomplete braces
        self.__autocomplete_braces = self.register_extension(
            braces.AutocompleteBraces)
        self.autocomplete_braces(settings.AUTOCOMPLETE_BRACKETS)
        # Autocomplete quotes
        self.__autocomplete_quotes = self.register_extension(
            quotes.AutocompleteQuotes)
        self.autocomplete_quotes(settings.AUTOCOMPLETE_QUOTES)
        # Highlight word under cursor
        self.__word_occurrences = []
        self._highlight_word_timer = QTimer()
        self._highlight_word_timer.setSingleShot(True)
        self._highlight_word_timer.setInterval(1000)
        self._highlight_word_timer.timeout.connect(
            self.highlight_selected_word)
        # Install custom scrollbar
        self._scrollbar = scrollbar.NScrollBar(self)
        self._scrollbar.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setVerticalScrollBar(self._scrollbar)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.additional_builtins = None
        # Set the editor after initialization
        if self._neditable is not None:
            if self._neditable.editor:
                self.setDocument(self._neditable.document)
            else:
                self._neditable.set_editor(self)
            self._neditable.checkersUpdated.connect(self._highlight_checkers)
        # self.register_syntax_for(language=neditable.language())
        # Widgets on side area
        self.side_widgets = manager.SideWidgetManager(self)
        # Mark text changes
        self._text_change_widget = self.side_widgets.add(
            text_change_widget.TextChangeWidget)
        self.show_text_changes(settings.SHOW_TEXT_CHANGES)
        # Breakpoints/bookmarks widget
        self._marker_area = self.side_widgets.add(
            marker_widget.MarkerWidget)
        # Line number widget
        self._line_number_widget = self.side_widgets.add(
            line_number_widget.LineNumberWidget)
        self.show_line_numbers(settings.SHOW_LINE_NUMBERS)
        # Code folding
        self.side_widgets.add(code_folding.CodeFoldingWidget)

        # FIXME: we need a method to initialize
        # self.__set_whitespaces_flags(self.__show_whitespaces)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.blockCountChanged.connect(self.update)

    @property
    def nfile(self):
        return self._neditable.nfile

    @property
    def neditable(self):
        return self._neditable

    @property
    def file_path(self):
        return self._neditable.file_path

    @property
    def is_modified(self):
        return self.document().isModified()

    @property
    def encoding(self):
        if self.__encoding is not None:
            return self.__encoding
        return "utf-8"

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    @property
    def default_font(self):
        return self.document().defaultFont()

    @default_font.setter
    def default_font(self, font):
        super().setFont(font)
        self._update_tab_stop_width()

    @property
    def indentation_width(self):
        return self._indenter.width

    @indentation_width.setter
    def indentation_width(self, width):
        self._indenter.width = width
        self._update_tab_stop_width()

    @pyqtSlot()
    def _on_cursor_position_changed(self):
        # self.__clear_occurrences()
        line, col = self.cursor_position
        self.cursor_position_changed.emit(line, col)
        if line != self._last_line_position:
            self._last_line_position = line
            self.current_line_changed.emit(line)
        # Create marker for scrollbar
        self.update_current_line_in_scrollbar(line)
        # Mark occurrences
        self._highlight_word_timer.stop()
        self._highlight_word_timer.start()

    def scrollbar(self):
        return self._scrollbar

    def update_current_line_in_scrollbar(self, current_line):
        """Update current line highlight in scrollbar"""

        self._scrollbar.remove_marker('current_line')
        if self._scrollbar.maximum() > 0:
            self._scrollbar.add_marker(
                "current_line", current_line, "white", priority=2)

    def is_comment(self, block):
        """Check if the block is a inline comment"""

        text_block = block.text().lstrip()
        return text_block.startswith('#')  # FIXME: generalize it

    def show_line_numbers(self, value):
        self._line_number_widget.setVisible(value)

    def show_text_changes(self, value):
        self._text_change_widget.setVisible(value)

    def highlight_selected_word(self):
        """Highlight word under cursor"""

        # Clear previous selections
        self.__word_occurrences.clear()
        self.clear_extra_selections("occurrences")

        if self.extra_selections("find"):
            # No re-highlight occurrences when have "find" extra selections
            return

        word = self.word_under_cursor().selectedText()
        if not word:
            return

        results = self._get_find_index_results(word, cs=False, wo=True)[1]
        selections = []
        append = selections.append
        # On very big files where a lots of occurrences can be found,
        # this freeze the editor during a few seconds. So, we can limit of 500
        # and make sure the editor will always remain responsive
        for start_pos, end_pos in results[:500]:
            selection = extra_selection.ExtraSelection(
                self.textCursor(),
                start_pos=start_pos,
                end_pos=end_pos
            )
            color = resources.COLOR_SCHEME.get("editor.occurrence")
            selection.set_background(color)
            append(selection)
            # TODO: highlight results in scrollbar
            # FIXME: from settings
            # line = selection.cursor.blockNumber()
            # Marker = scrollbar.marker
            # marker = Marker(line, resources.get_color("SearchResult"), 0)
            # self._scrollbar.add_marker("find", marker)
        self.add_extra_selections("occurrences", selections)

    def highlight_found_results(self, text, cs=False, wo=False):
        """Highlight all found results from find/replace widget"""

        self._scrollbar.remove_marker("find")

        index, results = self._get_find_index_results(text, cs=cs, wo=wo)

        selections = []
        append = selections.append
        for start, end in results:
            selection = extra_selection.ExtraSelection(
                self.textCursor(),
                start_pos=start,
                end_pos=end
            )
            color = resources.COLOR_SCHEME.get("editor.search.result")
            selection.set_outline(color)
            append(selection)
            line = selection.cursor.blockNumber()
            self._scrollbar.add_marker("find", line, color)
        self.add_extra_selections("find", selections)

        return index, len(results)

    def _highlight_checkers(self, neditable):
        """Add checker selections to the Editor"""
        # Remove selections if they exists
        self.clear_extra_selections('checker')
        self._scrollbar.remove_marker("checker")
        # Get checkers from neditable
        checkers = neditable.sorted_checkers

        selections = []
        for items in checkers:
            checker, color, _ = items
            lines = checker.checks.keys()
            for line in lines:
                # Scrollbar marker
                self._scrollbar.add_marker("checker", line, color, priority=1)
                # Extra selection
                msg, col = checker.checks[line]
                selection = extra_selection.ExtraSelection(
                    self.textCursor(),
                    start_line=line,
                    offset=col - 1
                )
                selection.set_underline(color)
                selections.append(selection)

        self.add_extra_selections('checker', selections)

    def reset_selections(self):
        self.clear_extra_selections("find")
        self._scrollbar.remove_marker("find")

    def extra_selections(self, selection_key):
        return self._extra_selections.get(selection_key, [])

    def add_extra_selections(self, selection_key, selections):
        """Adds a extra selection on a editor instance"""
        self._extra_selections[selection_key] = selections
        self.update_extra_selections()

    def clear_extra_selections(self, selection_key):
        """Removes a extra selection from the editor"""
        if selection_key in self._extra_selections:
            self._extra_selections[selection_key] = []
            self.update_extra_selections()

    def update_extra_selections(self):
        extra_selections = []
        for key, selection in self._extra_selections.items():
            extra_selections.extend(selection)
        extra_selections = sorted(extra_selections, key=lambda sel: sel.order)
        self.setExtraSelections(extra_selections)

    def all_extra_selections(self):
        return self._extra_selections

    def show_indentation_guides(self, value):
        self._indentation_guides.actived = value

    def register_extension(self, Extension):
        extension_instance = Extension()
        self.__extensions[Extension.name] = extension_instance
        extension_instance.initialize(self)
        return extension_instance

    def autocomplete_braces(self, value):
        self.__autocomplete_braces.actived = value

    def autocomplete_quotes(self, value):
        self.__autocomplete_quotes.actived = value

    def navigate_bookmarks(self, forward=True):
        if forward:
            self._marker_area.next_bookmark()
        else:
            self._marker_area.previous_bookmark()

    def register_syntax_for(self, language="python", force=False):
        syntax = highlighter.build_highlighter(language)
        if syntax is not None:
            self._highlighter = highlighter.SyntaxHighlighter(
                self.document(),
                syntax.partition_scanner,
                syntax.scanners,
                syntax.context
            )

    def set_font(self, font):
        """Set font and update tab stop width"""

        super().setFont(font)
        self.font_antialiasing(settings.FONT_ANTIALIASING)
        self._update_tab_stop_width()

    def _update_tab_stop_width(self):
        """Update the tab stop width"""

        width = self.fontMetrics().width(' ') * self._indenter.width
        self.setTabStopWidth(width)

    def allow_word_wrap(self, value):
        wrap_mode = wrap_mode = self.NoWrap
        if value:
            wrap_mode = self.WidgetWidth
        self.setLineWrapMode(wrap_mode)

    def font_antialiasing(self, value):
        font = self.default_font
        style = font.PreferAntialias
        if not value:
            style = font.NoAntialias
        font.setStyleStrategy(style)
        self.default_font = font

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.editorFocusObtained.emit()

    def dropEvent(self, event):
        if event.type() == Qt.ControlModifier and self.has_selection:
            insertion_cursor = self.cursorForPosition(event.pos())
            insertion_cursor.insertText(self.selected_text())
        else:
            super().dropEvent(event)

    def paintEvent(self, event):
        self.painted.emit(event)
        super().paintEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.side_widgets.resize()
        self.adjust_scrollbar_ranges()

    def clear_link(self):
        self.clear_extra_selections("link")
        self.viewport().setCursor(Qt.IBeamCursor)
        self.__link_cursor = QTextCursor()

    def __smart_backspace(self):
        accepted = False
        cursor = self.textCursor()
        text_before_cursor = self.text_before_cursor(cursor)
        text = cursor.block().text()
        indentation = self._indenter.text()
        space_at_start_len = len(text) - len(text.lstrip())
        column_number = cursor.positionInBlock()
        if text_before_cursor.endswith(indentation) and \
                space_at_start_len == column_number and \
                not cursor.hasSelection():
            to_remove = len(text_before_cursor) % len(indentation)
            if to_remove == 0:
                to_remove = len(indentation)
            cursor.setPosition(cursor.position() - to_remove,
                               QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            accepted = True
        return accepted

    def __manage_key_home(self, event):
        """Performs home key action"""
        cursor = self.textCursor()
        indent = self.line_indent()
        # For selection
        move = QTextCursor.MoveAnchor
        if event.modifiers() == Qt.ShiftModifier:
            move = QTextCursor.KeepAnchor
        # Operation
        if cursor.positionInBlock() == indent:
            cursor.movePosition(QTextCursor.StartOfBlock, move)
        elif cursor.atBlockStart():
            cursor.setPosition(cursor.block().position() + indent, move)
        elif cursor.positionInBlock() > indent:
            cursor.movePosition(QTextCursor.StartOfLine, move)
            cursor.setPosition(cursor.block().position() + indent, move)
        self.setTextCursor(cursor)
        event.accept()

    def text_before_cursor(self, text_cursor=None):
        if text_cursor is None:
            text_cursor = self.textCursor()
        text_block = text_cursor.block().text()
        return text_block[:text_cursor.positionInBlock()]

    def _text_under_cursor(self):
        text_cursor = self.textCursor()
        text_cursor.select(QTextCursor.WordUnderCursor)
        match = re.findall(r'([^\d\W]\w*)', text_cursor.selectedText())
        if match:
            return match[0]

    def word_under_cursor(self, cursor=None):
        """Returns QTextCursor that contains a word under passed cursor
        or actual cursor"""
        if cursor is None:
            cursor = self.textCursor()
        start_pos = end_pos = cursor.position()
        while not cursor.atStart():
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            selected_text = cursor.selectedText()
            if not selected_text:
                break
            char = selected_text[0]
            if (selected_text in self.word_separators and (
                    selected_text != "n" and selected_text != "t") or
                    char.isspace()):
                break
            start_pos = cursor.position()
            cursor.setPosition(start_pos)
        cursor.setPosition(end_pos)
        while not cursor.atEnd():
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            selected_text = cursor.selectedText()
            if not selected_text:
                break
            char = selected_text[0]
            if (selected_text in self.word_separators and (
                    selected_text != "n" and selected_text != "t") or
                    char.isspace()):
                break
            end_pos = cursor.position()
            cursor.setPosition(end_pos)
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        return cursor

    def mouseMoveEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            cursor = self.cursorForPosition(event.pos())
            cursor = self.word_under_cursor(cursor)
            if self.__link_cursor == cursor:
                return
            if not cursor.selectedText():
                return
            self.__link_cursor = cursor
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            selection = extra_selection.ExtraSelection(
                cursor,
                start_pos=start,
                end_pos=end
            )
            link_color = resources.COLOR_SCHEME.get("editor.link.navigate")
            selection.set_underline(link_color)
            selection.set_foreground(link_color)
            self.add_extra_selections("link", [selection])
            self.viewport().setCursor(Qt.PointingHandCursor)
        else:
            self.clear_link()
        # Restore mouse cursor if settings say hide while typing
        if self.viewport().cursor().shape() == Qt.BlankCursor:
            self.viewport().setCursor(Qt.IBeamCursor)
        '''if event.modifiers() == Qt.ControlModifier:
            if self.__link_selection is not None:
                return
            cursor = self.cursorForPosition(event.pos())
            # Check that the mouse was actually on the text somewhere
            on_text = self.cursorRect(cursor).right() >= event.x()
            if on_text:
                cursor.select(QTextCursor.WordUnderCursor)
                selection_start = cursor.selectionStart()
                selection_end = cursor.selectionEnd()
                self.__link_selection = extra_selection.ExtraSelection(
                    cursor,
                    start_pos=selection_start,
                    end_pos=selection_end
                )
                self.__link_selection.set_underline("red")
                self.__link_selection.set_full_width()
                self.add_extra_selection(self.__link_selection)
                self.viewport().setCursor(Qt.PointingHandCursor)'''
        super(NEditor, self).mouseMoveEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.clear_link()
        #    if self.__link_selection is not None:
        #        self.remove_extra_selection(self.__link_selection)
        #        self.__link_selection = None
        #        self.viewport().setCursor(Qt.IBeamCursor)
        super().keyReleaseEvent(event)

    def keyPressEvent(self, event):
        if settings.HIDE_MOUSE_CURSOR:
            self.viewport().setCursor(Qt.BlankCursor)
        if self.isReadOnly():
            return
        # Emit a signal then plugins can do something
        event.ignore()
        self.keyPressed.emit(event)
        if event.matches(QKeySequence.InsertParagraphSeparator):
            self._indenter.indent_block(self.textCursor())
            return
        if event.key() == Qt.Key_Home:
            self.__manage_key_home(event)
            return
        elif event.key() == Qt.Key_Tab:
            if self.textCursor().hasSelection():
                self._indenter.indent_selection()
            else:
                self._indenter.indent()
            event.accept()
        elif event.key() == Qt.Key_Backspace:
            if not event.isAccepted():
                if self.__smart_backspace():
                    event.accept()
        if not event.isAccepted():
            super().keyPressEvent(event)
        # Post key press
        self.postKeyPressed.emit(event)

    def adjust_scrollbar_ranges(self):
        line_spacing = QFontMetrics(self.font()).lineSpacing()
        if line_spacing == 0:
            return
        offset = self.contentOffset().y()
        self._scrollbar.set_visible_range(
            (self.viewport().rect().height() - offset) / line_spacing)
        self._scrollbar.set_range_offset(offset / line_spacing)

    def go_to_line(self, lineno, column=0, center=True):
        """Go to an specific line

        :param lineno: The line number to go
        :param column: The column number to go
        :param center: If True scrolls the document in order to center the
        cursor vertically.
        :type lineno: int"""

        if self.line_count() >= lineno:
            self.cursor_position = lineno, column
            if center:
                self.centerCursor()
            else:
                self.ensureCursorVisible()
        self.addBackItemNavigation.emit()

    def replace_match(self, word_old, word_new, cs=False, wo=False,
                      wrap_around=True):
        """
        Find if searched text exists and replace it with new one.
        If there is a selection just do it inside it and exit
        """

        cursor = self.textCursor()
        text = cursor.selectedText()
        if not cs:
            word_old = word_old.lower()
            text = text.lower()
        if text == word_old:
            cursor.insertText(word_new)

        # Next
        return self.find_match(word_old, cs, wo, forward=True,
                               wrap_around=wrap_around)

    def replace_all(self, word_old, word_new, cs=False, wo=False):
        # Save cursor for restore later
        cursor = self.textCursor()
        with self:
            # Move to beginning of text and replace all
            self.moveCursor(QTextCursor.Start)
            found = True
            while found:
                found = self.replace_match(word_old, word_new, cs, wo,
                                           wrap_around=False)
        # Reset position
        self.setTextCursor(cursor)

    def find_match(self, search, case_sensitive=False, whole_word=False,
                   backward=False, forward=False, wrap_around=True):

        if not backward and not forward:
            self.moveCursor(QTextCursor.StartOfWord)

        flags = QTextDocument.FindFlags()
        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        if whole_word:
            flags |= QTextDocument.FindWholeWords
        if backward:
            flags |= QTextDocument.FindBackward

        cursor = self.textCursor()
        found = self.document().find(search, cursor, flags)
        if not found.isNull():
            self.setTextCursor(found)

        elif wrap_around:
            if not backward and not forward:
                cursor.movePosition(QTextCursor.Start)
            elif forward:
                cursor.movePosition(QTextCursor.Start)
            else:
                cursor.movePosition(QTextCursor.End)

            # Try again
            found = self.document().find(search, cursor, flags)
            if not found.isNull():
                self.setTextCursor(found)

        return not found.isNull()

    def _get_find_index_results(self, expr, cs, wo):

        text = self.text
        current_index = 0

        if not cs:
            text = text.lower()
            expr = expr.lower()

        if wo:
            expr = r"\b%s\b" % expr

        def find_all_iter(string, sub):
            try:
                reobj = re.compile(re.escape(sub))
            except sre_constants.error:
                return
            for match in reobj.finditer(string):
                yield match.span()

        matches = list(find_all_iter(text, expr))

        if len(matches) > 0:
            position = self.textCursor().position()
            current_index = sum(1 for _ in re.finditer(expr, text[:position]))
        return current_index, matches

    def show_run_cursor(self):
        """Highlight momentarily a piece of code"""

        cursor = self.textCursor()
        if self.has_selection():
            # Get selection range
            start_pos, end_pos = cursor.selectionStart(), cursor.selectionEnd()
        else:
            # If no selected text, highlight current line
            cursor.movePosition(QTextCursor.StartOfLine)
            start_pos = cursor.position()
            cursor.movePosition(QTextCursor.EndOfLine)
            end_pos = cursor.position()
        # Create extra selection
        selection = extra_selection.ExtraSelection(
            cursor,
            start_pos=start_pos,
            end_pos=end_pos
        )
        selection.set_background("gray")
        self.add_extra_selections("run_cursor", [selection])
        # Clear selection for show correctly the extra selection
        cursor.clearSelection()
        self.setTextCursor(cursor)
        # Remove extra selection after 0.3 seconds
        QTimer.singleShot(
            300, lambda: self.clear_extra_selections("run_cursor"))

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if not settings.SCROLL_WHEEL_ZOMMING:
                return
            delta = event.angleDelta().y() / 120.
            if delta != 0:
                self.zoom(delta)
            return
        super().wheelEvent(event)

    def zoom(self, delta: int):
        font = self.default_font
        previous_point_size = font.pointSize()
        new_point_size = int(max(1, previous_point_size + delta))
        if new_point_size != previous_point_size:
            font.setPointSize(new_point_size)
            self.set_font(font)
            # Emit signal for indicator
            default_point_size = settings.FONT.pointSize()
            percent = new_point_size / default_point_size * 100.0
            self.zoomChanged.emit(percent)
        # Update all side widgets
        self.side_widgets.update_viewport()

    def reset_zoom(self):
        font = self.default_font
        default_point_size = settings.FONT.pointSize()
        if font.pointSize() != default_point_size:
            font.setPointSize(default_point_size)
            self.set_font(font)
            # Emit signal for indicator
            self.zoomChanged.emit(100)
        # Update all side widgets
        self.side_widgets.update_viewport()

    def link(self, clone):
        """Links the clone with its original"""
        # TODO: errro en compute indent
        clone.cursor_position = self.cursor_position
        for k, v in self._extra_selections.items():
            clone.add_extra_selections(k, v)
        # clone.setDocument(self.document())
        clone.scrollbar().link(self._scrollbar)


def create_editor(neditable=None):
    neditor = NEditor(neditable)
    # if neditable is not None:
    #    language = neditable.language()
    #    if language is not None:
    #        neditor.register_syntax_for(language=language)

    return neditor
