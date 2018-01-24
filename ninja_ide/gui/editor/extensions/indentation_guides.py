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

from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from ninja_ide.gui.editor.extensions import base


class IndentationGuide(base.Extension):
    """Indentation guides extension for Ninja-IDE Editor"""

    def __init__(self):
        super().__init__()
        self.color = Qt.darkGray

    def install(self):
        self._indentation_width = self._neditor.indentation_width
        self._neditor.updateRequest.connect(self._neditor.viewport().update)
        self._neditor.painted.connect(self._draw)
        self._neditor.viewport().update()

    def shutdown(self):
        self._neditor.painted.disconnect(self._draw)
        self._neditor.updateRequest.connect(self._neditor.viewport().update)
        self._neditor.viewport().update()

    def _draw(self, event):
        doc = self._neditor.document()
        painter = QPainter(self._neditor.viewport())
        color = QColor(self.color)
        color.setAlphaF(.3)
        painter.setPen(color)
        offset = doc.documentMargin() + self._neditor.contentOffset().x()
        previous = 0
        for top, lineno, block in self._neditor.visible_blocks:
            bottom = top + self._neditor.blockBoundingRect(block).height()
            indentation = len(block.text()) - len(block.text().lstrip())
            if not block.text().strip():
                indentation = max(indentation, previous)
            previous = indentation
            for i in range(self._indentation_width, indentation,
                           self._indentation_width):
                x = self._neditor.fontMetrics().width(i * '9') + offset
                painter.drawLine(x, top, x, bottom)
