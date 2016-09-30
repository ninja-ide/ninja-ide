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

from PyQt4.QtGui import (
    QWidget,
    QPainter,
    QBrush,
    QColor
)
from PyQt4.QtCore import Qt
from ninja_ide import resources
from ninja_ide.core import settings

#FIXME: configurable width, transparency, color
#FIXME: tooltips would be nice
#FIXME: configurable markers


class DocumentMap(QWidget):
    __minimum_width = 5
    __maximum_width = 40

    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self.__editor = editor
        self.__scrollbar = self.__editor.verticalScrollBar()
        # Configuration
        self.__initialize = False
        self.__background_color = QColor(resources.CUSTOM_SCHEME.get(
            'EditorBackground', resources.COLOR_SCHEME['EditorBackground']))
        self.__transparency = 100
        self.__background_color.setAlpha(self.__transparency)

        self.__selword_color = int(resources.get_color_hex("SelectedWord"), 16)

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, w):
        if w < self.__minimum_width:
            w = self.__minimum_width
        elif w > self.__maximum_width:
            w = self.__maximum_width
        self.__width = w

    def initialize(self):
        self.show()
        self.show_editor_scrollbar(settings.EDITOR_SCROLLBAR)
        self.width = settings.DOCMAP_WIDTH
        self.adjust()

    def adjust(self):
        self.setFixedHeight(self.__editor.height())
        self.setFixedWidth(self.__width)
        scroll_bar_width, minimap_width = 0, 0
        if self.__scrollbar.isVisible():
            scroll_bar_width = self.__scrollbar.width()
        if self.__editor._mini is not None:
            minimap_width = self.__editor._mini.width() - scroll_bar_width
        self.move(self.__editor.width() - self.__width -
                  minimap_width - scroll_bar_width, 0)

    def show_editor_scrollbar(self, show):
        style = ""
        if not show:
            style = "width: 0px;"
        self.__scrollbar.setStyleSheet(style)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.__background_color)
        # Draw markers
        self.__draw_markers(painter)
        # Draw slider
        if settings.DOCMAP_SLIDER and self.__scrollbar.isVisible():
            painter.setPen(Qt.NoPen)
            color = QColor(Qt.lightGray)
            color.setAlpha(50)
            painter.setBrush(QBrush(color))
            position1 = self.__get_position(self.__scrollbar.value())
            position2 = self.__get_position(
                self.__scrollbar.value() + self.__scrollbar.pageStep())
            painter.drawRect(0, position1, self.__width, position2 - position1)

    def __draw_markers(self, painter):
        if not self.__initialize:
            self.__checkers = self.__editor.neditable.sorted_checkers
            self.__initialize = True
            self.adjust()
        # Draw pep8, error and migrate markers
        for items in self.__checkers:
            checker, color, _ = items
            color = int(color[::-1][:-1], 16)
            lines = list(checker.checks.keys())
            for lineno in lines:
                self.__draw_marker(lineno, painter, color)
        # Draw search lines
        if settings.DOCMAP_SEARCH_LINES:
            for line in self.__editor.search_lines:
                self.__draw_marker(line, painter, self.__selword_color)
        # Draw current line
        if settings.DOCMAP_CURRENT_LINE:
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            curline, _ = self.__editor.getCursorPosition()
            painter.drawRect(0, self.__get_position(curline),
                             self.__width - 1, 1)
        self.update()

    def __draw_marker(self, line, painter, color):
        color = QColor(color)
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawRect(round(self.__width / 4), self.__get_position(line),
                         self.__width / 2, 2)

    def __get_position(self, lineno):
        """ Convert line number to position """

        factor = self.__get_scale_factor()
        return (lineno - self.__scrollbar.minimum()) * factor

    def __get_scale_factor(self):
        scrollb_height = self.__scrollbar.height()
        val = self.__scrollbar.maximum() + self.__scrollbar.pageStep()
        return scrollb_height / val

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            position = event.pos().y()
            line = round(position / self.__get_scale_factor())
            self.__editor.go_to_line(line)
            self.__scrollbar.setValue(line - self.__scrollbar.pageStep() / 2)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and settings.DOCMAP_SLIDER:
            position = event.pos().y()
            line = position / self.__get_scale_factor()
            self.__scrollbar.setValue(line - (self.__scrollbar.pageStep() / 2))