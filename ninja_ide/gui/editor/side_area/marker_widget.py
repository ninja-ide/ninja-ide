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

import bisect
from PyQt5.QtWidgets import QMenu
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


class MarkerWidget(side_area.SideWidget):

    @property
    def bookmarks(self):
        return sorted(self.__bookmarks)

    def __init__(self):
        side_area.SideWidget.__init__(self)
        self.setMouseTracking(True)
        self.__bookmarks = []
        self.__line_hovered = -1
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu)

    def add_bookmark(self, line):
        self.__bookmarks.append(line)

    def _menu(self, point):
        menu = QMenu(self)
        n = menu.addAction('Next')
        n.triggered.connect(self.next_bookmark)
        p = menu.addAction('Previous')
        p.triggered.connect(self.previous_bookmark)
        menu.exec_(self.mapToGlobal(point))

    def width(self):
        return self.sizeHint().width()

    def next_bookmark(self):
        if self.__bookmarks:
            current_line, col = self._neditor.cursor_position
            index = bisect.bisect(self.bookmarks, current_line)
            try:
                line = self.bookmarks[index]
            except IndexError:
                line = self.bookmarks[0]
            self._neditor.cursor_position = line, col

    def previous_bookmark(self):
        if self.__bookmarks:
            current_line, col = self._neditor.cursor_position
            index = bisect.bisect(self.bookmarks, current_line)
            line = self.bookmarks[index - 1]
            if line == current_line:
                line = self.bookmarks[index - 2]
            self._neditor.cursor_position = line, col

    def sizeHint(self):
        font_metrics = QFontMetrics(self._neditor.font())
        size = QSize(font_metrics.height(), font_metrics.height())
        return size

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Get line number from position
            y_pos = event.pos().y()
            line = self._neditor.line_from_position(y_pos)
            if line not in self.__bookmarks:
                # Add marker
                self.__bookmarks.append(line)
            else:
                # Remove marker
                self.__bookmarks.remove(line)
            self.repaint()

    def leaveEvent(self, event):
        self.__line_hovered = -1
        self.repaint()

    def mouseMoveEvent(self, event):
        line = self._neditor.line_from_position(event.pos().y())
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
            for top, block_number, _ in self._neditor.visible_blocks:
                if self.__line_hovered == block_number:
                    painter.drawEllipse(5, top + 3, r, r)
        color.setAlpha(255)
        painter.setPen(color)
        painter.setBrush(color)
        for top, block_number, _ in self._neditor.visible_blocks:
            for marker in self.__bookmarks:
                if marker == block_number:
                    painter.drawEllipse(5, top + 3, r, r)
