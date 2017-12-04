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

from PyQt5.QtWidgets import (
    QApplication,
    QPlainTextEdit,
    QTextEdit
)
from PyQt5.QtGui import (
    QColor,
    QTextFormat,
    QTextCursor,
    QKeyEvent,
    QFont
)
from PyQt5.QtCore import (
    Qt,
    QEvent,
    QProcess,
    QRegExp
)

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.tools import console
from ninja_ide.gui.ide import IDE
# from ninja_ide.gui.editor import syntax_highlighter
from ninja_ide.gui.editor.syntaxes import python_syntax
# from ninja_ide.tools.completion import completer
# from ninja_ide.tools.completion import completer_widget

from ninja_ide.tools.logger import NinjaLogger


try:
    # For Python2
    str = unicode  # lint:ok
except NameError:
    # We are in Python3
    pass

logger = NinjaLogger('ninja_ide.gui.misc.console_widget')

BRACES = {
    "'": "'",
    '"': '"',
    '{': '}',
    '[': ']',
    '(': ')'
}


class ConsoleWidget(QPlainTextEdit):

    def __init__(self):
        super(ConsoleWidget, self).__init__('>>> ')
        self.setUndoRedoEnabled(False)
        self.setFrameShape(0)
        self.apply_editor_style()
        self.setToolTip(self.tr("Show/Hide (F4)"))
        self.moveCursor(QTextCursor.EndOfLine)

        self._patIsWord = re.compile('\w+')
        self.prompt = '>>> '
        self._console = console.Console()
        self._history = []
        self.history_index = 0
        self._current_command = ''
        self._braces = None
        self.imports = ['import __builtin__']
        self.patFrom = re.compile('^(\\s)*from ((\\w)+(\\.)*(\\w)*)+ import')
        self.patImport = re.compile('^(\\s)*import (\\w)+')
        self.patObject = re.compile('[^a-zA-Z0-9_\\.]')
        # self.completer = completer_widget.CompleterWidget(self)
        self.okPrefix = QRegExp('[.)}:,\]]')

        self._pre_key_press = {
            Qt.Key_Enter: self._enter_pressed,
            Qt.Key_Return: self._enter_pressed,
            Qt.Key_Tab: self._tab_pressed,
            Qt.Key_Home: self._home_pressed,
            Qt.Key_PageUp: lambda x: True,
            Qt.Key_PageDown: lambda x: True,
            Qt.Key_Left: self._left_pressed,
            Qt.Key_Up: self._up_pressed,
            Qt.Key_Down: self._down_pressed,
            Qt.Key_Backspace: self._backspace,
        }

        # Create Context Menu
        self._create_context_menu()

        #Set Font
        self.set_font(settings.FONT)
        #Create Highlighter
        # parts_scanner, code_scanner, formats = \
        #    syntax_highlighter.load_syntax(python_syntax.syntax)
        # self.highlighter = syntax_highlighter.SyntaxHighlighter(
        #    self.document(),
        #    parts_scanner, code_scanner, formats)

        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.highlight_current_line()

        self._proc = QProcess(self)
        self._proc.readyReadStandardOutput.connect(self._python_path_detected)
        self._proc.error[QProcess.ProcessError].connect(self.process_error)
        self._add_system_path_for_frozen()

        # ninjaide = IDE.get_service('ide')
        # self.connect(ninjaide,
        #    SIGNAL("ns_preferences_editor_font(PyQt_PyObject)"),
        #    self.set_font)

    def _add_system_path_for_frozen(self):
        try:
            self._proc.start(settings.PYTHON_EXEC, [resources.GET_SYSTEM_PATH])
        except Exception as reason:
            logger.warning('Could not get system path, error: %r' % reason)

    def _python_path_detected(self):
        paths = self._proc.readAllStandardOutput().data().decode('utf8')
        add_system_path = ('import sys; '
                           'sys.path = list(set(sys.path + %s))' % paths)
        self._write(add_system_path)
        self._proc.deleteLater()

    def process_error(self, error):
        message = ''
        if error == 0:
            message = 'Failed to start'
        else:
            message = 'Error during execution, QProcess error: %d' % error
        logger.warning('Could not get system path, error: %r' % message)

    def set_font(self, font):
        self.document().setDefaultFont(font)
        # Fix for older version of Qt which doens't has ForceIntegerMetrics
        if "ForceIntegerMetrics" in dir(QFont):
            self.document().defaultFont().setStyleStrategy(
                QFont.ForceIntegerMetrics)

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

        # Connections
        actionCut.triggered.connect(self._cut)
        actionCopy.triggered.connect(self.copy)
        actionPaste.triggered.connect(self._paste)
        actionClean.triggered.connect(self._clean_console)
        actionCopyHistory.triggered.connect(self._copy_history)
        actionCopyConsoleContent.triggered.connect(self._copy_console_content)

    def _cut(self):
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_X, Qt.ControlModifier, "x")
        self.keyPressEvent(event)

    def _paste(self):
        if self.textCursor().hasSelection():
            self.moveCursor(QTextCursor.End)
        self.paste()

    def _clean_console(self):
        self.clear()
        self._add_prompt()

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

    def _check_event_on_selection(self, event):
        if event.text():
            cursor = self.textCursor()
            begin_last_block = (self.document().lastBlock().position() +
                len(self.prompt))
            if cursor.hasSelection() and \
               ((cursor.selectionEnd() < begin_last_block) or
               (cursor.selectionStart() < begin_last_block)):
                self.moveCursor(QTextCursor.End)

    def _enter_pressed(self, event):
        self._write_command()
        return True

    def _tab_pressed(self, event):
        self.textCursor().insertText(' ' * settings.INDENT)
        return True

    def _home_pressed(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            self.setCursorPosition(0, QTextCursor.KeepAnchor)
        else:
            self.setCursorPosition(0)
        return True

    def _left_pressed(self, event):
        return self._get_cursor_position() == 0

    def _up_pressed(self, event):
        if self.history_index == len(self._history):
            command = self.document().lastBlock().text()[len(self.prompt):]
            self._current_command = command
        self._set_command(self._get_prev_history_entry())
        return True

    def _down_pressed(self, event):
        if len(self._history) == self.history_index:
            command = self._current_command
        else:
            command = self._get_next_history_entry()
        self._set_command(command)
        return True

    def _backspace(self, event):
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        text = cursor.selectedText()[len(self.prompt):]
        if (len(text) % settings.INDENT == 0) and text.isspace():
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor,
                settings.INDENT)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
                settings.INDENT)
            cursor.removeSelectedText()
            return True
        elif (selected_text ==
             self.document().lastBlock().text()[len(self.prompt):]):
            self.textCursor().removeSelectedText()
            return True

        position = self.textCursor().positionInBlock() - len(self.prompt)
        text = self.document().lastBlock().text()[len(self.prompt):]
        if position < len(text):
            if (text[position - 1] in BRACES and
            text[position] in BRACES.values()):
                self.textCursor().deleteChar()

        return self._get_cursor_position() == 0

    def keyPressEvent(self, event):
        #if self.completer.popup().isVisible():
            #if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
                #event.ignore()
                #self.completer.popup().hide()
                #return
            #elif event.key in (Qt.Key_Space, Qt.Key_Escape, Qt.Key_Backtab):
                #self.completer.popup().hide()

        self._check_event_on_selection(event)
        if self._pre_key_press.get(event.key(), lambda x: False)(event):
            return

        if event.text() in (set(BRACES.values()) - set(["'", '"'])):
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

        QPlainTextEdit.keyPressEvent(self, event)

        if event.text() in BRACES:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine,
                QTextCursor.KeepAnchor)
            self.textCursor().insertText(
                BRACES[event.text()])
            self.moveCursor(QTextCursor.Left)

        #completionPrefix = self._text_under_cursor()
        #if event.key() == Qt.Key_Period or (event.key() == Qt.Key_Space and
           #event.modifiers() == Qt.ControlModifier):
            #self.completer.setCompletionPrefix(completionPrefix)
            #self._resolve_completion_argument()
        #if self.completer.popup().isVisible() and \
           #completionPrefix != self.completer.completionPrefix():
            #self.completer.setCompletionPrefix(completionPrefix)
            #self.completer.popup().setCurrentIndex(
                #self.completer.completionModel().index(0, 0))
            #self.completer.setCurrentRow(0)
            #self._resolve_completion_argument()

    #def _resolve_completion_argument(self):
        #try:
            #cursor = self.textCursor()
            #cursor.movePosition(QTextCursor.StartOfLine,
                #QTextCursor.KeepAnchor)
            #var = cursor.selectedText()
            #chars = self.patObject.findall(var)
            #var = var[var.rfind(chars[-1]) + 1:]
            #cr = self.cursorRect()
            #proposals = completer.get_all_completions(var,
                #imports=self.imports)
            #if not proposals:
                #if self.completer.popup().isVisible():
                    #prefix = var[var.rfind('.') + 1:]
                    #var = var[:var.rfind('.') + 1]
                    #var = self._console.get_type(var)
                    #var += prefix
                #else:
                    #var = self._console.get_type(var)
                #proposals = completer.get_all_completions(var,
                    #imports=self.imports)
            #self.completer.complete(cr, proposals)
        #except:
            #self.completer.popup().hide()

    def highlight_current_line(self):
        self.extraSelections = []
        selection = QTextEdit.ExtraSelection()
        lineColor = QColor(resources.CUSTOM_SCHEME.get('CurrentLine',
                    resources.COLOR_SCHEME['CurrentLine']))
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
        #if pos2 is not None:
            #self._braces = (pos1, pos2)
            #selection = QTextEdit.ExtraSelection()
            #selection.format.setForeground(QColor(
                #resources.CUSTOM_SCHEME.get('brace-foreground',
                #resources.COLOR_SCHEME.get('brace-foreground'))))
            #selection.format.setBackground(QColor(
                #resources.CUSTOM_SCHEME.get('brace-background',
                #resources.COLOR_SCHEME.get('brace-background'))))
            #selection.cursor = cursor
            #self.extraSelections.append(selection)
            #selection = QTextEdit.ExtraSelection()
            #selection.format.setForeground(QColor(
                #resources.CUSTOM_SCHEME.get('brace-foreground',
                #resources.COLOR_SCHEME.get('brace-foreground'))))
            #selection.format.setBackground(QColor(
                #resources.CUSTOM_SCHEME.get('brace-background',
                #resources.COLOR_SCHEME.get('brace-background'))))
            #selection.cursor = self.textCursor()
            #selection.cursor.setPosition(pos2)
            #selection.cursor.movePosition(QTextCursor.NextCharacter,
                             #QTextCursor.KeepAnchor)
            #self.extraSelections.append(selection)
        #else:
            #self._braces = (pos1,)
            #selection = QTextEdit.ExtraSelection()
            #selection.format.setBackground(QColor(
                #resources.CUSTOM_SCHEME.get('brace-background',
                #resources.COLOR_SCHEME.get('brace-background'))))
            #selection.format.setForeground(QColor(
                #resources.CUSTOM_SCHEME.get('brace-foreground',
                #resources.COLOR_SCHEME.get('brace-foreground'))))
            #selection.cursor = cursor
            #self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)

    def _text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def get_selection(self, posStart, posEnd):
        cursor = self.textCursor()
        cursor.setPosition(posStart)
        if posEnd == QTextCursor.End:
            cursor2 = self.textCursor()
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

    def _add_prompt(self, incomplete=False):
        if incomplete:
            prompt = '.' * 3 + ' '
        else:
            prompt = self.prompt
        self.appendPlainText(prompt)
        self.moveCursor(QTextCursor.End)

    def _get_cursor_position(self):
        return self.textCursor().columnNumber() - len(self.prompt)

    def _write_command(self):
        text = self.textCursor().block().text()
        command = text[len(self.prompt):]
        incomplete = False
        print(command)
        if command:
            self._add_history(command)
            incomplete = self._write(command)
            output = self._read()
            if output:
                self.appendPlainText(output)
        self._add_prompt(incomplete)
        """command = self.document().lastBlock().text()
        #remove the prompt from the QString
        command = command[len(self.prompt):]
        self._add_history(command)
        conditional = command.strip() != 'quit()'
        incomplete = self._write(command) if conditional else None
        if self.patFrom.match(command) or self.patImport.match(command):
            self.imports += [command]
        if not incomplete:
            output = self._read()
            if output is not None:
                if isinstance(output, str):
                    output = output.encode('utf8')
                self.appendPlainText(output.decode('utf8'))
        # self._add_prompt(incomplete)"""

    def _set_command(self, command):
        self.moveCursor(QTextCursor.End)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
            len(self.prompt))
        cursor.insertText(command)

    def contextMenuEvent(self, event):
        self.popup_menu.exec_(event.globalPos())

    def _write(self, line):
        return self._console.push(line)

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
            hist_len = len(self._history) - 1
            self.history_index = min(hist_len, self.history_index + 1)
            index = self.history_index
            if self.history_index == hist_len:
                self.history_index += 1
            return self._history[index]
        return ''

    def restyle(self):
        self.apply_editor_style()
        parts_scanner, code_scanner, formats = \
            syntax_highlighter.load_syntax(python_syntax.syntax)
        self.highlighter = syntax_highlighter.SyntaxHighlighter(
            self.document(),
            parts_scanner, code_scanner, formats)

    def apply_editor_style(self):
        css = 'QPlainTextEdit {color: %s; background-color: %s;' \
            'selection-color: %s; selection-background-color: %s;}' \
            % (resources.CUSTOM_SCHEME.get('editor-text',
            resources.COLOR_SCHEME['Default']),
            resources.CUSTOM_SCHEME.get('EditorBackground',
                resources.COLOR_SCHEME['EditorBackground']),
            resources.CUSTOM_SCHEME.get('EditorSelectionColor',
                resources.COLOR_SCHEME['EditorSelectionColor']),
            resources.CUSTOM_SCHEME.get('EditorSelectionBackground',
                resources.COLOR_SCHEME['EditorSelectionBackground']))
        self.setStyleSheet(css)

    def load_project_into_console(self, projectFolder):
        """Load the projectFolder received into the sys.path."""
        self._console.push("import sys; sys.path += ['%s']" % projectFolder)

    def unload_project_from_console(self, projectFolder):
        """Unload the project from the system path."""
        self._console.push("import sys; "
            "sys.path = [path for path in sys.path "
            "if path != '%s']" % projectFolder)

    def zoom_in(self):
        font = self.document().defaultFont()
        size = font.pointSize()
        if size < settings.FONT_MAX_SIZE:
            size += 2
            font.setPointSize(size)
        self.setFont(font)

    def zoom_out(self):
        font = self.document().defaultFont()
        size = font.pointSize()
        if size > settings.FONT_MIN_SIZE:
            size -= 2
            font.setPointSize(size)
        self.setFont(font)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.delta() > 0:
                self.zoom_in()
            elif event.delta() < 0:
                self.zoom_out()
            event.ignore()
        super(ConsoleWidget, self).wheelEvent(event)
