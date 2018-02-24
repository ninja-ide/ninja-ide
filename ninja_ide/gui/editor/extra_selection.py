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

from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import (
    QTextCursor,
    QColor,
    QPen,
    QTextFormat,
    QTextCharFormat
)


class ExtraSelection(QTextEdit.ExtraSelection):

    def __init__(self, cursor, start_pos=None,
                 end_pos=None, start_line=None, offset=0):
        super().__init__()
        self.cursor = QTextCursor(cursor)
        # Highest value will appear on top of the lowest values
        self.order = 0
        if start_pos is not None:
            self.cursor.setPosition(start_pos)
        if end_pos is not None:
            self.cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        if start_line is not None:
            # Selection from offset to end of line
            self.cursor.movePosition(QTextCursor.Start,
                                     QTextCursor.MoveAnchor)
            self.cursor.movePosition(QTextCursor.Down,
                                     QTextCursor.MoveAnchor, start_line)
            self.cursor.movePosition(QTextCursor.Right,
                                     QTextCursor.MoveAnchor, offset)
            self.cursor.movePosition(QTextCursor.EndOfLine,
                                     QTextCursor.KeepAnchor)

    def set_underline(self, color, style=QTextCharFormat.SingleUnderline):
        if isinstance(color, str):
            color = QColor(color)
        self.format.setUnderlineStyle(style)
        self.format.setUnderlineColor(color)

    def set_foreground(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self.format.setForeground(color)

    def set_background(self, color):
        if isinstance(color, str):
            color = QColor(color)
        color.setAlpha(150)
        self.format.setBackground(color)

    def set_outline(self, color):
        self.format.setProperty(QTextFormat.OutlinePen, QPen(QColor(color)))

    def set_full_width(self):
        # self.cursor.clearSelection()
        self.format.setProperty(QTextFormat.FullWidthSelection, True)
