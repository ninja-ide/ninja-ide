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

from collections import namedtuple
from collections import defaultdict
from collections import OrderedDict
from PyQt5.QtWidgets import (
    QScrollBar,
    QStyleOptionSlider,
    QWidget,
    QStyle
)
from PyQt5.QtGui import (
    QPainter,
    QColor
)
from PyQt5.QtCore import Qt, QSize, QRect, QTimer
from ninja_ide import resources

STYLESHEET = """QScrollBar {
      background-color: transparent;
  }

  QScrollBar::handle {
      background-color: rgba(60, 60, 60, 70%);
  }

  QScrollBar::handle:hover {
      background-color: rgba(80, 80, 80, 70%);
  }
  QScrollBar::add-line,
  QScrollBar::sub-line,
  QScrollBar::up-arrow,
  QScrollBar::down-arrow,
  QScrollBar::add-page,
  QScrollBar::sub-page {
      background: none;
      border: none;
  }
"""

marker = namedtuple('Marker', 'position color priority')


class ScrollBarOverlay(QWidget):

    def __init__(self, nscrollbar):
        super().__init__(nscrollbar)
        self._nscrollbar = nscrollbar
        self.__schedule_updated = False
        self.markers = defaultdict(list)  # {'id': list of markers}
        self.cache = {}  # {'position': marker}
        self.range_offset = 0.0
        self.visible_range = 0.0

    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        self.update_cache()
        rect = self._nscrollbar.overlay_rect()
        if not self.cache:
            return

        sb_range = self._nscrollbar.get_scrollbar_range()
        sb_range = max(self.visible_range, sb_range)
        horizontal_margin = 3
        result_width = rect.width() - 2 * horizontal_margin + 1
        result_height = min(rect.height() / sb_range + 1, 4)
        x = rect.left() + horizontal_margin
        offset = rect.height() / sb_range * self.range_offset
        vertical_margin = ((rect.height() / sb_range) - result_height) / 2

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        for lineno in self.cache.keys():
            marker = self.cache[lineno]
            top = rect.top() + offset + vertical_margin + \
                marker.position / sb_range * rect.height()
            bottom = top + result_height
            painter.fillRect(
                x,
                top,
                result_width,
                bottom - top,
                QColor(marker.color))

    def update_cache(self):
        if not self.__schedule_updated:
            return
        self.cache.clear()
        categories = self.markers.keys()
        for category in categories:
            markers = self.markers[category]
            for marker in markers:
                self.cache[marker.position] = marker
        self.__schedule_updated = False

    def schedule_update(self):
        if self.__schedule_updated:
            return
        self.__schedule_updated = True
        QTimer.singleShot(0, self.update)


class NScrollBar(QScrollBar):
    """Custom QScrollBar with markers"""

    def __init__(self, neditor):
        super().__init__(neditor)
        self._neditor = neditor
        self._overlay = ScrollBarOverlay(self)
        # self.valueChanged.emit(0)

    def line_number_to_position(self, lineno):
        """ Converts line number to y position """

        return (lineno - self.minimum()) * self.__scale_factor()

    def __scale_factor(self):
        val = self.maximum() + self.pageStep()
        return self.height() / val

    def get_scrollbar_range(self):
        return self.maximum() + self.pageStep()

    def overlay_rect(self):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        return self.style().subControlRect(QStyle.CC_ScrollBar,
                                           opt,
                                           QStyle.SC_ScrollBarGroove,
                                           self)

    def set_visible_range(self, visible_range):
        self._overlay.visible_range = visible_range

    def set_range_offset(self, offset):
        self._overlay.range_offset = offset

    def resizeEvent(self, event):
        if self._overlay is None:
            return
        QScrollBar.resizeEvent(self, event)
        self._overlay.resize(self.size())

    def remove_marker(self, category):
        if category in self._overlay.markers:
            del self._overlay.markers[category]
            self._overlay.schedule_update()

    def add_marker(self, category, marker):
        self._overlay.markers[category].append(marker)
        self._overlay.schedule_update()


'''class NScrollBar(QScrollBar):
    """ Custom QScrollBar with markers

    The scroll bar is divided into three areas: left, center and right.

    """

    LEFT_AREA = 1
    CENTER_AREA = 6
    RIGHT_AREA = 11

    def __init__(self, neditor):
        QScrollBar.__init__(self)
        self._neditor = neditor
        self._neditor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setStyleSheet(STYLESHEET)
        self.__background = QColor(resources.COLOR_SCHEME['EditorBackground'])
        # Install scrollbar
        self._neditor.setVerticalScrollBar(self)
        # Update scrollbar markers
        self._neditor.cursorPositionChanged.connect(self.update)

    def sizeHint(self):
        return QSize(15, self.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.__background)
        # Draw border
        color = QColor("gray")
        color.setAlpha(70)
        painter.setPen(color)
        painter.drawLine(0, 0, 0, self.height())
        # Occurrences
        lcolor = QColor("lightGray")
        painter.setBrush(lcolor)
        painter.setPen(lcolor)
        if self._neditor.occurrences:
            for pos in self._neditor.occurrences:
                painter.drawRect(
                    self.CENTER_AREA,
                    self.__line_number_to_position(pos) - 2,
                    (self.width() // 3) - 2, 3
                )
        # Draw pep8
        checkers = self._neditor.neditable.sorted_checkers
        for items in checkers:
            checker, color, _ = items
            lines = checker.checks.keys()
            painter.setPen(QColor(color))
            painter.setBrush(QColor(color))
            for line in lines:
                painter.drawRect(
                    self.LEFT_AREA,
                    self.__line_number_to_position(line),
                    (self.width() // 3) - 2, 3
                )
        # Draw current line
        lineno, _ = self._neditor.cursor_position
        line_color = QColor("lightGray")
        painter.setPen(line_color)
        painter.drawRect(2, self.__line_number_to_position(lineno),
                         self.width() - 5, 1)
        # Paint slider after markers
        super().paintEvent(event)

    def __line_number_to_position(self, lineno):
        """ Converts line number to y position """

        return (lineno - self.minimum()) * self.__scale_factor()

    def __scale_factor(self):
        val = self.maximum() + self.pageStep()
        return self.height() / val
'''