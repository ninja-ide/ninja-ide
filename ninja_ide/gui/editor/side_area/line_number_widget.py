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


class LineNumberWidget(side_area.SideWidget):
    """
    Line number area Widget
    """
    LEFT_MARGIN = 5
    RIGHT_MARGIN = 3

    def __init__(self):
        side_area.SideWidget.__init__(self)
        self._color_unselected = QColor(
            resources.get_color('SidebarForeground'))
        self._color_selected = QColor(resources.get_color('CurrentLineNumber'))

    def sizeHint(self):
        return QSize(self.__calculate_width(), 0)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        width = self.width() - self.RIGHT_MARGIN - self.LEFT_MARGIN
        height = self._neditor.fontMetrics().height()
        font = self._neditor.font()
        font_bold = self._neditor.font()
        font_bold.setBold(True)
        pen = QPen(self._color_unselected)
        pen_selected = QPen(self._color_selected)
        painter.setFont(font)
        sel_start, sel_end = self._neditor.selection_range()
        has_sel = sel_start != sel_end
        current_line, _ = self._neditor.cursor_position
        # Draw visible blocks
        for top, line, block in self._neditor.visible_blocks:
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
        digits = len(str(max(1, self._neditor.blockCount())))
        fmetrics_width = QFontMetrics(
            self._neditor.document().defaultFont()).width('9')

        return self.LEFT_MARGIN + fmetrics_width * digits + self.RIGHT_MARGIN
