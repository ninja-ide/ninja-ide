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
import sys

from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QTextOption
from PyQt4.QtGui import QGraphicsOpacityEffect
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QPen
from PyQt4.QtGui import QBrush
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPropertyAnimation

from ninja_ide import resources
from ninja_ide.core import settings


#QGraphicsOpacityEffect doesn't work in mac cause a Qt Issue: QTBUG-15367
ACTIVATE_OPACITY = True if sys.platform != 'darwin' else False


class MiniMap(QPlainTextEdit):

    def __init__(self, parent):
        super(MiniMap, self).__init__(parent)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.setCenterOnScroll(True)
        self.setMouseTracking(True)
        self.viewport().setCursor(Qt.PointingHandCursor)
        self.setTextInteractionFlags(Qt.NoTextInteraction)

        self._parent = parent
        self.highlighter = None
        self.lines_count = 0

        if ACTIVATE_OPACITY:
            self.goe = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.goe)
            self.goe.setOpacity(settings.MINIMAP_MIN_OPACITY)
            self.animation = QPropertyAnimation(self.goe, "opacity")

        self.slider = SliderArea(self)
        self.slider.show()

    def __calculate_max(self):
        line_height = self._parent.cursorRect().height()
        if line_height > 0:
            self.lines_count = self._parent.viewport().height() / line_height
        self.slider.update_position()
        self.update_visible_area()

    def set_code(self, source):
        self.setPlainText(source)
        self.__calculate_max()

    def adjust_to_parent(self):
        self.setFixedHeight(self._parent.height())
        self.setFixedWidth(self._parent.width() * settings.SIZE_PROPORTION)
        x = self._parent.width() - self.width()
        self.move(x, 0)
        fontsize = int(self.width() / settings.MARGIN_LINE)
        if fontsize < 1:
            fontsize = 1
        font = self.document().defaultFont()
        font.setPointSize(fontsize)
        self.setFont(font)
        self.__calculate_max()

    def update_visible_area(self):
        if not self.slider.pressed:
            line_number = self._parent.firstVisibleBlock().blockNumber()
            block = self.document().findBlockByLineNumber(line_number)
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            rect = self.cursorRect(cursor)
            self.setTextCursor(cursor)
            self.slider.move_slider(rect.y())

    def enterEvent(self, event):
        if ACTIVATE_OPACITY:
            self.animation.setDuration(300)
            self.animation.setStartValue(settings.MINIMAP_MIN_OPACITY)
            self.animation.setEndValue(settings.MINIMAP_MAX_OPACITY)
            self.animation.start()

    def leaveEvent(self, event):
        if ACTIVATE_OPACITY:
            self.animation.setDuration(300)
            self.animation.setStartValue(settings.MINIMAP_MAX_OPACITY)
            self.animation.setEndValue(settings.MINIMAP_MIN_OPACITY)
            self.animation.start()

    def mousePressEvent(self, event):
        super(MiniMap, self).mousePressEvent(event)
        cursor = self.cursorForPosition(event.pos())
        self._parent.jump_to_line(cursor.blockNumber())

    def resizeEvent(self, event):
        super(MiniMap, self).resizeEvent(event)
        self.slider.update_position()

    def scroll_area(self, pos_parent, pos_slider):
        pos_parent.setY(pos_parent.y() - pos_slider.y())
        cursor = self.cursorForPosition(pos_parent)
        self._parent.verticalScrollBar().setValue(cursor.blockNumber())

    def wheelEvent(self, event):
        super(MiniMap, self).wheelEvent(event)
        self._parent.wheelEvent(event)


class SliderArea(QFrame):

    def __init__(self, parent):
        super(SliderArea, self).__init__(parent)
        self._parent = parent
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)
        color = resources.CUSTOM_SCHEME.get('current-line',
            resources.COLOR_SCHEME['current-line'])
        if ACTIVATE_OPACITY:
            self.setStyleSheet("background: %s;" % color)
            self.goe = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.goe)
            self.goe.setOpacity(settings.MINIMAP_MAX_OPACITY / 2)
        else:
            self.setStyleSheet("background: transparent;")

        self.pressed = False
        self.__scroll_margins = None

    def paintEvent(self, event):
        """Paint over the widget to overlay its content."""
        if not ACTIVATE_OPACITY:
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.fillRect(event.rect(), QBrush(
                QColor(255, 255, 255, 80)))
            painter.setPen(QPen(Qt.NoPen))
            painter.end()
        super(SliderArea, self).paintEvent(event)

    def update_position(self):
        font_size = QFontMetrics(self._parent.font()).height()
        height = self._parent.lines_count * font_size
        self.setFixedHeight(height)
        self.setFixedWidth(self._parent.width())
        self.__scroll_margins = (height, self._parent.height() - height)

    def move_slider(self, y):
        self.move(0, y)

    def mousePressEvent(self, event):
        super(SliderArea, self).mousePressEvent(event)
        self.pressed = True
        self.setCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        super(SliderArea, self).mouseReleaseEvent(event)
        self.pressed = False
        self.setCursor(Qt.OpenHandCursor)

    def mouseMoveEvent(self, event):
        super(SliderArea, self).mouseMoveEvent(event)
        if self.pressed:
            pos = self.mapToParent(event.pos())
            y = pos.y() - (self.height() / 2)
            if y < 0:
                y = 0
            if y < self.__scroll_margins[0]:
                self._parent.verticalScrollBar().setSliderPosition(
                    self._parent.verticalScrollBar().sliderPosition() - 2)
            elif y > self.__scroll_margins[1]:
                self._parent.verticalScrollBar().setSliderPosition(
                    self._parent.verticalScrollBar().sliderPosition() + 2)
            self.move(0, y)
            self._parent.scroll_area(pos, event.pos())
