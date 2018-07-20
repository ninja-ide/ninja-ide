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
from collections import defaultdict

from PyQt5.QtWidgets import QToolTip

from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QPainter

from PyQt5.QtCore import QSize
from PyQt5.QtCore import QRect

from ninja_ide.gui.ide import IDE
from ninja_ide.gui.editor import side_area
from ninja_ide.gui.main_panel.marks import Bookmark


class MarkerWidget(side_area.SideWidget):

    def __init__(self):
        side_area.SideWidget.__init__(self)
        self.setMouseTracking(True)
        self.__bookmarks = defaultdict(list)
        self.__line_hovered = -1

        self._bookmark_manager = IDE.get_service("bookmarks")
        self._bookmark_manager.dataChanged.connect(
            self._highlight_in_scrollbar)
        self.sidebarContextMenuRequested.connect(self._show_menu)

    def _highlight_in_scrollbar(self):
        self._neditor.scrollbar().remove_marker("bookmarks")
        for book in self._bookmark_manager.bookmarks(self._neditor.file_path):
            self._neditor.scrollbar().add_marker(
                "bookmarks", book.lineno, "#8080ff")

    def on_register(self):
        """Highlight markers on scrollbar"""
        bookmarks = self._bookmark_manager.bookmarks(self._neditor.file_path)
        for b in bookmarks:
            self._neditor.scrollbar().add_marker(
                "bookmarks", b.lineno, "#8080ff")

    def _show_menu(self, line, menu):
        set_breakpoint_action = menu.addAction(
            "Set Breakpoint at: {}".format(line + 1))
        toggle_bookmark_action = menu.addAction("Toggle Bookmark")
        toggle_bookmark_action.triggered.connect(
            lambda: self._toggle_bookmark(line))

    def _toggle_bookmark(self, line):
        filename = self._neditor.file_path
        if line <= 0 or filename is None:
            return

        bookmark = self._bookmark_manager.find_bookmark(filename, line)
        if bookmark is not None:
            self._bookmark_manager.remove_bookmark(bookmark)
            return
        bookmark = Bookmark(filename, line)
        self._bookmark_manager.add_bookmark(bookmark)

    def width(self):
        return self.sizeHint().width()

    def next_bookmark(self):
        bookmarks = self._bookmark_manager.bookmarks(self._neditor.file_path)
        if bookmarks:
            bookmarks = [bookmark.lineno for bookmark in bookmarks]
            current_line, col = self._neditor.cursor_position
            index = bisect.bisect(bookmarks, current_line)
            try:
                line = bookmarks[index]
            except IndexError:
                line = bookmarks[0]
            self._neditor.go_to_line(line, col, center=False)
            self._neditor.setFocus()

    def previous_bookmark(self):
        bookmarks = self._bookmark_manager.bookmarks(self._neditor.file_path)
        if bookmarks:
            bookmarks = [bookmark.lineno for bookmark in bookmarks]
            current_line, col = self._neditor.cursor_position
            index = bisect.bisect(bookmarks, current_line)
            line = bookmarks[index - 1]
            if line == current_line:
                line = bookmarks[index - 2]
            self._neditor.go_to_line(line, col, center=False)
            self._neditor.setFocus()

    def sizeHint(self):
        font_metrics = QFontMetrics(self._neditor.font())
        size = QSize(font_metrics.height(), font_metrics.height())
        return size

    # def enterEvent(self, event):
    #     self.setCursor(Qt.PointingHandCursor)

    def mouseMoveEvent(self, event):
        cursor = self._neditor.cursorForPosition(event.pos())
        line = cursor.blockNumber()
        bookmarks = self._bookmark_manager.bookmarks(self._neditor.file_path)
        for book in bookmarks:
            if book.lineno == line and book.note:
                QToolTip.showText(self.mapToGlobal(event.pos()), book.note)
    #     if event.button() == Qt.LeftButton:
    #         # Get line number from position
    #         y_pos = event.pos().y()
    #         line = self._neditor.line_from_position(y_pos)
    #         if line not in self.__bookmarks:
    #             # Add marker
    #             self.__bookmarks.append(line)
    #         else:
    #             # Remove marker
    #             self.__bookmarks.remove(line)
    #         self.repaint()

    def leaveEvent(self, event):
        self.__line_hovered = -1
        self.repaint()

    # def mouseMoveEvent(self, event):
    #     line = self._neditor.line_from_position(event.pos().y())
    #     self.__line_hovered = line
    #     self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        r = self.width() - 10
        marks = IDE.get_service("bookmarks").bookmarks(self._neditor.file_path)
        for top, block_number, block in self._neditor.visible_blocks:
            for mark in marks:
                if mark.lineno == block_number:
                    r = QRect(0, top + 3, 16, 16)
                    mark.linetext = block.text()
                    mark.paint_icon(painter, r)
