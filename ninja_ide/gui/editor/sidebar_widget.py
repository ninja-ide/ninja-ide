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
from __future__ import absolute_import

import math
import re

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QLinearGradient
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QPainter
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPointF

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.editor import helpers


#based on: http://john.nachtimwald.com/2009/08/15/qtextedit-with-line-numbers/
#(MIT license)


class SidebarWidget(QWidget):

    def __init__(self, editor, neditable):
        QWidget.__init__(self, editor)
        self.edit = editor
        self._neditable = neditable
        self.highest_line = 0
        self.foldArea = 15
        self.rightArrowIcon = QPixmap()
        self.downArrowIcon = QPixmap()
        self.pat = re.compile(
            r"(\s)*\"\"\"|(\s)*def |(\s)*class |(\s)*if |(\s)*while |"
            "(\s)*else:|(\s)*elif |(\s)*for |"
            "(\s)*try:|(\s)*except:|(\s)*except |(\s)*#begin-fold:")
        self.patNotPython = re.compile('(\s)*#begin-fold:|(.)*{')
        self.patComment = re.compile(r"(\s)*\"\"\"")
        self._endDocstringBlocks = []
        self.foldedBlocks = []
        self.breakpoints = []
        self.bookmarks = []

        if self._neditable.file_path in settings.BREAKPOINTS:
            self.breakpoints = settings.BREAKPOINTS[self._neditable.file_path]
        if self._neditable.file_path in settings.BOOKMARKS:
            self.bookmarks = settings.BOOKMARKS[self._neditable.file_path]

    def update_area(self):
        maxLine = math.ceil(math.log10(self.edit.blockCount()))
        width = QFontMetrics(
            self.edit.document().defaultFont()).width(
                '0' * int(maxLine)) + 10 + self.foldArea
        if self.width() != width:
            self.setFixedWidth(width)
            self.edit.setViewportMargins(width, 0, 0, 0)
        self.update()

    def update(self, *args):
        QWidget.update(self, *args)

    def code_folding_event(self, lineNumber):
        if self._is_folded(lineNumber):
            self._fold(lineNumber)
        else:
            self._unfold(lineNumber)

        self.edit.update()
        self.update()

    def _fold(self, lineNumber):
        startBlock = self.edit.document().findBlockByNumber(lineNumber - 1)
        endPos = self._find_fold_closing(startBlock)
        endBlock = self.edit.document().findBlockByNumber(endPos)

        block = startBlock.next()
        while block.isValid() and block != endBlock:
            block.setVisible(False)
            block.setLineCount(0)
            block = block.next()

        self.foldedBlocks.append(startBlock.blockNumber())
        self.edit.document().markContentsDirty(startBlock.position(), endPos)

    def _unfold(self, lineNumber):
        startBlock = self.edit.document().findBlockByNumber(lineNumber - 1)
        endPos = self._find_fold_closing(startBlock)
        endBlock = self.edit.document().findBlockByNumber(endPos)

        block = startBlock.next()
        while block.isValid() and block != endBlock:
            block.setVisible(True)
            block.setLineCount(block.layout().lineCount())
            endPos = block.position() + block.length()
            if block.blockNumber() in self.foldedBlocks:
                close = self._find_fold_closing(block)
                block = self.edit.document().findBlockByNumber(close)
            else:
                block = block.next()

        self.foldedBlocks.remove(startBlock.blockNumber())
        self.edit.document().markContentsDirty(startBlock.position(), endPos)

    def _is_folded(self, line):
        block = self.edit.document().findBlockByNumber(line)
        if not block.isValid():
            return False
        return block.isVisible()

    def _find_fold_closing(self, block):
        text = block.text()
        pat = re.compile('(\s)*#begin-fold:')
        patBrace = re.compile('(.)*{$')
        if pat.match(text):
            return self._find_fold_closing_label(block)
        elif patBrace.match(text):
            return self._find_fold_closing_brace(block)
        elif self.patComment.match(text):
            return self._find_fold_closing_docstring(block)

        spaces = helpers.get_leading_spaces(text)
        pat = re.compile('^\s*$|^\s*#')
        block = block.next()
        while block.isValid():
            text2 = block.text()
            if not pat.match(text2):
                spacesEnd = helpers.get_leading_spaces(text2)
                if len(spacesEnd) <= len(spaces):
                    if pat.match(block.previous().text()):
                        return block.previous().blockNumber()
                    else:
                        return block.blockNumber()
            block = block.next()
        return block.previous().blockNumber()

    def _find_fold_closing_label(self, block):
        text = block.text()
        label = text.split(':')[1]
        block = block.next()
        pat = re.compile('\s*#end-fold:' + label)
        while block.isValid():
            if pat.match(block.text()):
                return block.blockNumber() + 1
            block = block.next()
        return block.blockNumber()

    def _find_fold_closing_docstring(self, block):
        block = block.next()
        while block.isValid():
            if block.text().count('"""') > 0:
                return block.blockNumber() + 1
            block = block.next()
        return block.blockNumber()

    def _find_fold_closing_brace(self, block):
        block = block.next()
        openBrace = 1
        while block.isValid():
            openBrace += block.text().count('{')
            openBrace -= block.text().count('}')
            if openBrace == 0:
                return block.blockNumber() + 1
            elif openBrace < 0:
                return block.blockNumber()
            block = block.next()
        return block.blockNumber()

    def paintEvent(self, event):
        page_bottom = self.edit.viewport().height()
        font_metrics = QFontMetrics(self.edit.document().defaultFont())
        current_block = self.edit.document().findBlock(
            self.edit.textCursor().position())
        pattern = self.pat if self.edit.lang == "python" else self.patNotPython

        painter = QPainter(self)
        background = resources.CUSTOM_SCHEME.get(
            'sidebar-background',
            resources.COLOR_SCHEME['sidebar-background'])
        foreground = resources.CUSTOM_SCHEME.get(
            'sidebar-foreground',
            resources.COLOR_SCHEME['sidebar-foreground'])
        background_selected = resources.CUSTOM_SCHEME.get(
            'sidebar-selected-background',
            resources.COLOR_SCHEME['sidebar-selected-background'])
        foreground_selected = resources.CUSTOM_SCHEME.get(
            'sidebar-selected-foreground',
            resources.COLOR_SCHEME['sidebar-selected-foreground'])
        painter.fillRect(self.rect(), QColor(background))

        block = self.edit.firstVisibleBlock()
        viewport_offset = self.edit.contentOffset()
        line_count = block.blockNumber()
        painter.setFont(self.edit.document().defaultFont())

        xofs = self.width() - self.foldArea
        painter.fillRect(xofs, 0, self.foldArea, self.height(),
                         QColor(resources.CUSTOM_SCHEME.get('fold-area',
                                resources.COLOR_SCHEME['fold-area'])))

        while block.isValid():
            line_count += 1
            # The top left position of the block in the document
            position = self.edit.blockBoundingGeometry(block).topLeft() + \
                viewport_offset
            # Check if the position of the block is outside of the visible area
            if position.y() > page_bottom:
                break

            # Set the Painter Pen depending on special lines
            painter.setPen(QColor(foreground))
            error = False
            checkers = self._neditable.sorted_checkers
            for items in checkers:
                checker, color, _ = items
                if (line_count - 1) in checker.checks:
                    painter.setPen(QColor(color))
                    font = painter.font()
                    font.setItalic(True)
                    font.setUnderline(True)
                    painter.setFont(font)
                    error = True
                    break

            # We want the line number for the selected line to be bold.
            bold = False
            if block == current_block:
                painter.fillRect(
                    0, round(position.y()) + font_metrics.descent(),
                    self.width(),
                    font_metrics.ascent() + font_metrics.descent(),
                    QColor(background_selected))

                bold = True
                font = painter.font()
                font.setBold(True)
                if not error:
                    painter.setPen(QColor(foreground_selected))
                painter.setFont(font)

            # Draw the line number right justified at the y position of the
            # line. 3 is a magic padding number. drawText(x, y, text).
            if block.isVisible():
                painter.drawText(
                    self.width() - self.foldArea -
                    font_metrics.width(str(line_count)) - 3,
                    round(position.y()) + font_metrics.ascent() +
                    font_metrics.descent() - 1,
                    str(line_count))

            # Remove the bold style if it was set previously.
            if bold:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)
            if error:
                font = painter.font()
                font.setItalic(False)
                font.setUnderline(False)
                painter.setFont(font)

            block = block.next()

        self.highest_line = line_count

        #Code Folding
        if self.foldArea != self.rightArrowIcon.width():
            polygon = QPolygonF()

            self.rightArrowIcon = QPixmap(self.foldArea, self.foldArea)
            self.rightArrowIcon.fill(Qt.transparent)
            self.downArrowIcon = QPixmap(self.foldArea, self.foldArea)
            self.downArrowIcon.fill(Qt.transparent)

            polygon.append(QPointF(self.foldArea * 0.4, self.foldArea * 0.25))
            polygon.append(QPointF(self.foldArea * 0.4, self.foldArea * 0.75))
            polygon.append(QPointF(self.foldArea * 0.8, self.foldArea * 0.5))
            iconPainter = QPainter(self.rightArrowIcon)
            iconPainter.setRenderHint(QPainter.Antialiasing)
            iconPainter.setPen(Qt.NoPen)
            iconPainter.setBrush(QColor(
                resources.CUSTOM_SCHEME.get(
                    'fold-arrow',
                    resources.COLOR_SCHEME['fold-arrow'])))
            iconPainter.drawPolygon(polygon)

            polygon.clear()
            polygon.append(QPointF(self.foldArea * 0.25, self.foldArea * 0.4))
            polygon.append(QPointF(self.foldArea * 0.75, self.foldArea * 0.4))
            polygon.append(QPointF(self.foldArea * 0.5, self.foldArea * 0.8))
            iconPainter = QPainter(self.downArrowIcon)
            iconPainter.setRenderHint(QPainter.Antialiasing)
            iconPainter.setPen(Qt.NoPen)
            iconPainter.setBrush(QColor(
                resources.CUSTOM_SCHEME.get(
                    'fold-arrow',
                    resources.COLOR_SCHEME['fold-arrow'])))
            iconPainter.drawPolygon(polygon)

            self.calculate_docstring_block_fold()

        block = self.edit.firstVisibleBlock()
        while block.isValid():
            position = self.edit.blockBoundingGeometry(
                block).topLeft() + viewport_offset
            #Check if the position of the block is outside of the visible area
            if position.y() > page_bottom:
                break

            if pattern.match(block.text()) and block.isVisible():
                can_fold = True
                if self.patComment.match(block.text()) and \
                   (block.blockNumber() in self._endDocstringBlocks):
                    can_fold = False

                if can_fold:
                    if block.blockNumber() in self.foldedBlocks:
                        painter.drawPixmap(xofs, round(position.y()),
                                           self.rightArrowIcon)
                    else:
                        painter.drawPixmap(xofs, round(position.y()),
                                           self.downArrowIcon)
            #Add Bookmarks and Breakpoint
            if block.blockNumber() in self.breakpoints:
                linear_gradient = QLinearGradient(
                    xofs, round(position.y()),
                    xofs + self.foldArea, round(position.y()) + self.foldArea)
                linear_gradient.setColorAt(0, QColor(255, 11, 11))
                linear_gradient.setColorAt(1, QColor(147, 9, 9))
                painter.setRenderHints(QPainter.Antialiasing, True)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(linear_gradient))
                painter.drawEllipse(
                    xofs + 1,
                    round(position.y()) + 6,
                    self.foldArea - 1, self.foldArea - 1)
            elif block.blockNumber() in self.bookmarks:
                linear_gradient = QLinearGradient(
                    xofs, round(position.y()),
                    xofs + self.foldArea, round(position.y()) + self.foldArea)
                linear_gradient.setColorAt(0, QColor(13, 62, 243))
                linear_gradient.setColorAt(1, QColor(5, 27, 106))
                painter.setRenderHints(QPainter.Antialiasing, True)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(linear_gradient))
                painter.drawRoundedRect(
                    xofs + 1,
                    round(position.y()) + 6,
                    self.foldArea - 2, self.foldArea - 1,
                    3, 3)

            block = block.next()

        painter.end()
        super(SidebarWidget, self).paintEvent(event)

    def calculate_docstring_block_fold(self):
        self._endDocstringBlocks = []
        fold_docstring_open = False

        block = self.edit.firstVisibleBlock()
        while block.isValid():
            # check if block is a docstring
            if self.patComment.match(block.text()):
                fold_docstring_open = not fold_docstring_open
                #if we are closing the docstring block we add it's line number,
                #so we can skip it later
                if not fold_docstring_open:
                    self._endDocstringBlocks.append(block.blockNumber())
            block = block.next()

    def mousePressEvent(self, event):
        if self.foldArea > 0:
            xofs = self.width() - self.foldArea
            font_metrics = QFontMetrics(self.edit.document().defaultFont())
            fh = font_metrics.lineSpacing()
            ys = event.posF().y()
            lineNumber = 0

            if event.pos().x() > xofs:
                pattern = self.pat
                if self.edit.lang != "python":
                    pattern = self.patNotPython
                block = self.edit.firstVisibleBlock()
                viewport_offset = self.edit.contentOffset()
                page_bottom = self.edit.viewport().height()
                while block.isValid():
                    position = self.edit.blockBoundingGeometry(
                        block).topLeft() + viewport_offset
                    if position.y() > page_bottom:
                        break
                    if (position.y() < ys and (position.y() + fh) > ys and
                            pattern.match(str(block.text()))):
                        if not block.blockNumber() in self._endDocstringBlocks:
                            lineNumber = block.blockNumber() + 1
                            break
                    if (position.y() < ys and (position.y() + fh) > ys and
                            event.button() == Qt.LeftButton):
                        line = block.blockNumber()
                        self.set_breakpoint(line)
                        break
                    elif (position.y() < ys and (position.y() + fh) > ys and
                          event.button() == Qt.RightButton):
                        line = block.blockNumber()
                        self.set_bookmark(line)
                        break
                    block = block.next()
            if lineNumber > 0:
                self.code_folding_event(lineNumber)

    def _save_breakpoints_bookmarks(self):
        if self.bookmarks and not self._neditable.new_document:
            settings.BOOKMARKS[self._neditable.file_path] = self.bookmarks
        elif self._neditable.file_path in settings.BOOKMARKS:
            settings.BOOKMARKS.pop(self._neditable.file_path)
        if self.breakpoints and not self._neditable.new_document:
            settings.BREAKPOINTS[self._neditable.file_path] = self.breakpoints
        elif self._neditable.file_path in settings.BREAKPOINTS:
            settings.BREAKPOINTS.pop(self._neditable.file_path)

    def set_breakpoint(self, lineno):
        if lineno in self.breakpoints:
            self.breakpoints.remove(lineno)
        else:
            self.breakpoints.append(lineno)
        self.update()
        self._save_breakpoints_bookmarks()

    def set_bookmark(self, lineno):
        if lineno in self.bookmarks:
            self.bookmarks.remove(lineno)
        else:
            self.bookmarks.append(lineno)
        self.update()
        self._save_breakpoints_bookmarks()
