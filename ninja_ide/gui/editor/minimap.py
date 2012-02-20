# -*- coding: utf-8 *-*

from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QTextFormat
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QTextOption
from PyQt4.QtGui import QGraphicsOpacityEffect
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QPropertyAnimation

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.tools import styles


class MiniMap(QFrame):

    def __init__(self, parent):
        super(MiniMap, self).__init__(parent)
        self._parent = parent
        self.setMouseTracking(True)
        styles.set_style(self, 'minimap')
        self.max_line = 0

        vbox = QVBoxLayout(self)
        self.goe = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.goe)
        self.goe.setOpacity(settings.MINIMAP_MIN_OPACITY)
        self.animation = QPropertyAnimation(self.goe, "opacity")

        self.minicode = MiniPlainText()
        self.highlighter = None
        vbox.addWidget(self.minicode)

        self.connect(self.minicode, SIGNAL("blockSelected(int)"),
            self.move_to_line)

    def __calculate_max(self):
        first_line = self._parent.firstVisibleBlock().blockNumber()
        last_line = self._parent._sidebarWidget.highest_line
        self.max_line = last_line - first_line
        self.update_visible_area()

    def set_code(self, source):
        self.minicode.setPlainText(source)
        self.__calculate_max()

    def move_to_line(self, lineno):
        self._parent.jump_to_line(lineno)

    def adjust_to_parent(self):
        self.setFixedHeight(self._parent.height())
        self.setFixedWidth(self._parent.width() * settings.SIZE_PROPORTION)
        x = self._parent.width() - self.width()
        self.move(x, 0)
        fontsize = int(self.width() / settings.MARGIN_LINE)
        if fontsize < 1:
            fontsize = 1
        font = self.minicode.document().defaultFont()
        font.setPointSize(fontsize)
        self.minicode.setFont(font)
        self.__calculate_max()

    def update_visible_area(self):
        block = self._parent.firstVisibleBlock()
        parent_cursor = self._parent.textCursor()
        parent_cursor.setPosition(block.position())
        self.minicode.setTextCursor(parent_cursor)
        extraSelections = []
        for i in xrange(self.max_line):
            if not block.isValid():
                continue
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(resources.CUSTOM_SCHEME.get('current-line',
                        resources.COLOR_SCHEME['current-line']))
            lineColor.setAlpha(100)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            cursor = self.minicode.textCursor()
            cursor.setPosition(block.position())
            selection.cursor = cursor
            selection.cursor.clearSelection()
            extraSelections.append(selection)
            block = block.next()
        self.minicode.setExtraSelections(extraSelections)

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


class MiniPlainText(QPlainTextEdit):

###############################################################################
# SIGNALS
# blockSelected(int)
###############################################################################

    def __init__(self):
        super(MiniPlainText, self).__init__()
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.setCenterOnScroll(True)

    def mousePressEvent(self, event):
        super(MiniPlainText, self).mousePressEvent(event)
        cursor = self.cursorForPosition(event.pos())
        self.emit(SIGNAL("blockSelected(int)"), cursor.blockNumber())
