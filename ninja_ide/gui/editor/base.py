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

"""
Base editor
"""

from PyQt5.QtWidgets import QPlainTextEdit

from PyQt5.QtGui import QTextBlockUserData
from PyQt5.QtGui import QTextDocument
from PyQt5.QtGui import QTextCursor

from PyQt5.QtCore import QPoint


_WORD_SEPARATORS = '`~!@#$%^&*()-=+[{]}\\|;:\'\",.<>/?'


class BaseTextEditor(QPlainTextEdit):

    def __init__(self):
        super().__init__()
        self.word_separators = _WORD_SEPARATORS

    def __enter__(self):
        self.textCursor().beginEditBlock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.textCursor().endEditBlock()

    @property
    def cursor_position(self):
        """Get or set the current cursor position"""

        cursor = self.textCursor()
        return (cursor.blockNumber(), cursor.columnNumber())

    @cursor_position.setter
    def cursor_position(self, position):
        line, column = position
        line = min(line, self.line_count() - 1)
        column = min(column, len(self.line_text(line)))
        cursor = QTextCursor(self.document().findBlockByNumber(line))
        cursor.setPosition(cursor.block().position() + column,
                           QTextCursor.MoveAnchor)
        self.setTextCursor(cursor)

    @property
    def text(self):
        """Get or set the plain text editor's content. The previous contents
        are removed."""

        return self.toPlainText()

    @text.setter
    def text(self, text):
        self.setPlainText(text)

    def line_text(self, line=-1):
        """Returns the text of the specified line"""
        if line == -1:
            line, _ = self.cursor_position
        block = self.document().findBlockByNumber(line)
        return block.text()

    def line_count(self):
        """Returns the number of lines"""

        return self.document().blockCount()

    def line_indent(self, line=-1):
        """Returns the indentation level of `line`"""

        if line == -1:
            line, _ = self.cursor_position
        text = self.line_text(line)
        indentation = len(text) - len(text.lstrip())
        return indentation

    def insert_text(self, text):
        if not self.isReadOnly():
            self.textCursor().insertText(text)

    def first_visible_block(self):
        return self.firstVisibleBlock()

    def last_visible_block(self):
        return self.cursorForPosition(
            QPoint(0, self.viewport().height())).block()

    def selection_range(self):
        """Returns the start and end number of selected lines"""

        text_cursor = self.textCursor()
        start = self.document().findBlock(
            text_cursor.selectionStart()).blockNumber()
        end = self.document().findBlock(
            text_cursor.selectionEnd()).blockNumber()
        if text_cursor.columnNumber() == 0 and start != end:
            end -= 1
        return start, end

    def has_selection(self):
        return self.textCursor().hasSelection()

    def selected_text(self):
        """Returns the selected text"""
        return self.textCursor().selectedText()

    def get_right_word(self):
        """Gets the word on the right of the text cursor"""

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
        return cursor.selectedText().strip()

    def get_right_character(self):
        """Gets the right character on the right of the text cursor"""

        right_word = self.get_right_word()
        right_char = None
        if right_word:
            right_char = right_word[0]
        return right_char

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

    def move_up_down(self, up=False):
        cursor = self.textCursor()
        move = cursor
        with self:
            has_selection = cursor.hasSelection()
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            if has_selection:
                move.setPosition(start)
                move.movePosition(QTextCursor.StartOfBlock)
                move.setPosition(end, QTextCursor.KeepAnchor)
                m = QTextCursor.EndOfBlock
                if move.atBlockStart():
                    m = QTextCursor.Left
                move.movePosition(m, QTextCursor.KeepAnchor)
            else:
                move.movePosition(QTextCursor.StartOfBlock)
                move.movePosition(QTextCursor.EndOfBlock,
                                  QTextCursor.KeepAnchor)

            text = cursor.selectedText()
            move.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            move.removeSelectedText()

            if up:
                move.movePosition(QTextCursor.PreviousBlock)
                move.insertBlock()
                move.movePosition(QTextCursor.Left)
            else:
                move.movePosition(QTextCursor.EndOfBlock)
                if move.atBlockStart():
                    move.movePosition(QTextCursor.NextBlock)
                    move.insertBlock()
                    move.movePosition(QTextCursor.Left)
                else:
                    move.insertBlock()

            start = move.position()
            move.clearSelection()
            move.insertText(text)
            end = move.position()
            if has_selection:
                move.setPosition(end)
                move.setPosition(start, QTextCursor.KeepAnchor)
            else:
                move.setPosition(start)
            self.setTextCursor(move)

    def duplicate_line(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor_at_start = cursor.position() == start
            cursor.setPosition(end)
            cursor.insertText("\n" + text)
            cursor.setPosition(end if cursor_at_start else start)
            cursor.setPosition(start if cursor_at_start else end,
                               QTextCursor.KeepAnchor)
        else:
            position = cursor.position()
            block = cursor.block()
            text = block.text() + "\n"
            cursor.setPosition(block.position())
            cursor.insertText(text)
            cursor.setPosition(position)
        self.setTextCursor(cursor)


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


class CodeEditor(BaseTextEditor):

    def __init__(self):
        super().__init__()
        self.__visible_blocks = []

    @property
    def visible_blocks(self):
        return self.__visible_blocks

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

    def user_data(self, block=None):
        if block is None:
            block = self.textCursor().block()
        user_data = block.userData()
        if user_data is None:
            user_data = BlockUserData()
            block.setUserData(user_data)
        return user_data

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
