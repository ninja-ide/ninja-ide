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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPen,
    QFontMetrics
)
from PyQt5.QtCore import Qt, QSize
from ninja_ide.gui.editor import side_area
from ninja_ide import resources


class LineNumberArea(side_area.SideArea):
    """
    Line number area Widget
    """
    LEFT_MARGIN = 5
    RIGHT_MARGIN = 3

    def __init__(self, neditor):
        side_area.SideArea.__init__(self, neditor)
        self.neditor = neditor
        self._color_unselected = QColor(
            resources.get_color('SidebarForeground'))
        self._color_selected = QColor("#6a6ea9")  # FIXME: based on palette
        self.__width = self.__calculate_width()
        self.neditor.blockCountChanged.connect(self.__update_width)

    def sizeHint(self):
        return QSize(self.__calculate_width(), 0)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        width = self.width() - self.RIGHT_MARGIN - self.LEFT_MARGIN
        height = self.neditor.fontMetrics().height()
        font = self.neditor.font()
        font_bold = self.neditor.font()
        font_bold.setBold(True)
        pen = QPen(self._color_unselected)
        pen_selected = QPen(self._color_selected)
        painter.setFont(font)
        sel_start, sel_end = self.neditor.selection_range()
        has_sel = sel_start != sel_end
        current_line, _ = self.neditor.cursor_position
        # Draw visible blocks
        for top, line, block in self.neditor.visible_blocks:
            # Set bold to current line and selected lines
            if ((has_sel and sel_start <= line <= sel_end) or
                    (not has_sel and current_line == line)):
                painter.setPen(pen_selected)
                painter.setFont(font_bold)
            else:
                painter.setPen(pen)
                painter.setFont(font)
            painter.drawText(self.LEFT_MARGIN, top, width, height,
                             Qt.AlignRight, str(line + 1))

    def __calculate_width(self):
        digits = len(str(max(1, self.neditor.blockCount())))
        fmetrics_width = QFontMetrics(
            self.neditor.document().defaultFont()).width('9')

        return self.LEFT_MARGIN + fmetrics_width * digits + self.RIGHT_MARGIN

    def __update_width(self):
        width = self.__calculate_width()
        if width != self.__width:
            self.__width = width
            self.neditor.update_viewport()

    def width(self):
        return self.__width

    def setFont(self, font):
        QWidget.setFont(self, font)
        self.__update_width()
