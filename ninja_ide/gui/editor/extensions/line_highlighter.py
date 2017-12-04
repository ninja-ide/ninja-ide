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

from PyQt5.QtGui import (
    QColor
)
from ninja_ide.gui.editor.extensions import Extension
from ninja_ide.gui.editor.extra_selection import ExtraSelection
from ninja_ide import resources


class CurrentLineHighlighter(Extension):
    name = 'line_highlighter'
    version = '0.1'

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self.__background = color

    def __init__(self, neditor):
        super().__init__(neditor)
        self.__background = QColor(resources.get_color('CurrentLine'))
        self.__background.setAlpha(40)

    def install(self):
        self._neditor.cursorPositionChanged.connect(self._highlight)

    def shutdown(self):
        self._neditor.cursorPositionChanged.disconnect(self._highlight)

    def _highlight(self):
        self._neditor.clear_extra_selections('current_line')
        selection = ExtraSelection(self._neditor.textCursor())
        selection.set_full_width()
        selection.set_background(self.__background)
        self._neditor.add_extra_selections('current_line', [selection])

