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
from PyQt5.QtWidgets import (
    QScrollBar,
    QToolTip,
    QStyleOptionSlider,
    QWidget,
    QStyle
)
from PyQt5.QtGui import (
    QPainter,
    QColor
)

from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt


Marker = namedtuple('Marker', 'position color priority')


class ScrollBarOverlay(QWidget):

    class Position:
        LEFT = 0
        CENTER = 1
        RIGHT = 2

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
        if not self.cache:
            return

        rect = self._nscrollbar.overlay_rect()
        sb_range = self._nscrollbar.get_scrollbar_range()
        sb_range = max(self.visible_range, sb_range)
        # horizontal_margin = 3
        # result_width = rect.width() - 2 * horizontal_margin + 1
        result_width = rect.width() / 3
        result_height = min(rect.height() / sb_range + 1, 4)
        # x = rect.left() + horizontal_margin
        x = rect.center().x() - 1
        offset = rect.height() / sb_range * self.range_offset
        vertical_margin = ((rect.height() / sb_range) - result_height) / 2

        painter = QPainter(self)

        for lineno in self.cache.keys():
            marker = self.cache[lineno]
            top = rect.top() + offset + vertical_margin + \
                marker.position / sb_range * rect.height()
            # bottom = top + result_height
            painter.fillRect(
                x,
                top,
                result_width,
                4,
                QColor(marker.color))

    def update_cache(self):
        if not self.__schedule_updated:
            return
        self.cache.clear()
        categories = self.markers.keys()
        for category in categories:
            markers = self.markers[category]
            for marker in markers:
                old = self.cache.get(marker.position)
                if old is not None and old.position == marker.position:
                    if old.priority > marker.priority:
                        self.cache[old.position] = old
                        continue
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

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._tooltip_pos = event.globalPos() - QPoint(event.pos().x(), 0)
            from_line = self._neditor.first_visible_block().blockNumber() + 1
            to_line = self._neditor.last_visible_block().blockNumber()
            text = "<center>%d<br/>&#x2014;<br/>%d</center>"
            QToolTip.showText(self._tooltip_pos, text % (from_line, to_line))

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # tooltip_position = event.globalPos() - QPoint(event.pos().x(), 0)
        from_line = self._neditor.first_visible_block().blockNumber() + 1
        to_line = self._neditor.last_visible_block().blockNumber()
        text = "<center>%d<br/>&#x2014;<br/>%d</center>"
        QToolTip.showText(self._tooltip_pos, text % (from_line, to_line))

    def remove_marker(self, category):
        if category in self._overlay.markers:
            del self._overlay.markers[category]
            self._overlay.schedule_update()

    def add_marker(self, category, lineno, color, priority=0):
        marker = Marker(lineno, color, priority)
        self._overlay.markers[category].append(marker)
        self._overlay.schedule_update()

    def link(self, scrollbar):
        self._overlay.markers.update(scrollbar.markers().copy())

    def markers(self):
        return self._overlay.markers
