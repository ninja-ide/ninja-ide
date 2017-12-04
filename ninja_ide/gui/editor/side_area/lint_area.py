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

from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import (
    QPainter,
    QColor
)
from ninja_ide.gui.editor import side_area


class LintArea(side_area.SideArea):
    """Shows markes with messages collected by checkers"""

    def __init__(self, editor):
        super().__init__(editor)
        self.setMouseTracking(True)
        self._editor = editor
        self.__checkers = None
        self._editor.highlight_checker_updated.connect(self.__update)
        self.__messages = {}

    def __update(self, checkers):
        # self.__checkers = checkers
        # print(self.__checkers)
        self.__checkers = checkers

    def mouseMoveEvent(self, event):
        if not self.__checkers:
            return
        line = self._editor.line_from_position(event.pos().y())
        for checker in self.__checkers:
            obj, _, _ = checker
            message = obj.message(line)
            if message is not None:
                # Formatting text
                text = "<div style='color: green'>Lint</div><hr>%s" % message
                QToolTip.showText(self.mapToGlobal(event.pos()), text, self)

    def width(self):
        return 15

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.__checkers is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        for checker in self.__checkers:
            checker_obj, color, _ = checker
            lines = checker_obj.checks.keys()
            painter.setPen(QColor(color))
            painter.setBrush(QColor(color))
            for top, block_number, _ in self._editor.visible_blocks:
                for marker in lines:
                    if marker == block_number:
                        r = self.width() - 9
                        painter.drawEllipse(5, top + 10, r, r)
    """

    """
    """

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.__checks:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QColor("#ffd66c"))
        painter.setBrush(QColor("#ffd66c"))
        if self.__checks is not None:
            lines = self.__checks.keys()
            for top, block_number, _ in self._editor.visible_blocks:
                for marker in lines:
                    if marker == block_number:
                        r = self.width() - 9
                        painter.drawEllipse(5, top + 10, r, r)
    """
