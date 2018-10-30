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

from PyQt5.QtGui import QTextCursor

from PyQt5.QtCore import QPoint


class BaseTextEditor(QPlainTextEdit):

    def __init__(self):
        super().__init__()

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
