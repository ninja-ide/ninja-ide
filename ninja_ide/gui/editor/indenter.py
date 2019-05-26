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
# Based on https://github.com/DSpeckhals/python-indent

# from ninja_ide.gui.editor.base_inde import base
from PyQt5.QtGui import QTextCursor
from ninja_ide.core import settings
from ninja_ide.tools.logger import NinjaLogger
# Logger
logger = NinjaLogger(__name__)


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


class PythonIndenter(BaseIndenter):
    """PEP8 indenter for Python"""
    LANG = 'python'

    def _compute_indent(self, cursor):
        # At this point, the new block has added
        block = cursor.block()
        line = self._neditor.textCursor().blockNumber()
        # Source code at current position
        text = self._neditor.get_text()[:cursor.position()]
        current_indent = self.block_indent(block.previous())

        # Parse text
        results = self.__parse_text(text)
        # Get result of parsed text
        bracket_stack, last_closed_line, should_hang, last_colon_line = results
        logger.debug(results)

        if should_hang:
            cursor = self._neditor.textCursor()
            text = cursor.block().text()
            next_char = ""
            if (len(text) > 0):
                next_char = text[0]

            if len(next_char) > 0 and next_char in "}])":
                cursor.insertBlock()
                cursor.insertText(current_indent)
                cursor.movePosition(cursor.Up)
                self._neditor.setTextCursor(cursor)
            else:
                cursor.insertText(current_indent)

            cursor.insertText(current_indent + self.text())
            return

        if not bracket_stack:
            if last_closed_line:
                if last_closed_line[1] == line - 1:
                    indent_level = self.line_indent(last_closed_line[0])
                    if last_colon_line == line - 1:
                        indent_level += self.width
                    return indent_level * " "
                else:
                    text_stripped = block.previous().text().strip()
                    if text_stripped in ("break", "continue", "raise", "pass",
                                         "return") or \
                            text_stripped.startswith("raise ") or \
                            text_stripped.startswith("return "):
                        return " " * (len(current_indent) - self.width)
            else:
                text_stripped = block.previous().text().strip()
                if text_stripped in ("break", "continue", "raise", "pass",
                                     "return") or \
                        text_stripped.startswith("raise ") or \
                        text_stripped.startswith("return "):
                    return " " * (len(current_indent) - self.width)

            last_previous_char = block.previous().text()[-1]
            if last_previous_char == ":":
                return self.text() + current_indent
            return self.block_indent(block.previous())

        last_open_bracket = bracket_stack.pop()

        have_closed_bracket = len(last_closed_line) > 0
        just_opened_bracket = last_open_bracket[0] == line - 1
        just_closed_bracket = have_closed_bracket and \
            last_closed_line[1] == line - 1

        v = have_closed_bracket and last_closed_line[0] > last_open_bracket[0]
        if not just_opened_bracket and not just_closed_bracket:
            return current_indent
        elif just_closed_bracket and v:
            previous_indent = self.line_indent(last_closed_line[0])
            indent_col = previous_indent
        else:
            indent_col = last_open_bracket[1] + 1
        return indent_col * " "

    def __parse_text(self, text):
        # [line, column] pairs describing where open brackets are
        open_bracket = []
        # Describing the lines where the last bracket to be closed was
        # opened and closed
        last_close_line = []
        # The last line a def/for/if/elif/else/try/except block started
        last_colon_line = None
        # Indicating wheter or not a hanging indent is needed
        should_hang = False

        for lineno, line in enumerate(text.splitlines()):
            last_last_colon_line = last_colon_line
            for col, char in enumerate(line):
                if char in '{[(':
                    open_bracket.append([lineno, col])
                    should_hang = True
                else:
                    should_hang = False
                    last_colon_line = last_last_colon_line
                    if char == ':':
                        last_colon_line = lineno
                    elif char in '}])' and open_bracket:
                        opened_row = open_bracket.pop()[0]
                        if lineno != opened_row:
                            last_close_line = [opened_row, lineno]
        return (open_bracket, last_close_line, should_hang, last_colon_line)
