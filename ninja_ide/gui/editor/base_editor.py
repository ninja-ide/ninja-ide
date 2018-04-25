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

from PyQt5.QtWidgets import QPlainTextEdit
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QAbstractSlider
# from PyQt5.QtWidgets import QListView
# from PyQt5.QtWidgets import QFrame

from PyQt5.QtGui import QTextBlockUserData
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QTextCursor

from PyQt5.QtCore import QPoint
# from PyQt5.QtCore import QModelIndex
# from PyQt5.QtCore import QEvent
# from PyQt5.QtCore import QAbstractListModel
# from PyQt5.QtCore import Qt
# from PyQt5.QtCore import QSize

from ninja_ide import resources
# from ninja_ide.core import settings


# class CompletionListView(QListView):

#     MAX_VISIBLE_ITEMS = 10

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setVerticalScrollMode(self.ScrollPerItem)
#         self.setFont(settings.FONT)

#     def calculate_size(self):
#         """Determine size by calculating the space of the visible items"""

#         visible_items = min(self.model().rowCount(), self.MAX_VISIBLE_ITEMS)
#         first_visible_row = self.verticalScrollBar().value()
#         option = self.viewOptions()
#         size_hint = QSize()
#         for i in range(visible_items):
#             tmp = self.itemDelegate().sizeHint(
#                 option, self.model().index(i + first_visible_row, 0))
#             if size_hint.width() < tmp.width():
#                 size_hint = tmp

#         height = size_hint.height()
#         height *= visible_items
#         size_hint.setHeight(height)
#         return size_hint


# class CompletionModel(QAbstractListModel):

#     def __init__(self, completion_list, parent=None):
#         super().__init__(parent)
#         self.__completion_list = completion_list

#     def rowCount(self, index=QModelIndex()):
#         return len(self.__completion_list)

#     def data(self, index, role):

#         if not index.isValid() or index.row() >= len(self.__completion_list):
#             return None
#         if role == Qt.DisplayRole:
#             return self.__completion_list[index.row()]
#         return None

#     def item(self, row):
#         return self.__completion_list[row]


# class ProposalWidget(QFrame):

#     def __init__(self, editor):
#         super().__init__(editor)
#         self._editor = editor

#         self._completion_view = CompletionListView(self)
#         self._completion_view.setFrameStyle(QFrame.NoFrame)
#         self._completion_view.setUniformItemSizes(True)
#         self._completion_view.installEventFilter(self)
#         self._completion_view.verticalScrollBar().valueChanged.connect(
#             self.update_position_and_size)

#         self._model = None
#         self.hide()

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(self._completion_view)

#     def eventFilter(self, obj, event):
#         if event.type() == QEvent.FocusOut:
#             self.abort()
#             return True
#         elif event.type() == QEvent.KeyPress:
#             key = event.key()
#             if key == Qt.Key_Escape:
#                 self.abort()
#                 event.accept()
#                 return True
#             elif key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
#                 self.abort()
#                 self.select_item()
#                 event.accept()
#                 return True
#             elif key in (Qt.Key_Right, Qt.Key_Left, Qt.Key_Home,
#                          Qt.Key_End, Qt.Key_Backspace):
#                 # We want these navigation keys to work in the editor.
#                 pass
#             else:
#                 # event.ignore()
#                 # if self.isVisible():
#                 #    prefix = self._editor.word_under_cursor().selectedText()
#                 #     print(prefix)
#                 # return True
#                 # if event.text() and not (event == QKeySequence.Paste):
#                 #     print("hola")
#                 #     return True
#                 pass
#         return False

#     def select_item(self):
#         row = self._completion_view.currentIndex().row()
#         item = self._model.item(row)
#         self._editor.textCursor().insertText(item)

#     def abort(self):
#         if self.isVisible():
#             self.close()
#         self._editor.setFocus()

#     def set_model(self, model):
#         if self._model is not None:
#             self._model.deleteLater()
#             self._model = None
#         self._model = model
#         self._completion_view.setModel(self._model)

#     def show_proposal(self, prefix):
#         self.ensurePolished()
#         self._completion_view.setCurrentIndex(self._model.index(0, 0))
#         self.update_position_and_size()
#         self._completion_view.setFocus()
#         self.show()

#     def update_position_and_size(self):
#         s = self._completion_view.calculate_size()
#         fw = self.frameWidth()
#         w = s.width() + fw * 2 + 30
#         h = s.height() + fw * 2

#         desktop = QApplication.instance().desktop()
#         screen = desktop.availableGeometry(self._editor)
#         cr = self._editor.cursorRect()
#         pos = cr.bottomLeft()
#         rx = pos.x() + 60
#         pos.setX(rx)
#         # pos.rx() -= 16 + fw
#         if pos.y() + h > screen.bottom():
#             print("SI")
#             pos.setY(max(0, cr.top() - h))
#         if pos.x() + w > screen.right():
#             print("NO")
#             pos.setX(max(0, screen.y() - w))
#         self.setGeometry(pos.x(), pos.y(), min(w, screen.width()),
#                          min(h, screen.height()))


class BaseEditor(QPlainTextEdit):

    def __init__(self):
        QPlainTextEdit.__init__(self)
        # Style
        self.__init_style()
        self.__apply_style()
        self.__visible_blocks = []

    @property
    def visible_blocks(self):
        return self.__visible_blocks

    @property
    def cursor_position(self):
        """Get or set the current cursor position.

        :param position: The position to set.
        :type position: tuple(line, column).
        :return: Current cursor position in document.
        :rtype: tuple(line, colum)."""

        cursor = self.textCursor()
        return (cursor.blockNumber(), cursor.columnNumber())

    @cursor_position.setter
    def cursor_position(self, position):
        line, column = position
        line = min(line, self.line_count() - 1)
        column = min(column, len(self.line_text(line)))
        cursor = QTextCursor(self.document().findBlockByNumber(line))
        cursor.setPosition(cursor.block().position() + column,
                           QTextCursor.MoveAnchor)
        self.setTextCursor(cursor)

    @property
    def background_color(self):
        """Get or set the background color.

        :param color: Color to set (name or hexa).
        :type color: QColor or str.
        :return: Background color.
        :rtype: QColor."""

        return self._background_color

    @background_color.setter
    def background_color(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self._background_color = color
        # Refresh stylesheet
        self.__apply_style()

    @property
    def foreground_color(self):
        """Get or set the foreground color.
        :param color: Color to set (name or hexa).
        :type color: QColor or str.
        :return: Foreground color.
        :rtype: QColor"""

        return self._foreground_color

    @foreground_color.setter
    def foreground_color(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self._foreground_color = color
        self.__apply_style()

    def __init_style(self):
        self._background_color = QColor(
            resources.COLOR_SCHEME.get("editor.background"))
        #     resources.get_color('editor.background'))
        self._foreground_color = QColor(
            resources.COLOR_SCHEME.get("editor.foreground"))
        #     resources.get_color('editor.foreground'))
        self._selection_color = QColor(
            resources.COLOR_SCHEME.get("editor.selection.foreground"))
        #     resources.get_color('EditorSelectionColor'))
        self._selection_background_color = QColor(
            resources.COLOR_SCHEME.get("editor.selection.background"))
        #     resources.get_color('EditorSelectionBackground'))

    def __apply_style(self):
        palette = self.palette()
        palette.setColor(palette.Base, self._background_color)
        palette.setColor(palette.Text, self._foreground_color)
        palette.setColor(palette.HighlightedText, self._selection_color)
        palette.setColor(palette.Highlight,
                         self._selection_background_color)
        self.setPalette(palette)

    def paintEvent(self, event):
        self._update_visible_blocks()
        super().paintEvent(event)

    def _update_visible_blocks(self):
        """Updates the list of visible blocks"""

        self.__visible_blocks.clear()
        append = self.__visible_blocks.append

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        editor_height = self.height()
        while block.isValid():
            visible = bottom <= editor_height
            if not visible:
                break
            if block.isVisible():
                append((top, block_number, block))
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def scroll_step_up(self):
        self.verticalScrollBar().triggerAction(
            QAbstractSlider.SliderSingleStepSub)

    def scroll_step_down(self):
        self.verticalScrollBar().triggerAction(
            QAbstractSlider.SliderSingleStepAdd)

    def first_visible_block(self):
        return self.firstVisibleBlock()

    def last_visible_block(self):
        return self.cursorForPosition(
            QPoint(0, self.viewport().height())).block()

    def __enter__(self):
        self.textCursor().beginEditBlock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.textCursor().endEditBlock()

    def selection_range(self):
        """Returns the start and end number of selected lines"""

        text_cursor = self.textCursor()
        start = self.document().findBlock(
            text_cursor.selectionStart()).blockNumber()
        end = self.document().findBlock(
            text_cursor.selectionEnd()).blockNumber()
        if text_cursor.columnNumber() == 0 and start != end:
            end -= 1
        return start, end

    def selected_text(self):
        """Returns the selected text"""

        return self.textCursor().selectedText()

    def has_selection(self):
        return self.textCursor().hasSelection()

    def get_right_word(self):
        """Gets the word on the right of the text cursor"""

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
        return cursor.selectedText().strip()

    def get_right_character(self):
        """Gets the right character on the right of the text cursor"""

        right_word = self.get_right_word()
        right_char = None
        if right_word:
            right_char = right_word[0]
        return right_char

    def move_up_down(self, up=False):
        cursor = self.textCursor()
        move = cursor
        with self:
            has_selection = cursor.hasSelection()
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            if has_selection:
                move.setPosition(start)
                move.movePosition(QTextCursor.StartOfBlock)
                move.setPosition(end, QTextCursor.KeepAnchor)
                m = QTextCursor.EndOfBlock
                if move.atBlockStart():
                    m = QTextCursor.Left
                move.movePosition(m, QTextCursor.KeepAnchor)
            else:
                move.movePosition(QTextCursor.StartOfBlock)
                move.movePosition(QTextCursor.EndOfBlock,
                                  QTextCursor.KeepAnchor)

            text = cursor.selectedText()
            move.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            move.removeSelectedText()

            if up:
                move.movePosition(QTextCursor.PreviousBlock)
                move.insertBlock()
                move.movePosition(QTextCursor.Left)
            else:
                move.movePosition(QTextCursor.EndOfBlock)
                if move.atBlockStart():
                    move.movePosition(QTextCursor.NextBlock)
                    move.insertBlock()
                    move.movePosition(QTextCursor.Left)
                else:
                    move.insertBlock()

            start = move.position()
            move.clearSelection()
            move.insertText(text)
            end = move.position()
            if has_selection:
                move.setPosition(end)
                move.setPosition(start, QTextCursor.KeepAnchor)
            else:
                move.setPosition(start)
            self.setTextCursor(move)

    def duplicate_line(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor_at_start = cursor.position() == start
            cursor.setPosition(end)
            cursor.insertText("\n" + text)
            cursor.setPosition(end if cursor_at_start else start)
            cursor.setPosition(start if cursor_at_start else end,
                               QTextCursor.KeepAnchor)
        else:
            position = cursor.position()
            block = cursor.block()
            text = block.text() + "\n"
            cursor.setPosition(block.position())
            cursor.insertText(text)
            cursor.setPosition(position)
        self.setTextCursor(cursor)

    def line_text(self, line=-1):
        """Returns the text of the specified line.

        :param line: The line number of the text to return.
        :return: Entire lines text.
        :rtype: str.
        """
        if line == -1:
            line, _ = self.cursor_position
        block = self.document().findBlockByNumber(line)
        return block.text()

    def line_count(self):
        """Returns the number of lines"""

        return self.document().blockCount()

    @property
    def text(self):
        """Get or set the plain text editor's content. The previous contents
        are removed.

        :param text: Text to set in document.
        :type text: string.
        :return: The plain text in document.
        :rtype: string.
        """

        return self.toPlainText()

    @text.setter
    def text(self, text):
        self.setPlainText(text)

    def line_indent(self, line=-1):
        """Returns the indentation level of `line`"""

        if line == -1:
            line, _ = self.cursor_position
        text = self.document().findBlockByNumber(line).text()
        indentation = len(text) - len(text.lstrip())
        return indentation

    def select_lines(self, start=0, end=0):
        """Selects enteri lines between start and end line numbers"""

        if end == -1:
            end = self.line_count() - 1
        if start < 0:
            start = 0
        cursor = self.textCursor()
        block = self.document().findBlockByNumber(start)
        cursor.setPosition(block.position())

        if end > start:
            cursor.movePosition(QTextCursor.Down,
                                QTextCursor.KeepAnchor, end - start)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

        elif end < start:
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.Up,
                                QTextCursor.KeepAnchor, start - end)
            cursor.movePosition(QTextCursor.StartOfLine,
                                QTextCursor.KeepAnchor)
        else:
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

        self.setTextCursor(cursor)

    def line_from_position(self, position):
        height = self.fontMetrics().height()
        for top, line, block in self.__visible_blocks:
            if top <= position <= top + height:
                return line
        return -1

    def word_under_cursor(self, cursor=None):
        """Returns QTextCursor that contains a word under passed cursor
        or actual cursor"""
        if cursor is None:
            cursor = self.textCursor()
        start_pos = end_pos = cursor.position()
        while not cursor.atStart():
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            char = cursor.selectedText()[0]
            selected_text = cursor.selectedText()
            if (selected_text in self.word_separators and (
                    selected_text != "n" and selected_text != "t") or
                    char.isspace()):
                break
            start_pos = cursor.position()
            cursor.setPosition(start_pos)
        cursor.setPosition(end_pos)
        while not cursor.atEnd():
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            char = cursor.selectedText()[0]
            selected_text = cursor.selectedText()
            if (selected_text in self.word_separators and (
                    selected_text != "n" and selected_text != "t") or
                    char.isspace()):
                break
            end_pos = cursor.position()
            cursor.setPosition(end_pos)
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        return cursor

    def user_data(self, block=None):
        if block is None:
            block = self.textCursor().block()
        user_data = block.userData()
        if user_data is None:
            user_data = BlockUserData()
            block.setUserData(user_data)
        return user_data


class BlockUserData(QTextBlockUserData):
    """Representation of the data for a block"""

    def __init__(self):
        QTextBlockUserData.__init__(self)
        self.attrs = {}

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def __getitem__(self, name):
        return self.attrs[name]

    def __setitem__(self, name, value):
        self.attrs[name] = value
