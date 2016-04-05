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

from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QEvent

from PyQt5.Qsci import QsciScintilla

from ninja_ide import resources
from ninja_ide.core import settings


#QGraphicsOpacityEffect doesn't work in mac cause a Qt Issue: QTBUG-15367
ACTIVATE_OPACITY = True if sys.platform != 'darwin' else False


class MiniMap(QsciScintilla):

    def __init__(self, parent):
        super(MiniMap, self).__init__(parent)
        #self.setWordWrapMode(QTextOption.NoWrap)
        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.SendScintilla(QsciScintilla.SCI_SETBUFFEREDDRAW, 0)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, 0)
        self.setMarginWidth(1, 0)
        self.setFolding(self.NoFoldStyle, 2)
        #self.setCenterOnScroll(True)
        self.setMouseTracking(True)
        #self.viewport().setCursor(Qt.PointingHandCursor)
        #self.setTextInteractionFlags(Qt.NoTextInteraction)

        self.Document = parent
        #self.highlighter = None
        # self.lines_count = 0
        self.Locked = False

        # self.Document.updateRequest['const QRect&', int].connect(self.update_visible_area)
        self.connect_DocumentSignal()

        if ACTIVATE_OPACITY:
            self.goe = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.goe)
            self.goe.setOpacity(settings.MINIMAP_MIN_OPACITY)
            self.animation = QPropertyAnimation(self.goe, b"opacity")

        self.slider = SliderArea(self)
        # self.changeSliderHeight()
        # self.viewport().resizeEvent['QResizeEvent*'].connect(\
        #     lambda e: QTimer.singleShot(200, self.changeSliderHeight))
        # self.slider.show()
        self.setReadOnly(True)


    def changeSliderHeight(self):
        self.slider.setFixedHeight(self.viewport().geometry().height())

    def connect_DocumentSignal(self):
        self.Document.SCN_UPDATEUI[int].connect(self.update_visible_area)

    def disconnect_DocumentSignal(self):
        self.Document.SCN_UPDATEUI[int].disconnect(self.update_visible_area)

    def Lock_DocumentSignal(self):
        self.Locked = True

    def unLock_DocumentSignal(self):
        self.Locked = False

    # def disconnect_MinimapSignal(self):
    #     self.SCN_UPDATEUI[int].disconnect(self.update_visible_area)

    # def connect_MinimapSignal(self):
    #     self.SCN_UPDATEUI[int].connect(self.update_visible_area)

    # def shutdown(self):
    #     self.Document.updateRequest['const QRect&', int].disconnect(self.update_visible_area)

    def __calculate_max(self):
        #line_height = self.Document.cursorRect().height()
        #if line_height > 0:
            #self.lines_count = self.Document.viewport().height() / line_height
        self.slider.update_position()
        self.update_visible_area()

    def set_code(self, source):
        #self.setPlainText(source)
        self.__calculate_max()

    def adjust_to_parent(self):
        self.setFixedHeight(self.Document.height())
        self.setFixedWidth(self.Document.width() * settings.SIZE_PROPORTION)
        x = self.Document.width() - self.width()
        self.move(x, 0)
        #fontsize = int(self.width() / settings.MARGIN_LINE)
        #if fontsize < 1:
            #fontsize = 1
        #font = self.document().defaultFont()
        #font.setPointSize(fontsize)
        #self.setFont(font)
        self.__calculate_max()

    def update_visible_area(self):
        if self.Locked:
            return
        #if not self.slider.pressed:
        # line_number = self.Document.firstVisibleBlock().blockNumber()
        # block = self.document().findBlockByLineNumber(line_number)
        #print("\nself.Document.getCursorPosition():", self.Document.getCursorPosition(), self.Document.firstVisibleLine())
        # cursor = self.textCursor()
        # self.setFirstVisibleLine(self.Document.firstVisibleLine())
        l1 = self.Document.firstVisibleLine()
        # l2 = self.firstVisibleLine()
        # p1 = self.Document.getCursorPosition()
        # p2 = self.getCursorPosition()
        # self.setCursorPosition(*self.Document.getCursorPosition())#block.position())
        # rect = self.cursorRect(cursor)
        # self.setTextCursor(cursor)
        # self.slider.move_slider((l1-l2)*QFontMetrics(self.Document.font()).height()/3.2)# arbitraty value!
        # self.slider.move_slider(l1*QFontMetrics(self.Document.font()).height()/3.2)# arbitraty value!
        self.slider.move_slider(l1*QFontMetrics(self.font()).lineSpacing()/3.2)

    #def enterEvent(self, event):
        #if ACTIVATE_OPACITY:
            #self.animation.setDuration(300)
            #self.animation.setStartValue(settings.MINIMAP_MIN_OPACITY)
            #self.animation.setEndValue(settings.MINIMAP_MAX_OPACITY)
            #self.animation.start()

    #def leaveEvent(self, event):
        #if ACTIVATE_OPACITY:
            #self.animation.setDuration(300)
            #self.animation.setStartValue(settings.MINIMAP_MAX_OPACITY)
            #self.animation.setEndValue(settings.MINIMAP_MIN_OPACITY)
            #self.animation.start()

    #def mousePressEvent(self, event):
        #super(MiniMap, self).mousePressEvent(event)
        #cursor = self.cursorForPosition(event.pos())
        #self.Document.jump_to_line(cursor.blockNumber())

    def move_Document(self, y):
        self.Document.move_Document(y)
        # self.Document.fillIndicatorRange(4,0, 12,0, 1)

    def resizeEvent(self, event):
        super(MiniMap, self).resizeEvent(event)
        self.slider.update_position()

    # def scroll_area(self, posDocument, pos_slider):#ensureLineVisible
    #     # posDocument.setY(posDocument.y() - pos_slider.y())
    #     line = self.lineAt(posDocument)
    #     #self.Document.verticalScrollBar().setValue(line)# * QFontMetrics(self.font()).height())
    #     self.setFirstVisibleLine(line)

    def scroll_area(self, __Y):#ensureLineVisible
        # posDocument.setY(posDocument.y() - pos_slider.y())
        line = self.lineAt(QPoint(1, __Y))
        if line < 0:
            print("\n----LINE", line)
            line = self.lineAt(QPoint(1, __Y+1))
        if line < 0:
            print("\n++++LINE", line)
            line = self.lineAt(QPoint(0, __Y))
        if line < 0:
            print("\n*****LINE", line)
            line = self.lineAt(QPoint(0, __Y+1))
        if line < 0:
            print("\n/////LINE", line)
            line = self.lineAt(QPoint(1, __Y-1))
        #self.Document.verticalScrollBar().setValue(line)# * QFontMetrics(self.font()).height())
        self.Lock_DocumentSignal()
        self.Document.setFirstVisibleLine(line)
        print("\nLINE", line, __Y)
        self.unLock_DocumentSignal()

    def scroll_area2(self, pos):#ensureLineVisible
        # posDocument.setY(posDocument.y() - pos_slider.y())
        line = self.lineAt(pos)
        #self.Document.verticalScrollBar().setValue(line)# * QFontMetrics(self.font()).height())
        self.Lock_DocumentSignal()
        # self.Document.setFirstVisibleLine(pos.y()/QFontMetrics(self.font()).lineSpacing()*3.4)
        bar = self.Document.verticalScrollBar() 
        lenght = bar.maximum() - bar.minimum()
        bar.setSliderPosition(pos.y())
        self.unLock_DocumentSignal()

    def wheelEvent(self, event):
        super(MiniMap, self).wheelEvent(event)
        self.Document.wheelEvent(event)

    def inputMethodEvent(self, event):
        print("inputMethodEvent::", event.attributes())#Selection
        super(MiniMap, self).inputMethodEvent(event)

#QsciScintilla:QsciScintillaBase:QAbstractScrollArea
class SliderArea(QFrame):

    def __init__(self, parent):
        super(SliderArea, self).__init__(parent)
        self.minimap = parent
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)
        color = resources.CUSTOM_SCHEME.get(
            'CurrentLine', resources.COLOR_SCHEME['CurrentLine'])
        if ACTIVATE_OPACITY:
            print("\nACTIVATE_OPACITY")
            # self.setStyleSheet("background: %s;" % color)
            self.setStyleSheet("background-color: rgb(203, 186, 98);")#↔167, 167, 167, 100);")
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
        font_size = QFontMetrics(self.minimap.font()).lineSpacing()
        # height = self.minimap.lines() / 5.1 * font_size
        _view = self.minimap.Document.viewport()
        # height = _view.height() / self.minimap.Document.height() * self.minimap.height()# font_size /
        height = _view.height() * settings.SIZE_PROPORTION * 1.22#1.2# font_size /
        print("\nHeight:", height)
        self.setFixedHeight(height)
        self.setFixedWidth(self.minimap.width())
        self.__scroll_margins = (height, self.minimap.height() - height)

    def move_slider(self, y):
        self.move(0, y)

    def move__slider(self, y):
        geo = self.geometry()
        geo.setY(y)
        self.setGeometry(geo)

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
            # if y < self.__scroll_margins[0]:
            #     self.minimap.verticalScrollBar().setSliderPosition(
            #         self.minimap.verticalScrollBar().sliderPosition() - 2)
            # elif y > self.__scroll_margins[1]:
            #     self.minimap.verticalScrollBar().setSliderPosition(
            #         self.minimap.verticalScrollBar().sliderPosition() + 2)
            self.move_slider(y)
            # self.minimap.scroll_area(pos, event.pos())
            _pos = pos
            # _pos.setY(y)
            # _pos.setY(-pos.y() + self.mapToParent(self.pos()).y())
            # self.minimap.scroll_area(self.mapToParent(self.pos()).y())
            self.minimap.scroll_area2(self.pos())

            # _event = QMouseEvent(QEvent.MouseMove, pos, event.windowPos(),\
            #     event.screenPos(), event.button(), \
            #     event.buttons(), event.modifiers())
            # self.minimap.mouseMoveEvent(_event)

            # self.minimap.move_Document(y)

    def function(self):
        l1 = self.minimap.firstVisibleLine()
        l2 = self.firstVisibleLine()
        p1 = self.minimap.getCursorPosition()
        p2 = self.getCursorPosition()
        # self.setCursorPosition(*self.minimap.getCursorPosition())#block.position())
        # rect = self.cursorRect(cursor)
        # self.setTextCursor(cursor)
        self.slider.move_slider((l1-l2)*QFontMetrics(self.minimap.font()).height()/4)#(p1[0]-p2[0])

    def wheelEvent(self, event):
        super(SliderArea, self).wheelEvent(event)
        self.minimap.wheelEvent(event)