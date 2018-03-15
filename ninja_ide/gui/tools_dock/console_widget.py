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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMenu

from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QKeyEvent

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QEvent

from ninja_ide import translations
from ninja_ide import resources
from ninja_ide.tools import console
from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.core import settings
from ninja_ide.gui.editor import highlighter
from ninja_ide.gui.editor import indenter
from ninja_ide.gui.editor import base_editor
from ninja_ide.gui.tools_dock.tools_dock import _ToolsDock

logger = NinjaLogger(__name__)

# FIXME: editor background color from theme


class Highlighter(highlighter.SyntaxHighlighter):
    """Extends syntax highlighter to only highlight code after prompt"""

    def highlightBlock(self, text):
        data = self.currentBlock().userData()
        try:
            if data.get("prompt") == "[ out ]:":
                return
        except AttributeError:
            return
        super().highlightBlock(text)


class ConsoleSideBar(QWidget):

    PROMPT_IN = "[ in  ]:"
    PROMPT_OUT = "[ out ]:"
    PROMPT_INCOMPLETE = "... "

    def __init__(self, console_widget):
        super().__init__(console_widget)
        self._console_widget = console_widget
        self.setFixedHeight(self._console_widget.height())
        self.user_data = console_widget.user_data
        self._background_color = QColor(
            resources.COLOR_SCHEME.get("editor.background"))
        console_widget.updateRequest.connect(self.update)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = event.rect()
        rect.setWidth(self.__width())
        painter.fillRect(rect, self._background_color)
        painter.setPen(Qt.white)

        font = self._console_widget.font()
        painter.setFont(font)

        width = self.__width()
        height = self._console_widget.fontMetrics().height()
        for top, line, block in self._console_widget.visible_blocks:
            data = self.user_data(block)
            prompt = data.get("prompt")
            text = self.PROMPT_IN
            color = Qt.white
            if prompt is not None:
                if prompt == self.PROMPT_INCOMPLETE:
                    text = self.PROMPT_INCOMPLETE
                    color = Qt.yellow
                else:
                    text = self.PROMPT_OUT
                    color = Qt.gray

            painter.setPen(color)
            painter.drawText(0, top, width, height,
                             Qt.AlignCenter, text)

    def sizeHint(self):
        return QSize(self.__width(), 0)

    def __width(self):
        fmetrics = QFontMetrics(
            self._console_widget.font()).width(self.PROMPT_IN)
        return fmetrics

    def resize_widget(self):
        cr = self._console_widget.contentsRect()
        x = cr.left()
        top = cr.top()
        height = cr.height()
        hint = self.sizeHint()
        width = hint.width()
        self.setGeometry(x, top, width, height)


class ConsoleWidget(base_editor.BaseEditor):
    """Extends QPlainTextEdit to emulate a python interpreter"""

    def __init__(self, parent=None):
        super().__init__()
        self.setUndoRedoEnabled(False)
        self.setCursorWidth(10)
        self.setFrameShape(0)
        self.moveCursor(QTextCursor.EndOfLine)
        self.__incomplete = False
        # History
        self._history_index = 0
        self._history = []
        self._current_command = ''
        # Console
        self._console = console.Console()
        self.setFont(settings.FONT)
        # Set highlighter and indenter for Python
        syntax = highlighter.build_highlighter(language='python')
        if syntax is not None:
            self._highlighter = Highlighter(
                self.document(),
                syntax.partition_scanner,
                syntax.scanners,
                syntax.context
            )
        #     self._highlighter = Highlighter(self.document(), syntax)
        self._indenter = indenter.load_indenter(self, lang="python")
        # Sidebar
        self.sidebar = ConsoleSideBar(self)
        self.setViewportMargins(self.sidebar.sizeHint().width(), 0, 0, 0)
        # Key operations
        self._key_operations = {
            Qt.Key_Enter: self.__manage_enter,
            Qt.Key_Return: self.__manage_enter,
            Qt.Key_Left: self.__manage_left,
            Qt.Key_Up: self.__up_pressed,
            Qt.Key_Down: self.__down_pressed,
            Qt.Key_Home: self.__manage_home,
            Qt.Key_Backspace: self.__manage_backspace
        }
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

        _ToolsDock.register_widget("Interpreter", self)

    def _context_menu(self, pos):
        menu = QMenu(self)
        cut_action = menu.addAction(translations.TR_CUT)
        copy_action = menu.addAction(translations.TR_COPY)
        paste_action = menu.addAction(translations.TR_PASTE)
        menu.addSeparator()
        clear_action = menu.addAction(translations.TR_CLEAR)

        cut_action.triggered.connect(self._cut)
        copy_action.triggered.connect(self.copy)
        paste_action.triggered.connect(self._paste)
        clear_action.triggered.connect(self.clear)

        menu.exec_(self.mapToGlobal(pos))

    def _cut(self):
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_X, Qt.ControlModifier, "x")
        self.keyPressEvent(event)

    def _paste(self):
        self.moveCursor(QTextCursor.End)
        self.paste()

    def install_widget(self):
        logger.debug("Installing {}".format(self.__class__.__name__))

    def __manage_left(self, event):
        return self._cursor_position == 0

    def __up_pressed(self, event):
        if self._history_index == len(self._history):
            command = self.document().lastBlock().text()
            self._current_command = command
        self._set_command(self._get_previous_history_entry())
        return True

    def __down_pressed(self, event):
        if len(self._history) == self._history_index:
            command = self._current_command
        else:
            command = self._get_next_history_entry()
        self._set_command(command)
        return True

    def _get_previous_history_entry(self):
        if self._history:
            self._history_index = max(0, self._history_index - 1)
            return self._history[self._history_index]
        return ''

    def _get_next_history_entry(self):
        if self._history:
            history_len = len(self._history) - 1
            self._history_index = min(history_len, self._history_index + 1)
            index = self._history_index
            if self._history_index == history_len:
                self._history_index += 1
            return self._history[index]
        return ''

    def _add_in_history(self, command):
        if command and (not self._history or self._history[-1] != command):
            self._history.append(command)
        self._history_index = len(self._history)

    def _set_command(self, command):
        self.moveCursor(QTextCursor.End)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.insertText(command)

    def __manage_home(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            self.set_cursor_position(0, QTextCursor.KeepAnchor)
        else:
            self.set_cursor_position(0)
        return True

    def set_cursor_position(self, position, mode=QTextCursor.MoveAnchor):
        self.moveCursor(QTextCursor.StartOfLine, mode)
        for i in range(position):
            self.moveCursor(QTextCursor.Right, mode)

    def __manage_backspace(self, event):
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        selected_text = cursor.selectedText()
        if selected_text == self.document().lastBlock():
            self.textCursor().removeSelectedText()
            return True
        return self._cursor_position == 0

    def _check_event_on_selection(self, event):
        if event.text():
            cursor = self.textCursor()
            begin_last_block = self.document().lastBlock().position()
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            if cursor.hasSelection() and (end < begin_last_block) or (
                    start < begin_last_block):
                self.moveCursor(QTextCursor.End)

    def __manage_enter(self, event):
        """After enter or return pressed"""

        self._write_command()
        if not self.__incomplete:
            self.textCursor().insertBlock()
        self.moveCursor(QTextCursor.End)
        return True

    def _write_command(self):
        command = self.textCursor().block().text()
        self._add_in_history(command)
        incomplete = self._console.push(command)
        if not incomplete:
            self.__incomplete = False
            output = self._console.output.splitlines()
            cursor = self.textCursor()
            block = cursor.block()
            if output:
                for line in output:
                    cursor.insertText("\n" + line)
                block = block.next()
                while block.isValid():
                    self.user_data(block)["prompt"] = ConsoleSideBar.PROMPT_OUT
                    block = block.next()
        else:
            cursor = self.textCursor()
            if not self.__incomplete:
                self.__incomplete = True
            if not self._indenter.indent_block(self.textCursor()):
                cursor.insertBlock()
            self.user_data(cursor.block())["prompt"] = \
                ConsoleSideBar.PROMPT_INCOMPLETE

    def keyPressEvent(self, event):
        self._check_event_on_selection(event)
        if self._key_operations.get(event.key(), lambda e: False)(event):
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y() / 120.
            if delta != 0:
                self.zoom(delta)
            return
        super().wheelEvent(event)

    def zoom(self, delta):
        font = self.document().defaultFont()
        previous_point_size = font.pointSize()
        new_point_size = int(max(1, previous_point_size + delta))
        if new_point_size != previous_point_size:
            font.setPointSize(new_point_size)
            super().setFont(font)
            self.setViewportMargins(self.sidebar.sizeHint().width(), 0, 0, 0)
            self.sidebar.resize_widget()

    @property
    def _cursor_position(self):
        return self.textCursor().columnNumber()


ConsoleWidget()
