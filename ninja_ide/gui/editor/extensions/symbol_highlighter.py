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
from PyQt5.QtGui import QColor

from ninja_ide import resources
from ninja_ide.gui.editor.extensions import base
from ninja_ide.gui.editor.extra_selection import ExtraSelection
# TODO: change colors for all editor clones


class SymbolHighlighter(base.Extension):
    """Symbol Matcher extension for Ninja-IDE Editor"""

    OPEN_SYMBOLS = "([{"
    CLOSED_SYMBOLS = ")]}"
    ALL_SYMBOLS = OPEN_SYMBOLS + CLOSED_SYMBOLS
    SYMBOLS_MAP = dict((k, v) for (k, v) in zip(OPEN_SYMBOLS, CLOSED_SYMBOLS))
    REVERSED_SYMBOL_MAP = dict((k, v) for v, k in SYMBOLS_MAP.items())

    @property
    def matched_background(self):
        """Background color of matching symbol"""

        return self.__matched_background

    @matched_background.setter
    def matched_background(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self.__matched_background = color

    @property
    def unmatched_background(self):
        """Background color of unmatching symbol"""

        return self.__unmatched_background

    @unmatched_background.setter
    def unmatched_background(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self.__unmatched_background = color

    def __init__(self):
        super().__init__()
        self.__matched_background = QColor(
            resources.COLOR_SCHEME.get("editor.brace.matched"))
        self.__unmatched_background = QColor(
            resources.COLOR_SCHEME.get('editor.brace.unmatched'))

    def install(self):
        self._neditor.cursorPositionChanged.connect(self._highlight)

    def shutdown(self):
        self._neditor.cursorPositionChanged.disconnect(self._highlight)

    def _highlight(self):

        self._neditor.extra_selections.remove("matcher")
        cursor = self._neditor.textCursor()
        current_block = cursor.block()
        if self._neditor.inside_string_or_comment(cursor):
            return
        column_index = cursor.positionInBlock()

        if column_index < len(current_block.text()) and \
                current_block.text()[column_index] in self.ALL_SYMBOLS:
            char = current_block.text()[column_index]
        elif column_index > 0 and current_block.text()[column_index - 1] in \
                self.ALL_SYMBOLS:
            char = current_block.text()[column_index - 1]
            column_index -= 1
        else:
            return
        if char in self.OPEN_SYMBOLS:
            generator = self.__iterate_code_forward(current_block,
                                                    column_index + 1)
        else:
            generator = self.__iterate_code_backward(current_block,
                                                     column_index)

        matched_block, matched_index = self.__find_matching_symbol(
            char, generator)

        if matched_block is not None:
            selections = [
                self._make_selection(current_block, column_index, True),
                self._make_selection(matched_block, matched_index, True)
            ]
        else:
            selections = [
                self._make_selection(current_block, column_index, False)
            ]
        self._neditor.extra_selections.add("matcher", selections)

    def _make_selection(self, block, index, matched):
        cur = QTextCursor(block)
        cur.setPosition(block.position() + index)
        cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        selection = ExtraSelection(cur)
        background = self.matched_background
        if not matched:
            background = self.unmatched_background
        selection.set_background(background)
        return selection

    def __get_complementary_symbol(self, symbol):
        complementary = self.SYMBOLS_MAP.get(symbol, None)
        if complementary is None:
            # If the complementary symbol is not found,
            # look at the reverse of the dict
            complementary = self.REVERSED_SYMBOL_MAP[symbol]
        return complementary

    def __find_matching_symbol(self, symbol, generator):
        count = 1
        complementary = self.__get_complementary_symbol(symbol)
        for block, column, char in generator:
            # Check if current position are inside a comment or string
            # cursor = QTextCursor(block)
            # Because positionInBlock() = cursor.position() - block.position()
            # and positionInBlock() = column, then "setPositionInBlock":
            # cursor.setPosition(column + block.position())
            # if self._neditor.inside_string_or_comment(cursor):
            #     continue
            if char == complementary:
                count -= 1
                if count == 0:
                    return block, column
            elif char == symbol:
                count += 1
        else:
            return None, None

    @staticmethod
    def __iterate_code_forward(block, index):
        for col, char in list(enumerate(block.text()))[index:]:
            yield block, col, char
        block = block.next()

        while block.isValid():
            for col, char in list(enumerate(block.text())):
                yield block, col, char
            block = block.next()

    @staticmethod
    def __iterate_code_backward(block, index):
        for col, char in reversed(list(enumerate(block.text()[:index]))):
            yield block, col, char
        block = block.previous()

        while block.isValid():
            for col, char in reversed(list(enumerate(block.text()))):
                yield block, col, char
            block = block.previous()
