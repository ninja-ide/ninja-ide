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
from __future__ import unicode_literals

import re

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QTextFormat
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QColor
from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.tools import console
from ninja_ide.gui.editor import highlighter
from ninja_ide.tools.completion import completer
from ninja_ide.tools.completion import completer_widget

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.misc.console_widget')

BRACES = {"'": "'",
    '"': '"',
    '{': '}',
    '[': ']',
    '(': ')'}

locked = False


class WriteThread(QThread):
    outputted = QtCore.pyqtSignal(str, bool)

    def __init__(self, console, line):
        global locked
        locked = True

        self.console = console
        self.line = line

        super(WriteThread, self).__init__()

    def run(self):
        incomplete = self.console.push(self.line)
        self.outputted.emit(self.line, incomplete)

        global locked
        locked = False


class ConsoleWidget(QPlainTextEdit):

    def __init__(self):
        QPlainTextEdit.__init__(self, '>>> ')
        self.setUndoRedoEnabled(False)
        self.apply_editor_style()
        self.setToolTip(self.tr("Show/Hide (F4)"))
        self.moveCursor(QTextCursor.EndOfLine)

        self._patIsWord = re.compile('\w+')
        self.prompt = '>>> '
        self._console = console.Console()
        self._history = []
        self._braces = None
        self.imports = ['import __builtin__']
        self.patFrom = re.compile('^(\\s)*from ((\\w)+(\\.)*(\\w)*)+ import')
        self.patImport = re.compile('^(\\s)*import (\\w)+')
        self.patObject = re.compile('[^a-zA-Z0-9_\\.]')
        self.completer = completer_widget.CompleterWidget(self)
        self.okPrefix = QRegExp('[.)}:,\]]')

        self._create_context_menu()

        self._highlighter = highlighter.Highlighter(self.document(), 'python',
            resources.CUSTOM_SCHEME)

        self.connect(self, SIGNAL("cursorPositionChanged()"),
            self.highlight_current_line)
        self.highlight_current_line()

        self._proc = QProcess(self)
        self.connect(self._proc, SIGNAL("readyReadStandardOutput()"),
            self._python_path_detected)
        self.connect(self._proc, SIGNAL("error(QProcess::ProcessError)"),
            self.process_error)
        self._add_system_path_for_frozen()

    def _add_system_path_for_frozen(self):
        try:
            self._proc.start(settings.PYTHON_PATH, [resources.GET_SYSTEM_PATH])
        except Exception as reason:
            logger.warning('Could not get system path, error: %r' % reason)

    def _python_path_detected(self):
        paths = self._proc.readAllStandardOutput().data().decode('utf8')
        add_system_path = ('import sys; '
                           'sys.path = list(set(sys.path + %s))' % paths)
        self._write(add_system_path)

    def process_error(self, error):
        message = ''
        if error == 0:
            message = 'Failed to start'
        else:
            message = 'Error during execution, QProcess error: %d' % error
        logger.warning('Could not get system path, error: %r' % message)

    def _create_context_menu(self):
        self.popup_menu = self.createStandardContextMenu()

        self.popup_menu.clear()

        actionCut = self.popup_menu.addAction(self.tr("Cut"))
        actionCopy = self.popup_menu.addAction(self.tr("Copy"))
        actionPaste = self.popup_menu.addAction(self.tr("Paste"))
        actionClean = self.popup_menu.addAction(self.tr("Clean Console"))
        actionCopyHistory = self.popup_menu.addAction(self.tr("Copy History"))
        actionCopyConsoleContent = self.popup_menu.addAction(
            self.tr("Copy Console Content"))

        self.popup_menu.addAction(actionCut)
        self.popup_menu.addAction(actionCopy)
        self.popup_menu.addAction(actionPaste)
        self.popup_menu.addSeparator()
        self.popup_menu.addAction(actionClean)
        self.popup_menu.addSeparator()
        self.popup_menu.addAction(actionCopyHistory)
        self.popup_menu.addAction(actionCopyConsoleContent)

        self.connect(actionCut, SIGNAL("triggered()"), self.cut)
        self.connect(actionCopy, SIGNAL("triggered()"), self.copy)
        self.connect(actionPaste, SIGNAL("triggered()"), self.paste)
        self.connect(actionClean, SIGNAL("triggered()"), self._clean_console)
        self.connect(actionCopyHistory, SIGNAL("triggered()"),
            self._copy_history)
        self.connect(actionCopyConsoleContent, SIGNAL("triggered()"),
            self._copy_console_content)

    def _clean_console(self):
        self.setPlainText(self.prompt)

    def _copy_history(self):
        historyContent = '\n'.join(self._history)
        clipboard = QApplication.instance().clipboard()
        clipboard.setText(historyContent)

    def _copy_console_content(self):
        content = self.toPlainText()
        clipboard = QApplication.instance().clipboard()
        clipboard.setText(content)

    def setCursorPosition(self, position, mode=QTextCursor.MoveAnchor):
        self.moveCursor(QTextCursor.StartOfLine, mode)
        for i in range(len(self.prompt) + position):
            self.moveCursor(QTextCursor.Right, mode)

    def keyPressEvent(self, event):
        global locked
        if locked:
            if event.key() == Qt.Key_C \
            and event.modifiers() == Qt.ControlModifier:
                self.write_thread.terminate()
                locked = False
                self._add_prompt(False)
                event.accept()
            else:
                event.ignore()
            return
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
                event.ignore()
                self.completer.popup().hide()
                return
            elif event.key in (Qt.Key_Space, Qt.Key_Escape, Qt.Key_Backtab):
                self.completer.popup().hide()
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self._write_command()
            return
        if self._get_cursor_position() < 0:
            self.setCursorPosition(0)
        if event.key() == Qt.Key_Tab:
            self.textCursor().insertText(' ' * settings.INDENT)
            return
        if event.key() == Qt.Key_Home:
            if event.modifiers() == Qt.ShiftModifier:
                self.setCursorPosition(0, QTextCursor.KeepAnchor)
            else:
                self.setCursorPosition(0)
            return
        if event.key() == Qt.Key_PageUp:
            return
        elif event.key() == Qt.Key_Left and self._get_cursor_position() == 0:
            return
        elif event.key() == Qt.Key_Up:
            self._set_command(self._get_prev_history_entry())
            return
        elif event.key() == Qt.Key_Down:
            self._set_command(self._get_next_history_entry())
            return

        if event.key() == Qt.Key_Tab:
            if self.textCursor().hasSelection():
                self.indent_more()
                return
            else:
                self.textCursor().insertText(' ' * settings.INDENT)
                return
        elif event.key() == Qt.Key_Backspace:
            if self.textCursor().hasSelection():
                QPlainTextEdit.keyPressEvent(self, event)
                return
            elif self._get_cursor_position() == 0:
                return
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor,
                settings.INDENT)
            text = cursor.selection().toPlainText()
            if text == ' ' * settings.INDENT:
                cursor.removeSelectedText()
                return True
        elif event.key() == Qt.Key_Home:
            if event.modifiers() == Qt.ShiftModifier:
                move = QTextCursor.KeepAnchor
            else:
                move = QTextCursor.MoveAnchor
            if self.textCursor().atBlockStart():
                self.moveCursor(QTextCursor.WordRight, move)
                return
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return) and \
          event.modifiers() == Qt.ShiftModifier:
            return
        elif event.text() in \
        (set(BRACES.values()) - set(["'", '"'])):
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            brace = cursor.selection().toPlainText()
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            braceClose = cursor.selection().toPlainText()
            if BRACES.get(brace, False) == event.text() and \
              braceClose == event.text():
                self.moveCursor(QTextCursor.Right)
                return
        selection = self.textCursor().selectedText()

        QPlainTextEdit.keyPressEvent(self, event)

        if event.text() in BRACES:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine,
                QTextCursor.KeepAnchor)
            self.textCursor().insertText(
                BRACES[event.text()])
            self.moveCursor(QTextCursor.Left)
            self.textCursor().insertText(selection)
        completionPrefix = self._text_under_cursor()
        if event.key() == Qt.Key_Period or (event.key() == Qt.Key_Space and
        event.modifiers() == Qt.ControlModifier):
            self.completer.setCompletionPrefix(completionPrefix)
            self._resolve_completion_argument()
        elif event.key() == Qt.Key_Space and \
        self.completer.popup().isVisible():
            self.completer.popup().hide()
        if self.completer.popup().isVisible() and \
        completionPrefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completionPrefix)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0))
            self.completer.setCurrentRow(0)
            self._resolve_completion_argument()

    def _resolve_completion_argument(self):
        try:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine,
                QTextCursor.KeepAnchor)
            var = cursor.selectedText()
            chars = self.patObject.findall(var)
            var = var[var.rfind(chars[-1]) + 1:]
            cr = self.cursorRect()
            proposals = completer.get_all_completions(var,
                imports=self.imports)
            if not proposals:
                if self.completer.popup().isVisible():
                    prefix = var[var.rfind('.') + 1:]
                    var = var[:var.rfind('.') + 1]
                    var = self._console.get_type(var)
                    var += prefix
                else:
                    var = self._console.get_type(var)
                proposals = completer.get_all_completions(var,
                    imports=self.imports)
            self.completer.complete(cr, proposals)
        except:
            self.completer.popup().hide()

    def highlight_current_line(self):
        self.emit(SIGNAL("cursorPositionChange(int, int)"),
            self.textCursor().blockNumber() + 1,
            self.textCursor().columnNumber())
        self.extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(resources.CUSTOM_SCHEME.get('current-line',
                        resources.COLOR_SCHEME['current-line']))
            lineColor.setAlpha(20)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)

        if self._braces is not None:
            self._braces = None
        cursor = self.textCursor()
        if cursor.position() == 0:
            self.setExtraSelections(self.extraSelections)
            return
        cursor.movePosition(QTextCursor.PreviousCharacter,
                             QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        pos1 = cursor.position()
        if text in (')', ']', '}'):
            pos2 = self._match_braces(pos1, text, forward=False)
        elif text in ('(', '[', '{'):
            pos2 = self._match_braces(pos1, text, forward=True)
        else:
            self.setExtraSelections(self.extraSelections)
            return
        if pos2 is not None:
            self._braces = (pos1, pos2)
            selection = QTextEdit.ExtraSelection()
            selection.format.setForeground(QColor(
                resources.CUSTOM_SCHEME.get('brace-foreground',
                resources.COLOR_SCHEME.get('brace-foreground'))))
            selection.format.setBackground(QColor(
                resources.CUSTOM_SCHEME.get('brace-background',
                resources.COLOR_SCHEME.get('brace-background'))))
            selection.cursor = cursor
            self.extraSelections.append(selection)
            selection = QTextEdit.ExtraSelection()
            selection.format.setForeground(QColor(
                resources.CUSTOM_SCHEME.get('brace-foreground',
                resources.COLOR_SCHEME.get('brace-foreground'))))
            selection.format.setBackground(QColor(
                resources.CUSTOM_SCHEME.get('brace-background',
                resources.COLOR_SCHEME.get('brace-background'))))
            selection.cursor = self.textCursor()
            selection.cursor.setPosition(pos2)
            selection.cursor.movePosition(QTextCursor.NextCharacter,
                             QTextCursor.KeepAnchor)
            self.extraSelections.append(selection)
        else:
            self._braces = (pos1,)
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(
                resources.CUSTOM_SCHEME.get('brace-background',
                resources.COLOR_SCHEME.get('brace-background'))))
            selection.format.setForeground(QColor(
                resources.CUSTOM_SCHEME.get('brace-foreground',
                resources.COLOR_SCHEME.get('brace-foreground'))))
            selection.cursor = cursor
            self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)

    def _text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def get_selection(self, posStart, posEnd):
        cursor = self.textCursor()
        cursor.setPosition(posStart)
        cursor2 = self.textCursor()
        if posEnd == QTextCursor.End:
            cursor2.movePosition(posEnd)
            cursor.setPosition(cursor2.position(), QTextCursor.KeepAnchor)
        else:
            cursor.setPosition(posEnd, QTextCursor.KeepAnchor)
        return cursor.selectedText()

    def _match_braces(self, position, brace, forward):
        """based on: http://gitorious.org/khteditor"""
        if forward:
            braceMatch = {'(': ')', '[': ']', '{': '}'}
            text = self.get_selection(position, QTextCursor.End)
            braceOpen, braceClose = 1, 1
        else:
            braceMatch = {')': '(', ']': '[', '}': '{'}
            text = self.get_selection(QTextCursor.Start, position)
            braceOpen, braceClose = len(text) - 1, len(text) - 1
        while True:
            if forward:
                posClose = text.find(braceMatch[brace], braceClose)
            else:
                posClose = text.rfind(braceMatch[brace], 0, braceClose + 1)
            if posClose > -1:
                if forward:
                    braceClose = posClose + 1
                    posOpen = text.find(brace, braceOpen, posClose)
                else:
                    braceClose = posClose - 1
                    posOpen = text.rfind(brace, posClose, braceOpen + 1)
                if posOpen > -1:
                    if forward:
                        braceOpen = posOpen + 1
                    else:
                        braceOpen = posOpen - 1
                else:
                    if forward:
                        return position + posClose
                    else:
                        return position - (len(text) - posClose)
            else:
                return

    def _add_prompt(self, incomplete):
        if incomplete:
            prompt = '.' * 3 + ' '
        else:
            prompt = self.prompt
        self.appendPlainText(prompt)
        self.moveCursor(QTextCursor.End)

    def _get_cursor_position(self):
        return self.textCursor().columnNumber() - len(self.prompt)

    def _write_command(self):
        command = self.document().findBlockByLineNumber(
                    self.document().lineCount() - 1).text()
        #remove the prompt from the QString
        command = command[len(self.prompt):]
        self._add_history(command)
        self._write(command)

    def _write_helper(self, command, incomplete):
        if self.patFrom.match(command) or self.patImport.match(command):
            self.imports += [command]
        if not incomplete:
            output = self._read()
            if output is not None:
                if output.__class__.__name__ == 'unicode':
                    output = output.encode('utf8')
                self.appendPlainText(output.decode('utf8'))
        self._add_prompt(incomplete)

    def _set_command(self, command):
        self.moveCursor(QTextCursor.End)
        self.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        for i in range(len(self.prompt)):
            self.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
        self.textCursor().removeSelectedText()
        self.textCursor().insertText(command)
        self.moveCursor(QTextCursor.End)

    def mousePressEvent(self, event):
        #to avoid selection
        event.ignore()

    def contextMenuEvent(self, event):
        self.popup_menu.exec_(event.globalPos())

    def _write(self, line):
        console = self._console
        self.write_thread = WriteThread(console, line)
        self.write_thread.outputted.connect(self._write_helper)
        self.write_thread.start()

    def _read(self):
        return self._console.output

    def _add_history(self, command):
        if command and (not self._history or self._history[-1] != command):
            self._history.append(command)
        self.history_index = len(self._history)

    def _get_prev_history_entry(self):
        if self._history:
            self.history_index = max(0, self.history_index - 1)
            return self._history[self.history_index]
        return ''

    def _get_next_history_entry(self):
        if self._history:
            hist_len = len(self._history)
            self.history_index = min(hist_len, self.history_index + 1)
            if self.history_index < hist_len:
                return self._history[self.history_index]
        return ''

    def restyle(self):
        self.apply_editor_style()
        self._highlighter.apply_highlight('python', resources.CUSTOM_SCHEME)

    def apply_editor_style(self):
        css = 'QPlainTextEdit {color: %s; background-color: %s;' \
            'selection-color: %s; selection-background-color: %s;}' \
            % (resources.CUSTOM_SCHEME.get('editor-text',
            resources.COLOR_SCHEME['editor-text']),
            resources.CUSTOM_SCHEME.get('editor-background',
                resources.COLOR_SCHEME['editor-background']),
            resources.CUSTOM_SCHEME.get('editor-selection-color',
                resources.COLOR_SCHEME['editor-selection-color']),
            resources.CUSTOM_SCHEME.get('editor-selection-background',
                resources.COLOR_SCHEME['editor-selection-background']))
        self.setStyleSheet(css)

    def load_project_into_console(self, projectFolder):
        """Load the projectFolder received into the sys.path."""
        self._console.push("import sys; sys.path += ['%s']" % projectFolder)

    def unload_project_from_console(self, projectFolder):
        """Unload the project from the system path."""
        self._console.push("import sys; "
            "sys.path = [path for path in sys.path "
            "if path != '/home/gato/Desktop']")
