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
import re

from PyQt5.QtWidgets import QStyleOptionViewItem
from PyQt5.QtWidgets import QStyle

from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QTextBlock
from PyQt5.QtGui import QColor

from PyQt5.QtCore import QSize
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer

from ninja_ide import resources
from ninja_ide.gui.editor import side_area
from ninja_ide.tools.utils import get_inverted_color


class BaseCodeFolding(object):

    def foldable_blocks(self):
        """Detects the blocks that are going to be folded"""
        return []

    def is_foldable(self, text_or_block):
        """Returns True if the text if foldable. False otherwise"""
        raise NotImplementedError

    def block_indentation(self, block):
        """Return the indentation level of block"""

        block_text = block.text()
        return len(block_text) - len(block_text.strip())


class IndentationFolding(BaseCodeFolding):
    """Base blass for folding by indentation"""

    def foldable_blocks(self, block):
        block_indentation = self.block_indentation(block)
        block = block.next()
        last_block = None
        sub_blocks = []
        append = sub_blocks.append
        while block and block.isValid():
            text_stripped = block.text().strip()
            text_indent = self.block_indentation(block)
            if text_indent <= block_indentation:
                if text_stripped:
                    break
            if text_stripped:
                last_block = block
            append(block)
            block = block.next()

        for block in sub_blocks:
            yield block
            if block == last_block:
                break


class CharBaseFolding(BaseCodeFolding):

    @property
    def open_char(self):
        raise NotImplementedError

    @property
    def close_char(self):
        raise NotImplementedError

    def foldable_blocks(self, block):
        pass


class PythonCodeFolding(IndentationFolding):
    pattern = re.compile(
        "\s*(def|class|with|if|else|elif|for|while|async).*:")

    def is_foldable(self, text_or_block):
        if isinstance(text_or_block, QTextBlock):
            text_or_block = text_or_block.text()
        return self.pattern.match(text_or_block)


IMPLEMENTATIONS = {
    "python": PythonCodeFolding()
}


class CodeFoldingWidget(side_area.SideWidget):
    """Code folding widget"""

    def __init__(self):
        super().__init__()
        self.code_folding = None
        self.setMouseTracking(True)
        self.__mouse_over = None
        self.__current_line_number = -1
        self.__timer = QTimer(self)
        self.__timer.setSingleShot(True)
        self.__timer.setInterval(100)
        self.__timer.timeout.connect(self.update)
        reverse_color = get_inverted_color(
            resources.COLOR_SCHEME.get("editor.background"))
        self.__line_fold_color = QColor(reverse_color)

    def register(self, neditor):
        self.code_folding = IMPLEMENTATIONS.get(neditor.neditable.language())
        if self.code_folding is None:
            neditor.side_widgets.remove(self.object_name)
            return
        super().register(neditor)
        self.user_data = neditor.user_data
        neditor.painted.connect(self.__draw_collapsed_line)

    def __draw_collapsed_line(self):
        viewport = self._neditor.viewport()
        painter = QPainter(viewport)
        painter.setPen(self.__line_fold_color)
        for top, _, block in self._neditor.visible_blocks:
            if not block.next().isVisible():
                layout = block.layout()
                line = layout.lineAt(layout.lineCount() - 1)
                offset = self._neditor.contentOffset()
                line_rect = line.naturalTextRect().translated(offset.x(), top)
                bottom = line_rect.bottom()
                painter.drawLine(
                    line_rect.x(), bottom, line_rect.width(), bottom)

    def __block_under_mouse(self, event):
        """Returns QTextBlock under mouse"""
        posy = event.pos().y()
        height = self._neditor.fontMetrics().height()
        for top, _, block in self._neditor.visible_blocks:
            if posy >= top and posy <= top + height:
                return block

    def is_foldable_block(self, block):
        return self.code_folding.is_foldable(block) or \
            self.user_data(block).get("folded")

    def sizeHint(self):
        fm = self._neditor.fontMetrics()
        return QSize(fm.height(), fm.height())

    def leaveEvent(self, event):
        self.__mouse_over = None
        self.update()

    def mouseMoveEvent(self, event):
        block = self.__block_under_mouse(event)
        if block is None:
            return
        self.__mouse_over = block
        if self.code_folding.is_foldable(block):
            if self.__current_line_number == block.blockNumber():
                return
            self.setCursor(Qt.PointingHandCursor)
            self.__timer.start()
        else:
            self.setCursor(Qt.ArrowCursor)
            self.__timer.stop()
        self.__current_line_number = block.blockNumber()
        self.update()

    def mousePressEvent(self, event):
        block = self.__block_under_mouse(event)
        if block is not None:
            if self.user_data(block).get("folded", default=False):
                self.unfold(block)
            else:
                self.fold(block)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        for top, _, block in self._neditor.visible_blocks:
            if not self.is_foldable_block(block):
                continue
            branch_rect = QRect(0, top, self.sizeHint().width(),
                                self.sizeHint().height())
            opt = QStyleOptionViewItem()
            opt.rect = branch_rect
            opt.state = (QStyle.State_Active |
                         QStyle.State_Item |
                         QStyle.State_Children)
            folded = self.user_data(block).get("folded", default=False)
            if not folded:
                opt.state |= QStyle.State_Open
            # Draw item
            self.style().drawPrimitive(QStyle.PE_IndicatorBranch, opt,
                                       painter, self)
            # Draw folded region background
            if block == self.__mouse_over and not self.__timer.isActive():
                fm_height = self._neditor.fontMetrics().height()
                rect_height = 0
                color = self.palette().highlight().color()
                color.setAlpha(100)
                if not folded:
                    foldable_blocks = self.code_folding.foldable_blocks(block)
                    rect_height = (len(list(foldable_blocks))) * fm_height
                painter.fillRect(QRect(
                    0, top, self.sizeHint().width(),
                    rect_height + fm_height), color)

    def fold(self, block):
        if not self.code_folding.is_foldable(block):
            return
        line, _ = self._neditor.cursor_position
        contains_cursor = False
        for _block in self.code_folding.foldable_blocks(block):
            if _block.blockNumber() == line:
                contains_cursor = True
            _block.setVisible(False)
        self.user_data(block)["folded"] = True
        self._neditor.document().markContentsDirty(
            block.position(), _block.position())
        # If the cursor is inside a block to be hidden,
        # let's move the cursor to the end of the start block
        if contains_cursor:
            cursor = self._neditor.textCursor()
            cursor.setPosition(block.position())
            cursor.movePosition(cursor.EndOfBlock)
            self._neditor.setTextCursor(cursor)
        self._neditor.repaint()

    def unfold(self, block):
        for _block in self.code_folding.foldable_blocks(block):
            _block.setVisible(True)
        self.user_data(block)["folded"] = False
        self._neditor.document().markContentsDirty(
            block.position(), _block.position())
        self._neditor.repaint()
