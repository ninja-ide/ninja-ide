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
from ninja_ide.gui.editor.indenter import base
from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.core.settings import INDENT
# Logger
logger = NinjaLogger(__name__)


class HtmlIndenter(base.BaseIndenter):
    """indenter for Html5"""
    LANG = 'html'
    hang = False
    exempted_set = ('<!doctype html>', '<html>', '<!doctype>')
 
    def _compute_indent(self, cursor):
        block = cursor.block()
        line, _ = self._neditor.cursor_position
        # Source code at current position
        text = self._neditor.text[:cursor.position()]
        current_indent = self.block_indent(block.previous())
        indent_level = len(current_indent)

        # get last line
        text_splits = text.split('\n')
        last_line = text_splits[-2]

        self._parse_text(last_line)

        # if indent depth should increase
        if self.hang:
            indent_level += self.width
            indent = ' ' * indent_level

            # reset this so unindent and indent using tab will work properly
            self.width = INDENT
            return indent
        else:
            indent = ' ' * self.width

            # reset this so unindent and indent using tab will work properly
            self.width = INDENT
            return indent


    def _parse_text(self, last_line):
        # if it is a closing tag or a php
        if re.findall('[/|?]', last_line):
            self.hang = False
        else:
            # If it's not a closing tag or an exempted element.
            # this is normacy
            self.hang = True

        # if it is an exempted ele
        for ele in self.exempted_set:
            if re.findall(last_line, ele, 2):
                self.width = 0
                self.hang = False

