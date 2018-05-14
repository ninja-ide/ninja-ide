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

from PyQt5.QtWidgets import QPlainTextEdit
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QAbstractSlider
# from PyQt5.QtWidgets import QListView
# from PyQt5.QtWidgets import QFrame

from PyQt5.QtGui import QTextBlockUserData
from PyQt5.QtGui import QTextDocument
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QTextCursor

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.editor.mixin import EditorMixin


class BaseEditor(QPlainTextEdit, EditorMixin):

    zoomChanged = pyqtSignal(int)

    def __init__(self):
        QPlainTextEdit.__init__(self)
        EditorMixin.__init__(self)
        # Word separators
        # Can be used by code completion and the link emulator
        self.word_separators = "`~!@#$%^&*()-=+[{]}\\|;:'\",.<>/?"
        # Style
        self.__init_style()
        self.__apply_style()
        self.__visible_blocks = []

    @property
    def visible_blocks(self):
        return self.__visible_blocks

    @property
    def background_color(self):
        """Get or set the background color.

        :param color: Color to set (name or hexa).
        :type color: QColor or str.
        :return: Background color.
        :rtype: QColor."""

        return self._background_color

    @background_color.setter
    def background_color(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self._background_color = color
        # Refresh stylesheet
        self.__apply_style()

    @property
    def foreground_color(self):
        """Get or set the foreground color.
        :param color: Color to set (name or hexa).
        :type color: QColor or str.
        :return: Foreground color.
        :rtype: QColor"""

        return self._foreground_color

    @foreground_color.setter
    def foreground_color(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self._foreground_color = color
        self.__apply_style()

    def __init_style(self):
        self._background_color = QColor(
            resources.COLOR_SCHEME.get("editor.background"))
        #     resources.get_color('editor.background'))
        self._foreground_color = QColor(
            resources.COLOR_SCHEME.get("editor.foreground"))
        #     resources.get_color('editor.foreground'))
        self._selection_color = QColor(
            resources.COLOR_SCHEME.get("editor.selection.foreground"))
        #     resources.get_color('EditorSelectionColor'))
        self._selection_background_color = QColor(
            resources.COLOR_SCHEME.get("editor.selection.background"))
        #     resources.get_color('EditorSelectionBackground'))

    def __apply_style(self):
        palette = self.palette()
        palette.setColor(palette.Base, self._background_color)
        palette.setColor(palette.Text, self._foreground_color)
        palette.setColor(palette.HighlightedText, self._selection_color)
        palette.setColor(palette.Highlight,
                         self._selection_background_color)
        self.setPalette(palette)

    def paintEvent(self, event):
        self._update_visible_blocks()
        super().paintEvent(event)

    def _update_visible_blocks(self):
        """Updates the list of visible blocks"""

        self.__visible_blocks.clear()
        append = self.__visible_blocks.append

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        editor_height = self.height()
        while block.isValid():
            visible = bottom <= editor_height
            if not visible:
                break
            if block.isVisible():
                append((top, block_number, block))
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

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

    def line_from_position(self, position):
        height = self.fontMetrics().height()
        for top, line, block in self.__visible_blocks:
            if top <= position <= top + height:
                return line
        return -1

    def scroll_step_up(self):
        self.verticalScrollBar().triggerAction(
            QAbstractSlider.SliderSingleStepSub)

    def scroll_step_down(self):
        self.verticalScrollBar().triggerAction(
            QAbstractSlider.SliderSingleStepAdd)

    def __enter__(self):
        self.textCursor().beginEditBlock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.textCursor().endEditBlock()

    def word_under_cursor(self, cursor=None, ignore=None):
        """Returns QTextCursor that contains a word under passed cursor
        or actual cursor"""
        if cursor is None:
            cursor = self.textCursor()
        word_separators = self.word_separators
        if ignore is not None:
            word_separators = [w for w in self.word_separators
                               if w not in ignore]
        start_pos = end_pos = cursor.position()
        while not cursor.atStart():
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            selected_text = cursor.selectedText()
            if not selected_text:
                break
            char = selected_text[0]
            if (selected_text in word_separators and (
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
            if (selected_text in word_separators and (
                    selected_text != "n" and selected_text != "t") or
                    char.isspace()):
                break
            end_pos = cursor.position()
            cursor.setPosition(end_pos)
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        return cursor

    def user_data(self, block=None):
        if block is None:
            block = self.textCursor().block()
        user_data = block.userData()
        if user_data is None:
            user_data = BlockUserData()
            block.setUserData(user_data)
        return user_data

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
        # # Update all side widgets
        # self.side_widgets.update_viewport()

    def reset_zoom(self):
        font = self.default_font
        default_point_size = settings.FONT.pointSize()
        if font.pointSize() != default_point_size:
            font.setPointSize(default_point_size)
            self.set_font(font)
            # Emit signal for indicator
            self.zoomChanged.emit(100)
        # # Update all side widgets
        # self.side_widgets.update_viewport()

    def remove_trailing_spaces(self):
        cursor = self.textCursor()
        block = self.document().findBlockByLineNumber(0)
        with self:
            while block.isValid():
                text = block.text()
                if text.endswith(' '):
                    cursor.setPosition(block.position())
                    cursor.select(QTextCursor.LineUnderCursor)
                    cursor.insertText(text.rstrip())
                block = block.next()

    def insert_block_at_end(self):
        last_line = self.line_count() - 1
        text = self.line_text(last_line)
        if text:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertBlock()

    def text_before_cursor(self, text_cursor=None):
        if text_cursor is None:
            text_cursor = self.textCursor()
        text_block = text_cursor.block().text()
        return text_block[:text_cursor.positionInBlock()]


class BlockUserData(QTextBlockUserData):
    """Representation of the data for a block"""

    def __init__(self):
        QTextBlockUserData.__init__(self)
        self.attrs = {}

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def __getitem__(self, name):
        return self.attrs[name]

    def __setitem__(self, name, value):
        self.attrs[name] = value
