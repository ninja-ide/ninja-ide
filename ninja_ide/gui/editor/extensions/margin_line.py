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

""" Right margin """

from PyQt5.QtGui import (
    QPainter,
    QColor,
    QFontMetricsF
)
from PyQt5.QtCore import QRect
from ninja_ide.gui.editor.extensions import base


class RightMargin(base.Extension):
    """Displays a right margin at column the specified position"""

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, new_pos):
        if new_pos != self.__position:
            self.__position = new_pos
            self.update()

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, new_color):
        if new_color != self.__color:
            self.__color = new_color
            self.update()

    @property
    def background(self) -> bool:
        return self.__background

    @background.setter
    def background(self, value):
        if self.__background != value:
            self.__background = value
            self.update()

    def __init__(self):
        super().__init__()
        self.__position = 79  # Default position
        self.__color = QColor("gray")
        self.__color.setAlpha(50)
        self.__background_color = QColor("gray")
        self.__background_color.setAlpha(10)
        self.__background = False

    def update(self):
        self._neditor.viewport().update()

    def install(self):
        self._neditor.painted.connect(self.draw)
        self.update()

    def shutdown(self):
        self._neditor.painted.disconnect(self.draw)
        self.update()

    def draw(self):
        painter = QPainter(self._neditor.viewport())
        painter.setPen(self.__color)
        metrics = QFontMetricsF(self._neditor.font())
        doc_margin = self._neditor.document().documentMargin()
        offset = self._neditor.contentOffset().x() + doc_margin
        x = round(metrics.width(' ') * self.__position) + offset
        if self.__background:
            width = self._neditor.viewport().width() - x
            rect = QRect(x, 0, width, self._neditor.height())
            painter.fillRect(rect, self.__background_color)
        painter.drawLine(x, 0, x, self._neditor.height())
