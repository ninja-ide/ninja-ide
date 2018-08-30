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

import re
import sys
import sre_constants
from collections import OrderedDict

from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QToolTip

from PyQt5.QtGui import QTextCursor
# from PyQt5.QtGui import QTextDocument
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QKeySequence

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QEvent

from ninja_ide import resources
from ninja_ide.tools import utils
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
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
# from ninja_ide.gui.editor.extensions import calltip
# Side
from ninja_ide.gui.editor.side_area import manager
from ninja_ide.gui.editor.side_area import line_number_widget
from ninja_ide.gui.editor.side_area import text_change_widget
from ninja_ide.gui.editor.side_area import code_folding
from ninja_ide.gui.editor.side_area import marker_widget

# TODO: separte this module and create a editor component


class NEditor(base_editor.BaseEditor):

    goToDefRequested = pyqtSignal("PyQt_PyObject")
    painted = pyqtSignal("PyQt_PyObject")
    keyPressed = pyqtSignal("PyQt_PyObject")
    keyReleased = pyqtSignal("PyQt_PyObject")
    postKeyPressed = pyqtSignal("PyQt_PyObject")
    addBackItemNavigation = pyqtSignal()
    editorFocusObtained = pyqtSignal()
    # FIXME: cambiar nombre
    cursor_position_changed = pyqtSignal(int, int)
    current_line_changed = pyqtSignal(int)

    _MAX_CHECKER_SELECTIONS = 150  # For good performance

    def __init__(self, neditable):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self._neditable = neditable
        self.allow_word_wrap(False)
        self.setMouseTracking(True)
        self.setCursorWidth(2)
        self.__encoding = None
        self._highlighter = None
        self._last_line_position = 0
        # Extra Selections
        self._extra_selections = ExtraSelectionManager(self)
        # Load indenter based on language
        self._indenter = indenter.load_indenter(self, neditable.language())
        # Widgets on side area
        self.side_widgets = manager.SideWidgetManager(self)

        self.__link_pressed = False

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
        # Calltips
        # self.register_extension(calltip.CallTips)
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

        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.blockCountChanged.connect(self.update)

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

        from ninja_ide.gui.editor import intellisense_assistant as ia
        self._iassistant = None
        intellisense = IDE.get_service("intellisense")
        if intellisense is not None:
            if intellisense.provider_services(self._neditable.language()):
                self._iassistant = ia.IntelliSenseAssistant(self)

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

    @property
    def extra_selections(self):
        return self._extra_selections

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

    def insertFromMimeData(self, source):
        if self.isReadOnly():
            return
        text = source.text()
        if not text:
            return
        cursor = self.textCursor()
        with self:
            cursor.removeSelectedText()
            cursor.insertText(text)
            self.setTextCursor(cursor)

    def update_current_line_in_scrollbar(self, current_line):
        """Update current line highlight in scrollbar"""

        self._scrollbar.remove_marker('current_line')
        if self._scrollbar.maximum() > 0:
            self._scrollbar.add_marker(
                "current_line", current_line, "white", priority=2)

    def show_line_numbers(self, value):
        self._line_number_widget.setVisible(value)

    def show_text_changes(self, value):
        self._text_change_widget.setVisible(value)

    def __clear_occurrences(self):
        self.__word_occurrences.clear()
        self._extra_selections.remove("occurrences")

    def highlight_selected_word(self):
        """Highlight word under cursor"""

        # Clear previous selections
        self.__clear_occurrences()
        if self._extra_selections.get("find"):
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
        self._extra_selections.add("occurrences", selections)

    def clear_found_results(self):
        self._scrollbar.remove_marker("find")
        self._extra_selections.remove("find")

    def highlight_found_results(self, text, cs=False, wo=False):
        """Highlight all found results from find/replace widget"""

        index, results = self._get_find_index_results(text, cs=cs, wo=wo)
        selections = []
        append = selections.append
        color = resources.COLOR_SCHEME.get("editor.search.result")
        for start, end in results:
            selection = extra_selection.ExtraSelection(
                self.textCursor(),
                start_pos=start,
                end_pos=end
            )
            selection.set_background(color)
            selection.set_foreground(utils.get_inverted_color(color))
            append(selection)
            line = selection.cursor.blockNumber()
            self._scrollbar.add_marker("find", line, color)
        self._extra_selections.add("find", selections)

        return index, len(results)

    def _highlight_checkers(self, neditable):
        """Add checker selections to the Editor"""
        # Remove selections if they exists
        self._extra_selections.remove("checker")
        self._scrollbar.remove_marker("checker")
        # Get checkers from neditable
        checkers = neditable.sorted_checkers
        selections = []
        append = selections.append  # Reduce name look-ups for better speed
        for items in checkers:
            checker, color, _ = items
            lines = list(checker.checks.keys())
            lines.sort()
            for line in lines[:self._MAX_CHECKER_SELECTIONS]:
                cursor = self.textCursor()
                # Scrollbar marker
                self._scrollbar.add_marker("checker", line, color, priority=1)
                ms = checker.checks[line]
                for (col_start, col_end), _, _ in ms:
                    selection = extra_selection.ExtraSelection(
                        cursor,
                        start_line=line,
                        col_start=col_start,
                        col_end=col_end
                    )
                    selection.set_underline(color)
                    append(selection)
        self._extra_selections.add("checker", selections)

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
        # self.font_antialiasing(settings.FONT_ANTIALIASING)
        self.side_widgets.resize()
        self.side_widgets.update_viewport()
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

    def viewportEvent(self, event):
        if event.type() == QEvent.ToolTip:
            pos = event.pos()
            tc = self.cursorForPosition(pos)
            block = tc.block()
            line = block.layout().lineForTextPosition(tc.positionInBlock())
            if line.isValid():
                if pos.x() <= self.blockBoundingRect(block).left() + \
                        line.naturalTextRect().right():
                    column = tc.positionInBlock()
                    line = self.line_from_position(pos.y())
                    checkers = self._neditable.sorted_checkers
                    for items in checkers:
                        checker, _, _ = items
                        messages_for_line = checker.message(line)
                        if messages_for_line is not None:
                            for (start, end), message, content in \
                                    messages_for_line:
                                if column >= start and column <= end:
                                    QToolTip.showText(
                                        self.mapToGlobal(pos), message, self)
                    return True
                QToolTip.hideText()
        return super().viewportEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if event.reason() == Qt.MouseFocusReason:
            self.editorFocusObtained.emit()

    def dropEvent(self, event):
        if event.type() == Qt.ControlModifier and self.has_selection:
            insertion_cursor = self.cursorForPosition(event.pos())
            insertion_cursor.insertText(self.selected_text())
        else:
            super().dropEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        self.painted.emit(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.side_widgets.resize()
        self.side_widgets.update_viewport()
        self.adjust_scrollbar_ranges()

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

    def is_keyword(self, text):
        import keyword
        return text in keyword.kwlist

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.modifiers() == Qt.ControlModifier:
            if event.button() == Qt.LeftButton:
                if self.__link_pressed:
                    cursor = self.cursorForPosition(event.pos())
                    self._go_to_definition_requested(cursor)

    def _go_to_definition_requested(self, cursor):
        text = self.word_under_cursor(cursor).selectedText()
        # self._iassistant.definitions(text)
        if text and not self.inside_string_or_comment(cursor):
            self._iassistant.invoke("definitions")

    def _update_link(self, mouse_event):
        if mouse_event.modifiers() == Qt.ControlModifier:
            cursor = self.cursorForPosition(mouse_event.pos())
            text = self.word_under_cursor(cursor).selectedText()
            if self.inside_string_or_comment(cursor) or self.is_keyword(text):
                return
            if not text:
                self.clear_link()
                return
            self.show_link(cursor)
            self.viewport().setCursor(Qt.PointingHandCursor)
            return

        self.clear_link()

    def show_link(self, cursor):
        start_s, end_s = cursor.selectionStart(), cursor.selectionEnd()
        selection = extra_selection.ExtraSelection(
            cursor,
            start_pos=start_s,
            end_pos=end_s
        )
        link_color = resources.COLOR_SCHEME.get("editor.link.navigate")
        selection.set_underline(link_color, style=1)
        selection.set_foreground(link_color)
        self._extra_selections.add("link", selection)
        self.__link_pressed = True

    def clear_link(self):
        self._extra_selections.remove("link")
        self.viewport().setCursor(Qt.IBeamCursor)
        self.__link_pressed = False

    def wheelEvent(self, event):
        # Avoid scrolling the editor when the completions view is displayed
        if self._iassistant is not None:
            if self._iassistant._proposal_widget is not None:
                if not self._iassistant._proposal_widget.isVisible():
                    super().wheelEvent(event)
            else:
                super().wheelEvent(event)
        else:
            super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        if self._highlighter is not None:
            self._update_link(event)
        # Restore mouse cursor if settings say hide while typing
        if self.viewport().cursor().shape() == Qt.BlankCursor:
            self.viewport().setCursor(Qt.IBeamCursor)
        super(NEditor, self).mouseMoveEvent(event)

    def is_modifier(self, key_event):
        key = key_event.key()
        modifiers = (Qt.Key_Shift, Qt.Key_Control, Qt.Key_Meta, Qt.Key_Alt)
        if key in modifiers:
            return True
        return False

    def keyReleaseEvent(self, event):
        self.keyReleased.emit(event)
        if event.key() == Qt.Key_Control:
            self.clear_link()
        super().keyReleaseEvent(event)

    def show_tooltip(self, text, position, duration=1000 * 60):
        QToolTip.showText(position, text, self, self.rect(), duration)

    def hide_tooltip(self):
        QToolTip.hideText()

    def current_color(self, cursor=None):
        """Get the sintax highlighting color for the current QTextCursor"""

        if cursor is None:
            cursor = self.textCursor()
        block = cursor.block()
        pos = cursor.position() - block.position()
        layout = block.layout()
        block_formats = layout.additionalFormats()
        if block_formats:
            if cursor.atBlockEnd():
                current_format = block_formats[-1].format
            else:
                current_format = None
                for fmt in block_formats:
                    if (pos >= fmt.start) and (pos < fmt.start + fmt.length):
                        current_format = fmt.format
                if current_format is None:
                    return None
            color = current_format.foreground().color().name()
            return color
        else:
            return None

    def inside_string_or_comment(self, cursor=None):
        """Check if the cursor is inside a comment or string"""
        if self._highlighter is None:
            return False
        if cursor is None:
            cursor = self.textCursor()
        current_color = self.current_color(cursor)
        colors = []
        for k, v in self._highlighter.formats.items():
            if k.startswith("comment") or k.startswith("string"):
                colors.append(v.foreground().color().name())
        if current_color in colors:
            return True
        return False

    def _complete_declaration(self):
        if not self.neditable.language() == "python":
            return
        line, _ = self.cursor_position
        line_text = self.line_text(line - 1).strip()
        pat_class = re.compile("(\\s)*class.+\\:$")
        if pat_class.match(line_text):
            cursor = self.textCursor()
            block = cursor.block()
            init = False
            while block.isValid():
                text = block.text().strip()
                if text and text.startswith("def __init__(self"):
                    init = True
                    break
                block = block.next()
            if init:
                return
            class_name = [name for name in
                          re.split("(\\s)*class(\\s)+|:|\(", line_text)
                          if name is not None and name.strip()][0]

            line, col = self.cursor_position
            indentation = self.line_indent(line) * " "
            init_def = "def __init__(self):"
            definition = "\n{}{}\n{}".format(
                indentation, init_def, indentation * 2
            )
            super_include = ""
            if line_text.find("(") != -1:
                classes = line_text.split("(")
                parents = []
                if len(classes) > 1:
                    parents += classes[1].split(",")
                if len(parents) > 0 and "object):" not in parents:
                    super_include = "super({}, self).__init__()".format(
                        class_name)
                    definition = "\n{}{}\n{}{}\n{}".format(
                        indentation, init_def, indentation * 2,
                        super_include, indentation * 2
                    )
            self.insert_text(definition)

    def keyPressEvent(self, event):
        if not self.is_modifier(event) and settings.HIDE_MOUSE_CURSOR:
            self.viewport().setCursor(Qt.BlankCursor)
        if self.isReadOnly():
            return
        text = event.text()
        if text:
            self.__clear_occurrences()
        event.ignore()
        # Emit a signal then plugins can do something
        self.keyPressed.emit(event)
        if event.matches(QKeySequence.InsertParagraphSeparator):
            cursor = self.textCursor()
            if not self.inside_string_or_comment(cursor):
                self._indenter.indent_block(self.textCursor())
                self._complete_declaration()
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

        # TODO: generalize it with triggers
        # TODO: shortcut
        # force_completion = ctrl and event.key() == Qt.Key_Space
        # if event.key() == Qt.Key_Period or force_completion:
        #     if not self.inside_string_or_comment():
        #         self._intellisense.invoke_completion()
        #         self._intellisense.process("completions")

    def adjust_scrollbar_ranges(self):
        line_spacing = QFontMetrics(self.font()).lineSpacing()
        if line_spacing == 0:
            return
        offset = self.contentOffset().y()
        self._scrollbar.set_visible_range(
            (self.viewport().rect().height() - offset) / line_spacing)
        self._scrollbar.set_range_offset(offset / line_spacing)

    def _get_find_index_results(self, expr, cs, wo):

        text = self.text
        current_index = 0

        if not cs:
            text = text.lower()
            expr = expr.lower()

        expr = re.escape(expr)
        if wo:
            expr = r"\b" + re.escape(expr) + r"\b"

        def find_all_iter(string, sub):
            try:
                reobj = re.compile(sub)
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
        self._extra_selections.add("run_cursor", selection)
        # Clear selection for show correctly the extra selection
        cursor.clearSelection()
        self.setTextCursor(cursor)
        # Remove extra selection after 0.3 seconds
        QTimer.singleShot(
            300, lambda: self._extra_selections.remove("run_cursor"))

    def link(self, clone):
        """Links the clone with its original"""
        # TODO: errro en compute indent
        clone.cursor_position = self.cursor_position
        for kind, selections in self._extra_selections.items():
            clone._extra_selections.add(kind, selections)
        # clone.setDocument(self.document())
        clone.scrollbar().link(self._scrollbar)

    def comment_or_uncomment(self):
        cursor = self.textCursor()
        doc = self.document()
        block_start = doc.findBlock(cursor.selectionStart())
        block_end = doc.findBlock(cursor.selectionEnd()).next()
        key = self.neditable.language()
        card = settings.SYNTAX[key].get("comment", [])[0]
        has_selection = self.has_selection()
        lines_commented = 0
        lines_without_comment = 0
        with self:
            # Save blocks for use later
            temp_start, temp_end = block_start, block_end
            min_indent = sys.maxsize
            comment = True
            card_lenght = len(card)
            # Get operation (comment/uncomment) and the minimum indent
            # of selected lines
            while temp_start != temp_end:
                block_number = temp_start.blockNumber()
                indent = self.line_indent(block_number)
                block_text = temp_start.text().lstrip()
                if not block_text:
                    temp_start = temp_start.next()
                    continue
                min_indent = min(indent, min_indent)
                if block_text.startswith(card):
                    lines_commented += 1
                    comment = False
                elif block_text.startswith(card.strip()):
                    lines_commented += 1
                    comment = False
                    card_lenght -= 1
                else:
                    lines_without_comment += 1
                    comment = True
                temp_start = temp_start.next()

            total_lines = lines_commented + lines_without_comment
            if lines_commented > 0 and lines_commented != total_lines:
                comment = True
            # Comment/uncomment blocks
            while block_start != block_end:
                cursor.setPosition(block_start.position())
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.movePosition(QTextCursor.Right,
                                    QTextCursor.MoveAnchor, min_indent)
                if block_start.text().lstrip():
                    if comment:
                        cursor.insertText(card)
                    else:
                        cursor.movePosition(QTextCursor.Right,
                                            QTextCursor.KeepAnchor,
                                            card_lenght)
                        cursor.removeSelectedText()
                block_start = block_start.next()

            if not has_selection:
                cursor.movePosition(QTextCursor.Down)
                self.setTextCursor(cursor)


class ExtraSelectionManager(object):

    def __init__(self, neditor):
        self._neditor = neditor
        self.__selections = OrderedDict()

    def __len__(self):
        return len(self.__selections)

    def __iter__(self):
        return iter(self.__selections)

    def __getitem__(self, kind):
        return self.__selections[kind]

    def get(self, kind):
        return self.__selections.get(kind, [])

    def add(self, kind, selection):
        """Adds a extra selection on a editor instance"""
        if not isinstance(selection, list):
            selection = [selection]
        self.__selections[kind] = selection
        self.update()

    def remove(self, kind):
        """Removes a extra selection from the editor"""
        if kind in self.__selections:
            self.__selections[kind].clear()
            self.update()

    def items(self):
        return self.__selections.items()

    def remove_all(self):
        for kind in self:
            self.remove(kind)

    def update(self):
        selections = []
        for kind, selection in self.__selections.items():
            selections.extend(selection)
        selections = sorted(selections, key=lambda sel: sel.order)
        self._neditor.setExtraSelections(selections)


def create_editor(neditable=None):
    neditor = NEditor(neditable)
    language = neditable.language()
    if language is None:
        # For python files without the extension
        # FIXME: Move to another module
        # FIXME: Generalize it?
        for line in neditor.text.splitlines():
            if not line.strip():
                continue
            if line.startswith("#!"):
                shebang = line[2:]
                if "python" in shebang:
                    language = "python"
            else:
                break
    neditor.register_syntax_for(language)
    return neditor
