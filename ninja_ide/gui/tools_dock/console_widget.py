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

from PyQt5.QtWidgets import (
    QPlainTextEdit,
)
from PyQt5.QtGui import (
    QTextCursor,
    QColor,
    QTextCharFormat
)
from PyQt5.QtCore import Qt

from ninja_ide import resources
from ninja_ide.tools import console
from ninja_ide.core import settings
from ninja_ide.gui.editor import syntaxhighlighter


class Highlighter(syntaxhighlighter.SyntaxHighlighter):
    """Extends syntax highlighter to only highlight code after prompt"""

    def highlightBlock(self, text):
        if text.startswith('❭ ') or text.startswith('...'):
            super().highlightBlock(text)


class ConsoleWidget(QPlainTextEdit):
    """Extends QPlainTextEdit to emulate a python interpreter"""

    def __init__(self, parent=None):
        super().__init__("❭ ")
        self.setUndoRedoEnabled(False)
        self.document().setDefaultFont(settings.FONT)
        self.setFrameShape(0)
        self.prompt = "❭ "
        # Hostory
        self._history_index = 0
        self._history = []
        self._current_command = ''

        self.moveCursor(QTextCursor.EndOfLine)
        self._console = console.Console()
        syntax = syntaxhighlighter.build_highlighter_for(language='python')
        self._highlighter = Highlighter(
            self.document(),
            syntax.partition_scanner,
            syntax.scanners,
            syntax.formats
        )

        self.apply_editor_style()
        # Key operations
        self._key_operations = {
            Qt.Key_Enter: self.__manage_enter,
            Qt.Key_Return: self.__manage_enter,
            Qt.Key_Backspace: self.__manage_backspace,
            Qt.Key_Left: self.__manage_left,
            Qt.Key_Home: self.__manage_home,
            Qt.Key_Up: self.__up_pressed,
            Qt.Key_Down: self.__down_pressed
        }

    def apply_editor_style(self):
        palette = self.palette()
        palette.setColor(
            palette.Base, QColor(resources.get_color('EditorBackground')))
        palette.setColor(
            palette.Text, QColor(resources.get_color('Default')))
        self.setPalette(palette)

    def display_name(self):
        return 'Interpreter'

    def __manage_left(self, event):
        return self._cursor_position == 0

    def __up_pressed(self, event):
        if self._history_index == len(self._history):
            command = self.document().lastBlock().text()[len(self.prompt):]
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
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
                            len(self.prompt))
        cursor.insertText(command)

    def __manage_home(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            self.set_cursor_position(0, QTextCursor.KeepAnchor)
        else:
            self.set_cursor_position(0)
        return True

    def set_cursor_position(self, position, mode=QTextCursor.MoveAnchor):
        self.moveCursor(QTextCursor.StartOfLine, mode)
        for i in range(len(self.prompt) + position):
            self.moveCursor(QTextCursor.Right, mode)

    def __manage_backspace(self, event):
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        text = cursor.selectedText()[len(self.prompt):]
        if selected_text == self.document().lastBlock().text()[len(self.prompt):]:
            self.textCursor().removeSelectedText()
            return True
        return self._cursor_position == 0

    def _check_event_on_selection(self, event):
        if event.text():
            cursor = self.textCursor()
            begin_last_block = (self.document().lastBlock().position() + len(self.prompt))
            if cursor.hasSelection() and ((cursor.selectionEnd() < begin_last_block) or (cursor.selectionStart() < begin_last_block)):
                self.moveCursor(QTextCursor.End)

    def __manage_enter(self, event):
        """After enter or return pressed"""

        self._write_command()
        return True

    def _clear(self):
        """Clean console and add prompt"""

        self.clear()
        self.__add_prompt()

    def _write_command(self):
        text = self.textCursor().block().text()
        command = text[len(self.prompt):]
        if command.startswith('.'):
            command = command.split('.')[-1]
        # Add command to history
        self._add_in_history(command)
        conditional = command.strip() != 'quit()'
        clear = command.strip() == 'clear'
        if clear:
            self._clear()
            return
        incomplete = self._console.push(command) if conditional else None
        if not incomplete:
            output = self._console.output
            if output:
                self.appendPlainText(output)
        self.__add_prompt(incomplete)

    def __add_prompt(self, incomplete=False):
        prompt = self.prompt
        if incomplete:
            prompt = '...' + ' '
        self.appendPlainText(prompt)
        self.moveCursor(QTextCursor.End)

    def keyPressEvent(self, event):
        # self._check_event_on_selection(event)
        if self._key_operations.get(event.key(), lambda e: False)(event):
            return
        super().keyPressEvent(event)

    @property
    def _cursor_position(self):
        return self.textCursor().columnNumber() - len(self.prompt)

    def button_widgets(self):
        return []
