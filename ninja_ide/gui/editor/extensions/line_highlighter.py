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
    QColor,
    QPainter,
    QPen
)
from PyQt5.QtCore import Qt
from ninja_ide.gui.editor.extensions import base
from ninja_ide.gui.editor.extra_selection import ExtraSelection
from ninja_ide import resources
from ninja_ide.core import settings


class CurrentLineHighlighter(base.Extension):
    """This extension highlight current line"""

    # Modes
    FULL = 0
    SIMPLE = 1

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, value):
        if value != self.__mode:
            self.shutdown()
            self.__mode = value
            self.install()

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self.__background = color
        self._highlight()

    def __init__(self):
        super().__init__()
        self.__background = QColor(resources.COLOR_SCHEME.get('editor.line'))
        self.__mode = settings.HIGHLIGHT_CURRENT_LINE_MODE

    def install(self):
        if self.__mode == self.SIMPLE:
            self._neditor.painted.connect(self.paint_simple_mode)
            self._neditor.cursorPositionChanged.connect(
                self._neditor.viewport().update)
        else:
            self._neditor.cursorPositionChanged.connect(self._highlight)
            self._highlight()

    def shutdown(self):
        if self.__mode == self.SIMPLE:
            self._neditor.painted.disconnect(self.paint_simple_mode)
            self._neditor.cursorPositionChanged.connect(
                self._neditor.viewport().update)
        else:
            self._neditor.cursorPositionChanged.disconnect(self._highlight)
            self._neditor.clear_extra_selections('current_line')

    def paint_simple_mode(self):
        block = self.text_cursor().block()
        layout = block.layout()
        line_count = layout.lineCount()
        line = layout.lineAt(line_count - 1)
        if line_count < 1:
            # Avoid segmentation fault
            return
        co = self._neditor.contentOffset()
        top = self._neditor.blockBoundingGeometry(block).translated(co).top()
        line_rect = line.naturalTextRect().translated(co.x(), top)
        painter = QPainter(self._neditor.viewport())
        painter.setPen(QPen(self.__background, 1))
        painter.drawLine(line_rect.x(), line_rect.y(), self._neditor.width(),
                         line_rect.y())
        height = self._neditor.fontMetrics().height()
        painter.drawLine(line_rect.x(), line_rect.y() + height,
                         self._neditor.width(), line_rect.y() + height)

    def _highlight(self):
        self._neditor.clear_extra_selections('current_line')
        selection = ExtraSelection(self._neditor.textCursor())
        selection.set_full_width()
        selection.set_background(self.__background)
        self._neditor.add_extra_selections('current_line', [selection])
