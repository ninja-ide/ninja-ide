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
from PyQt5.QtGui import QTextCursor


class Indenter(object):

    WIDTH = 4
    USE_TABS = False

    def __init__(self, neditor):
        self._neditor = neditor
        self.width = self.WIDTH
        self.use_tabs = self.USE_TABS

    def text(self) -> str:
        """Returns indent text as \t or string of spaces"""

        if self.USE_TABS:
            return '\t'
        return ' ' * self.WIDTH

    def auto_indent(self):
        raise NotImplementedError

    def indent(self):
        cursor = self._neditor.textCursor()
        if self.USE_TABS:
            to_insert = self.text()
        else:
            text = cursor.block().text()
            text_before_cursor = text[:cursor.positionInBlock()]
            to_insert = self.WIDTH - (len(text_before_cursor)) % self.WIDTH
            to_insert *= " "
        cursor.insertText(to_insert)

    def indent_selection(self):
        def indent_block(block):
            cursor = QTextCursor(block)
            indentation = self.__block_indentation(block)
            cursor.setPosition(block.position() + len(indentation))
            cursor.insertText(self.text())

        cursor = self._neditor.textCursor()
        start_block = self._neditor.document().findBlock(
            cursor.selectionStart())
        end_block = self._neditor.document().findBlock(
            cursor.selectionEnd())

        with self._neditor:
            if start_block != end_block:
                stop_block = end_block.next()
                # Indent multiple lines
                block = start_block
                while block != stop_block:
                    indent_block(block)
                    block = block.next()
                new_cursor = QTextCursor(start_block)
                new_cursor.setPosition(
                    end_block.position() + len(end_block.text()),
                    QTextCursor.KeepAnchor)
                self._neditor.setTextCursor(new_cursor)
            else:
                # Indent one line
                indent_block(start_block)

    @staticmethod
    def __block_indentation(block):
        """Returns indentation level of block"""
        text = block.text()
        return text[:len(text) - len(text.lstrip())]

    def unindent(self):
        cursor = self._neditor.textCursor()
        start_block = self._neditor.document().findBlock(
            cursor.selectionStart())
        end_block = self._neditor.document().findBlock(
            cursor.selectionEnd())

        position = cursor.position()
        if position == 0:
            return

        if start_block != end_block:
            # Unindent multiple lines
            block = start_block
            stop_block = end_block.next()
            while block != stop_block:
                indentation = self.__block_indentation(block)
                if indentation.endswith(self.text()):
                    cursor = QTextCursor(block)
                    cursor.setPosition(block.position() + len(indentation))
                    cursor.setPosition(cursor.position() - self.WIDTH,
                                       QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()
                block = block.next()
        else:
            # Unindent one line
            indentation = self.__block_indentation(start_block)
            cursor = QTextCursor(start_block)
            cursor.setPosition(start_block.position() + len(indentation))
            cursor.setPosition(cursor.position() - self.WIDTH,
                               QTextCursor.KeepAnchor)
            cursor.removeSelectedText()


class BasicIndenter(Indenter):
    """Basic indenter"""

    def __init__(self, neditor):
        super().__init__(neditor)

    def auto_indent(self):
        cursor = self._neditor.textCursor()
        previous_block = cursor.block().previous()
        text = previous_block.text()
        indent = len(text) - len(text.lstrip())
        cursor.insertText(" " * indent)
