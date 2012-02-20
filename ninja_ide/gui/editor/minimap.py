# -*- coding: utf-8 *-*

from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QTextFormat
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QTextOption
from PyQt4.QtGui import QGraphicsOpacityEffect
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPropertyAnimation

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.tools import styles


class MiniMap(QPlainTextEdit):

    def __init__(self, parent):
        super(MiniMap, self).__init__(parent)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.setCenterOnScroll(True)
        self.setMouseTracking(True)

        self._parent = parent
        self.highlighter = None
        styles.set_style(self, 'minimap')
        self.max_line = 0

        self.goe = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.goe)
        self.goe.setOpacity(settings.MINIMAP_MIN_OPACITY)
        self.animation = QPropertyAnimation(self.goe, "opacity")

    def __calculate_max(self):
        first_line = self._parent.firstVisibleBlock().blockNumber()
        last_line = self._parent._sidebarWidget.highest_line
        self.max_line = last_line - first_line
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
        block = self._parent.firstVisibleBlock()
        first_line = block.blockNumber()
        max_count = self.blockCount()
        parent_cursor = self._parent.textCursor()
        parent_cursor.setPosition(block.position())
        self.setTextCursor(parent_cursor)
        lines_count = self.max_line
        if (first_line + self.max_line) > max_count:
            lines_count = max_count - first_line
        extraSelections = []
        for i in xrange(lines_count):
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(resources.CUSTOM_SCHEME.get('current-line',
                        resources.COLOR_SCHEME['current-line']))
            lineColor.setAlpha(100)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            selection.cursor = cursor
            selection.cursor.clearSelection()
            extraSelections.append(selection)
            block = block.next()
        self.setExtraSelections(extraSelections)

    def enterEvent(self, event):
        self.animation.setDuration(300)
        self.animation.setStartValue(settings.MINIMAP_MIN_OPACITY)
        self.animation.setEndValue(settings.MINIMAP_MAX_OPACITY)
        self.animation.start()

    def leaveEvent(self, event):
        self.animation.setDuration(300)
        self.animation.setStartValue(settings.MINIMAP_MAX_OPACITY)
        self.animation.setEndValue(settings.MINIMAP_MIN_OPACITY)
        self.animation.start()

    def mousePressEvent(self, event):
        super(MiniMap, self).mousePressEvent(event)
        cursor = self.cursorForPosition(event.pos())
        self._parent.jump_to_line(cursor.blockNumber())
