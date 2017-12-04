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
    QFontMetrics,
    QPainter,
    QColor
)
from PyQt5.QtCore import (
    QSize,
    Qt
)
from ninja_ide.gui.editor import side_area


class MarkerArea(side_area.SideArea):

    @property
    def breakpoints(self):
        return self.__breakpoints

    def __init__(self, editor):
        side_area.SideArea.__init__(self, editor)
        self.setMouseTracking(True)
        self._editor = editor
        self.__breakpoints = []
        self.__line_hovered = -1

    def width(self):
        return self.sizeHint().width()

    def sizeHint(self):
        font_metrics = QFontMetrics(self._editor.font())
        size = QSize(font_metrics.height(), font_metrics.height())
        return size

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Get line number from position
            y_pos = event.pos().y()
            line = self._editor.line_from_position(y_pos)
            if line not in self.__breakpoints:
                # Add marker
                self.__breakpoints.append(line)
            else:
                # Remove marker
                self.__breakpoints.remove(line)
            self.repaint()

    def leaveEvent(self, event):
        self.__line_hovered = -1
        self.repaint()

    def mouseMoveEvent(self, event):
        line = self._editor.line_from_position(event.pos().y())
        self.__line_hovered = line
        self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        color = QColor("#cc1100")
        r = self.width() - 10
        if self.__line_hovered != -1:
            color.setAlpha(100)
            painter.setPen(color)
            painter.setBrush(color)
            for top, block_number, _ in self._editor.visible_blocks:
                if self.__line_hovered == block_number:
                    painter.drawEllipse(5, top + 3, r, r)
        color.setAlpha(255)
        painter.setPen(color)
        painter.setBrush(color)
        for top, block_number, _ in self._editor.visible_blocks:
            for marker in self.__breakpoints:
                if marker == block_number:
                    painter.drawEllipse(5, top + 3, r, r)
