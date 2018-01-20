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
    QPainter,
    QColor,
    QTextCursor
)
from PyQt5.QtCore import (
    QPoint,
    QLine
)
from ninja_ide.gui.editor.extensions import base


class IndentationGuide(base.Extension):
    """Indentation guides extension for Ninja-IDE Editor"""

    def install(self):
        self._indentation_width = self._neditor.indentation_width
        self._neditor.painted.connect(self._draw)
        self._neditor.viewport().update()

    def shutdown(self):
        self._neditor.painted.disconnect(self._draw)
        self._neditor.viewport().update()

    def _draw(self):
        doc, viewport = self._neditor.document(), self._neditor.viewport()
        painter = QPainter(viewport)
        painter.setPen(QColor("#444"))
        offset = doc.documentMargin() + self._neditor.contentOffset().x()

        def paint(cursor):
            y3 = self._neditor.cursorRect(cursor).top()
            y4 = self._neditor.cursorRect(cursor).bottom()
            user_data = cursor.block().userData()
            if user_data is not None:
                for x in range(self._indentation_width,
                               user_data.get("indentation"),
                               self._indentation_width):
                    width = self._neditor.fontMetrics().width('i' * x) + offset
                    if width > 0:
                        painter.drawLine(QLine(width, y3, width, y4))
        self.do(paint)

    def do(self, func):
        cursor = self._neditor.cursorForPosition(QPoint(0, 0))
        cursor.movePosition(QTextCursor.StartOfBlock)
        while True:
            func(QTextCursor(cursor))
            y = self._neditor.cursorRect(cursor).bottom()
            if y > self._neditor.height():
                break
            if not cursor.block().next().isValid():
                break
            cursor.movePosition(QTextCursor.NextBlock)
