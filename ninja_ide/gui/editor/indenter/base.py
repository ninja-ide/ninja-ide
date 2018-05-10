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
from ninja_ide.core import settings


class BaseIndenter(object):

    def __init__(self, neditor):
        self._neditor = neditor  # Editor ref
        self.width = settings.INDENT
        self.use_tabs = settings.USE_TABS

    def text(self):
        """Get indent text as \t or string of spaces"""
        text = " " * self.width
        if self.use_tabs:
            text = "\t"
        return text

    def indent_block(self, cursor):
        """Indent block after enter pressed"""

        at_start_of_line = cursor.positionInBlock() == 0
        with self._neditor:
            cursor.insertBlock()
            if not at_start_of_line:
                indent = self._compute_indent(cursor)
                if indent is not None:
                    cursor.insertText(indent)
                    return True
                return False
        self._neditor.ensureCursorVisible()

    def block_indent(self, block):
        block_text = block.text()
        space_at_start_len = len(block_text) - len(block_text.lstrip())
        return block_text[:space_at_start_len]

    def indent(self):
        """Indent a single line after tab pressed"""
        cursor = self._neditor.textCursor()
        if self.use_tabs:
            to_insert = self.text()
        else:
            text = cursor.block().text()
            text_before_cursor = text[:cursor.positionInBlock()]
            to_insert = self.width - (len(text_before_cursor)) % self.width
            to_insert *= " "
        cursor.insertText(to_insert)

    def indent_selection(self):
        """Indent selection after tab pressed"""

        def indent_block(block):
            cursor = QTextCursor(block)
            indentation = self.block_indent(block)
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

    def line_indent(self, line):
        """Returns the indentation level of `line`"""

        return self._neditor.line_indent(line)

    def _compute_indent(self, cursor):
        raise NotImplementedError


class BasicIndenter(BaseIndenter):
    """Basic indenter"""

    def _compute_indent(self, cursor):
        # At this point, enter was pressed, so the block should be previous
        return self.block_indent(cursor.block().previous())
