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
        self.SendScintilla(QsciScintilla.SCI_SETMARGINWIDTHN, 1, 1)
        self.setMarginsBackgroundColor(QColor(
            resources.CUSTOM_SCHEME.get(
                'EditorBackground',
                resources.COLOR_SCHEME.get('EditorBackground'))))

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
        # Visible document line for the code view
        first_visible_line = self._editor.SendScintilla(
            QsciScintilla.SCI_GETFIRSTVISIBLELINE)
        first_doc_line = self._editor.SendScintilla(
            QsciScintilla.SCI_DOCLINEFROMVISIBLE, first_visible_line)
        lines_on_screen = self._editor.SendScintilla(
            QsciScintilla.SCI_LINESONSCREEN, first_visible_line)
        last_doc_line = self._editor.SendScintilla(
            QsciScintilla.SCI_DOCLINEFROMVISIBLE,
            first_visible_line + lines_on_screen)

        # Visible document line for the map view
        first_visible_line_map = self.SendScintilla(
            QsciScintilla.SCI_GETFIRSTVISIBLELINE)
        lines_on_map = self.SendScintilla(
            QsciScintilla.SCI_LINESONSCREEN, first_visible_line_map)
        last_map_line = self.SendScintilla(
            QsciScintilla.SCI_DOCLINEFROMVISIBLE,
            first_visible_line_map + lines_on_map)

        # If part of editor view is out of map, then scroll map
        if last_map_line < last_doc_line:
            self.SendScintilla(QsciScintilla.SCI_GOTOLINE, last_doc_line)
        else:
            self.SendScintilla(QsciScintilla.SCI_GOTOLINE, first_doc_line)

        higher_pos = self._editor.SendScintilla(
            QsciScintilla.SCI_POSITIONFROMPOINT, 0, 0)
        y = self.SendScintilla(
            QsciScintilla.SCI_POINTYFROMPOSITION, 0, higher_pos)
        self.slider.move(0, y)
        self._current_scroll_value = self._editor.verticalScrollBar().value()

    def scroll_area(self, pos_parent, pos_slider):
        pos_parent.setY(pos_parent.y() - pos_slider.y())
        line = self.__line_from_position(pos_parent)
        self._editor.verticalScrollBar().setValue(line)

    def mousePressEvent(self, event):
        super(MiniMap, self).mousePressEvent(event)
        line = self.__line_from_position(event.pos())
        self._editor.jump_to_line(line)

        # Go to center
        los = self._editor.SendScintilla(
            QsciScintilla.SCI_LINESONSCREEN) / 2
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
        self.__scroll_margins = (height, self._minimap.height() - height)

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

    def mouseMoveEvent(self, event):
        super(SliderArea, self).mouseMoveEvent(event)
        if self.pressed:
            pos = self.mapToParent(event.pos())
            y = pos.y() - (self.height() / 2)
            if y < 0:
                y = 0
            if y == 0 and y < self.__scroll_margins[0]:
                self._minimap.verticalScrollBar().setSliderPosition(
                    self._minimap.verticalScrollBar().sliderPosition() - 2)
            elif y > self.__scroll_margins[1]:
                self._minimap.verticalScrollBar().setSliderPosition(
                    self._minimap.verticalScrollBar().sliderPosition() + 2)
            self.move(0, y)
            self._minimap.scroll_area(pos, event.pos())