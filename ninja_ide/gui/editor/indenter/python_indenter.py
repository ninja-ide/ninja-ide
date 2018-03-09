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

from ninja_ide.gui.editor.indenter import base
from ninja_ide.tools.logger import NinjaLogger
# Logger
logger = NinjaLogger(__name__)


class PythonIndenter(base.BaseIndenter):
    """PEP8 indenter for Python"""
    LANG = 'python'

    def _compute_indent(self, cursor):
        # At this point, the new block has added
        block = cursor.block()
        line, _ = self._neditor.cursor_position
        # Source code at current position
        text = self._neditor.text[:cursor.position()]
        current_indent = self.block_indent(block.previous())

        indent = None
        # Parse text
        results = self.__parse_text(text)
        # Get result of parsed text
        bracket_stack, last_closed_line, should_hang, last_colon_line = results
        logger.debug(results)

        if should_hang:
            if block.text():
                if block.text()[0] in "])}":
                    cursor.insertBlock()
                    cursor.insertText(current_indent)
                    cursor.movePosition(cursor.Up)
                    self._neditor.setTextCursor(cursor)
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
        print("1")
        v = have_closed_bracket and last_closed_line[0] > last_open_bracket[0]
        if not just_opened_bracket and not just_closed_bracket:
            print("2")
            return current_indent
        elif just_closed_bracket and v:
            previous_indent = self.line_indent(last_closed_line[0])
            indent_col = previous_indent
            print("4")
        else:
            print("5")
            indent_col = last_open_bracket[1] + 1
        print("6")
        return indent_col * " "
        # if should_hang:
        #     cursor = self._neditor.textCursor()
        #     next_char = cursor.block().text()[0]
        #     if next_char in "}])":
        #         cursor.insertBlock()
        #         cursor.insertText(current_indent)
        #         cursor.movePosition(cursor.Up)
        #         self._neditor.setTextCursor(cursor)
        #     else:
        #         cursor.insertText(current_indent)
        #     cursor.insertText(current_indent + self.text())
        #     return None
        # if (not bracket_stack):
        #     if last_closed_line:
        #         if last_closed_line[1] == line - 1:
        #             # We just closed a bracket on the row, get indentation
        #             # from the row where it was opened
        #             indent_level_at_this_line = self.line_indent(
        #                 last_closed_line[0])
        #             if last_colon_line == line - 1:
        #                 # def/for/if/elif/else/try/except ...
        #                 # need to increase indent level by 1.
        #                 indent_level_at_this_line += self.width
        #             indent = ' ' * indent_level_at_this_line
        #             return indent
        #         else:
        #             text_stripped = block.previous().text().strip()
        #             # Decrease indent when block text contains
        #             # break/raise/pass/return/continue etc
        #             if text_stripped in ("break", "continue", "raise", "pass",
        #                                  "return") or \
        #                     text_stripped.startswith("raise ") or \
        #                     text_stripped.startswith("return "):
        #                 indent = " " * (len(current_indent) - self.width)
        #             else:
        #                 indent = current_indent
        #                 if self._neditor.line_text(line - 1).strip().endswith(':'):
        #                     indent = current_indent + self.text()
        #             return indent
        #     else:
        #         # FIXME: this sucks
        #         if self._neditor.line_text(line - 1).strip().endswith(':'):
        #             return current_indent + self.text()
        #         text_stripped = block.previous().text().strip()
        #         if text_stripped in ("break", "continue", "raise", "pass",
        #                              "return") or \
        #                 text_stripped.startswith("raise ") or \
        #                 text_stripped.startswith("return "):
        #             indent = " " * (len(current_indent) - self.width)
        #         else:
        #             indent = current_indent
        #         return indent

        # last_open_bracket_locations = bracket_stack.pop()
        # have_closed_bracket = True if last_closed_line else False
        # just_opened_bracket = last_open_bracket_locations[0] == line - 1

        # just_closed_bracket = False
        # if have_closed_bracket and last_closed_line[1] == line - 1:
        #     just_closed_bracket = True
        # if not just_opened_bracket and not just_closed_bracket:
        #     return current_indent
        # # last_open_bracket_locations[1] is the column where the bracket was,
        # # so need to bump up the indentation by one
        # indent_col = last_open_bracket_locations[1] + 1
        # indent = indent_col * ' '
        return indent

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
