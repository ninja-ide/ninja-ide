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

from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QPen
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QBrush
from PyQt4.QtCore import QPropertyAnimation
from PyQt4.QtGui import QGraphicsOpacityEffect
from PyQt4.QtCore import Qt
from PyQt4.Qsci import QsciScintilla

from ninja_ide.core import settings
from ninja_ide import resources

ACTIVATE_OPACITY = True if not settings.IS_MAC_OS else False


class MiniMap(QsciScintilla):

    def __init__(self, editor):
        super(MiniMap, self).__init__(editor)
        self._editor = editor
        self.SendScintilla(QsciScintilla.SCI_SETCARETSTYLE, 0)
        self.SendScintilla(QsciScintilla.SCI_SETBUFFEREDDRAW, 0)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, 0)
        self.SendScintilla(QsciScintilla.SCI_SETZOOM, -10)
        self.SendScintilla(QsciScintilla.SCI_SETREADONLY, 1)
        self.SendScintilla(QsciScintilla.SCI_HIDESELECTION, 1)
        self.SendScintilla(QsciScintilla.SCI_SETCURSOR, 8)
        # Hide markers
        for i in range(1, 5):
            self.SendScintilla(
                QsciScintilla.SCI_MARKERDEFINE, i, QsciScintilla.SC_MARK_EMPTY)
        self.SendScintilla(QsciScintilla.SCI_SETMARGINWIDTHN, 1, 0)

        self.setMouseTracking(True)

        if ACTIVATE_OPACITY:
            self.goe = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.goe)
            self.goe.setOpacity(settings.MINIMAP_MIN_OPACITY)
            self.animation = QPropertyAnimation(self.goe, "opacity")
            self.animation.setDuration(300)

        self.slider = SliderArea(self)
        self.slider.show()

    def adjust_to_parent(self):
        self.setFixedHeight(self._editor.height())
        self.setFixedWidth(self._editor.width() * settings.SIZE_PROPORTION)
        x = self._editor.width() - self.width()
        self.move(x, 0)
        self.slider.update_position()

    def shutdown(self):
        self._editor.SCN_UPDATEUI.disconnect()
        self._editor.SCN_ZOOM.disconnect()

    def fold(self, line):
        self.foldLine(line)

    def scroll_map(self):
        first_visible_line = self._editor.SendScintilla(
            QsciScintilla.SCI_GETFIRSTVISIBLELINE)
        num_doc_lines = self._editor.SendScintilla(
            QsciScintilla.SCI_GETLINECOUNT)
        num_visible_lines = self._editor.SendScintilla(
            QsciScintilla.SCI_DOCLINEFROMVISIBLE, num_doc_lines)
        lines_on_screen = self._editor.SendScintilla(
            QsciScintilla.SCI_LINESONSCREEN)

        if num_visible_lines > lines_on_screen:
            last_top_visible_line = num_visible_lines - lines_on_screen
            num_map_visible_lines = self.SendScintilla(
                QsciScintilla.SCI_DOCLINEFROMVISIBLE, num_doc_lines)
            # Lines on screen map
            lines_on_screenm = self.SendScintilla(
                QsciScintilla.SCI_LINESONSCREEN)
            # Last top visible line on map
            last_top_visible_linem = num_map_visible_lines - lines_on_screenm
            # Portion covered
            portion = first_visible_line / last_top_visible_line
            first_visible_linem = round(last_top_visible_linem * portion)
            # Scroll
            self.verticalScrollBar().setValue(first_visible_linem)

            # Move slider
            higher_pos = self._editor.SendScintilla(
                QsciScintilla.SCI_POSITIONFROMPOINT, 0, 0)
            y = self.SendScintilla(
                QsciScintilla.SCI_POINTYFROMPOSITION, 0, higher_pos)

            self.slider.move(0, y)

        self._current_scroll_value = self._editor.verticalScrollBar().value()

    def scroll_area(self, pos_parent, line_area):
        line = self.__line_from_position(pos_parent)
        self._editor.verticalScrollBar().setValue(line - line_area)

    def mousePressEvent(self, event):
        super(MiniMap, self).mousePressEvent(event)
        line = self.__line_from_position(event.pos())
        self._editor.jump_to_line(line)

        # Go to center
        los = self._editor.SendScintilla(QsciScintilla.SCI_LINESONSCREEN) / 2
        scroll_value = self._editor.verticalScrollBar().value()

        if self._current_scroll_value < scroll_value:
            self._editor.verticalScrollBar().setValue(scroll_value + los)
        else:
            self._editor.verticalScrollBar().setValue(scroll_value - los)

    def __line_from_position(self, point):
        position = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT,
                                      point.x(), point.y())
        return self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, position)

    def enterEvent(self, event):
        if ACTIVATE_OPACITY:
            self.animation.setStartValue(settings.MINIMAP_MIN_OPACITY)
            self.animation.setEndValue(settings.MINIMAP_MAX_OPACITY)
            self.animation.start()

    def leaveEvent(self, event):
        if ACTIVATE_OPACITY:
            self.animation.setStartValue(settings.MINIMAP_MAX_OPACITY)
            self.animation.setEndValue(settings.MINIMAP_MIN_OPACITY)
            self.animation.start()

    def wheelEvent(self, event):
        super(MiniMap, self).wheelEvent(event)
        self._editor.wheelEvent(event)

    def resizeEvent(self, event):
        super(MiniMap, self).resizeEvent(event)
        self.slider.update_position()


class SliderArea(QFrame):

    def __init__(self, minimap):
        super(SliderArea, self).__init__(minimap)
        self._minimap = minimap
        self.pressed = False
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)
        color = resources.CUSTOM_SCHEME.get(
            'MinimapVisibleArea', resources.COLOR_SCHEME['MinimapVisibleArea'])
        if ACTIVATE_OPACITY:
            self.setStyleSheet("background: %s;" % color)
            self.goe = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.goe)
            self.goe.setOpacity(settings.MINIMAP_MAX_OPACITY / 2)
        else:
            self.setStyleSheet("background: transparent;")

    def mousePressEvent(self, event):
        super(SliderArea, self).mousePressEvent(event)
        self.pressed = True
        self.setCursor(Qt.ClosedHandCursor)
        # Get line number from lines on screen
        # This is to moving the slider from the point where you clicked
        first_visible_line = self._minimap._editor.SendScintilla(
            QsciScintilla.SCI_GETFIRSTVISIBLELINE)
        pos_parent = self.mapToParent(event.pos())
        position = self._minimap.SendScintilla(
            QsciScintilla.SCI_POSITIONFROMPOINT, pos_parent.x(), pos_parent.y())
        line = self._minimap.SendScintilla(
            QsciScintilla.SCI_LINEFROMPOSITION, position)
        self.line_on_visible_area = (line - first_visible_line) + 1

    def mouseReleaseEvent(self, event):
        super(SliderArea, self).mouseReleaseEvent(event)
        self.pressed = False
        self.setCursor(Qt.OpenHandCursor)

    def update_position(self):
        font_size = round(self._minimap.font().pointSize() / 2.5)
        lines_count = self._minimap._editor.SendScintilla(
            QsciScintilla.SCI_LINESONSCREEN)
        height = lines_count * font_size
        self.setFixedHeight(height)
        self.setFixedWidth(self._minimap.width())

    def paintEvent(self, event):
        """Paint over the widget to overlay its content."""

        if not ACTIVATE_OPACITY:
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.fillRect(event.rect(), QBrush(
                QColor(226, 0, 0, 80)))
            painter.setPen(QPen(Qt.NoPen))
            painter.end()
        super(SliderArea, self).paintEvent(event)

    def mouseMoveEvent(self, event):
        super(SliderArea, self).mouseMoveEvent(event)
        if self.pressed:
            pos = self.mapToParent(event.pos())
            self._minimap.scroll_area(pos, self.line_on_visible_area)
