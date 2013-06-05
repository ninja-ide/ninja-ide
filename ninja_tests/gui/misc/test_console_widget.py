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

# Import this before Qt to set the correct API
import ninja_ide  # lint:ok

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QKeyEvent
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEvent

from ninja_ide.gui.misc import console_widget
from ninja_tests import BaseTest


class FakeCompleterWidget(object):

    def __init__(self, *arg):
        pass

    def popup(self):
        return self

    def isVisible(self):
        return False


class ConsoleWidgetTestCase(BaseTest):

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        del cls._app

    def setUp(self):
        super(ConsoleWidgetTestCase, self).setUp()
        self.patch(console_widget.completer_widget, "CompleterWidget",
            FakeCompleterWidget)
        self.patch(console_widget.ConsoleWidget, "_create_context_menu",
            lambda *arg: None)
        self.console_widget = console_widget.ConsoleWidget()

    def test_menu_cut(self):
        data = []

        def called(event):
            data.append(event)

        self.patch(self.console_widget, 'keyPressEvent', called)
        self.console_widget._cut()
        self.assertEqual(data[0].type(), QEvent.KeyPress)
        self.assertEqual(data[0].key(), Qt.Key_X)
        self.assertEqual(data[0].modifiers(), Qt.ControlModifier)
        self.assertEqual(data[0].text(), "x")

    def test_menu_cut_with_multiline_selection(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText("asdqwe")
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()
        self.console_widget._cut()
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)

    def test_menu_cut_with_line_selection(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.selectAll()
        # The >>> content
        text = self.console_widget.textCursor().selectedText()
        self.console_widget.moveCursor(QTextCursor.End)
        self.console_widget.textCursor().insertText("asdqwe")
        cursor = self.console_widget.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
            len(self.console_widget.prompt))
        # "asdqwe"
        text_word = cursor.selectedText()
        self.console_widget.setTextCursor(cursor)
        self.console_widget._cut()
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)
        self.assertEqual(text_word, "asdqwe")

    def test_menu_paste_selection(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText("asdqwe")
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText() + "ninja"

        self._app.clipboard().setText("ninja")
        self.console_widget._paste()
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)

    def test_menu_paste(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText("asdqwe")
        self.console_widget.moveCursor(QTextCursor.Left)
        text = self.console_widget.toPlainText()[:-1] + "ninjae"

        self._app.clipboard().setText("ninja")
        self.console_widget._paste()
        text_after = self.console_widget.toPlainText()
        self.assertEqual(text, text_after)

    def test_clean_console(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget._clean_console()
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, self.console_widget.prompt)

    def test_copy_history(self):
        lines = ("asd", "qwe", "rty")
        for line in lines:
            self.console_widget.textCursor().insertText(line)
            self.console_widget._write_command()
        self.console_widget._copy_history()
        paste = self._app.clipboard().text()
        self.assertEqual(paste, '\n'.join(lines))

    def test_copy_console_content(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        lines = ("print 'ninja'", "q = 3")
        for line in lines:
            self.console_widget.textCursor().insertText(line)
            self.console_widget._write_command()
        self.console_widget._copy_console_content()
        paste = self._app.clipboard().text()
        content = [">>> ", ">>> "] + [">>> " + line for line in lines]
        content.insert(-1, 'ninja')
        self.assertEqual(paste, '\n'.join(content + ['>>> ']))

    def test_check_event_on_selection_all_selected(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText('a = 5')
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText() + 'a'
        self.assertTrue(self.console_widget.textCursor().hasSelection())
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier, "a")
        self.console_widget.keyPressEvent(event)
        self.assertFalse(self.console_widget.textCursor().hasSelection())
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)

    def test_check_event_on_selection_all_selected_no_text(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText('a = 5')
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()
        self.assertTrue(self.console_widget.textCursor().hasSelection())
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier, "")
        self.console_widget.keyPressEvent(event)
        self.assertTrue(self.console_widget.textCursor().hasSelection())
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)

    def test_check_event_on_selection_last_block_selected(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText('a = 5')
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()[:-2] + '2'
        self.console_widget.moveCursor(QTextCursor.End)
        self.console_widget.setCursorPosition(3, QTextCursor.KeepAnchor)
        self.assertTrue(self.console_widget.textCursor().hasSelection())
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_2, Qt.NoModifier, "2")
        self.console_widget.keyPressEvent(event)
        self.assertFalse(self.console_widget.textCursor().hasSelection())
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)

    def test_tab_pressed(self):
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()
        self.console_widget.moveCursor(QTextCursor.End)
        self.assertEqual(text, self.console_widget.prompt)
        self.console_widget._tab_pressed(None)
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()
        self.assertEqual(text,
            self.console_widget.prompt + ' ' * console_widget.settings.INDENT)

    def test_home_pressed(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText('a = 5')
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Home, Qt.NoModifier, "")
        self.console_widget._home_pressed(event)
        self.assertEqual(self.console_widget.textCursor().position(),
            self.console_widget.document().lastBlock().position() +
            len(self.console_widget.prompt))

    def test_home_pressed_with_shift(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText('a = 5')
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Home, Qt.ShiftModifier, "")
        self.console_widget._home_pressed(event)
        text = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, "a = 5")

    def test_enter_pressed(self):
        data = []

        self.patch(self.console_widget, "_write_command",
            lambda: data.append(True))
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier, "")
        self.console_widget.keyPressEvent(event)
        self.assertEqual(data, [True])
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier, "")
        self.console_widget.keyPressEvent(event)
        self.assertEqual(data, [True, True])

    def test_left_pressed(self):
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText('a = 5')
        val = self.console_widget._left_pressed(None)
        self.assertFalse(val)
        self.console_widget.setCursorPosition(0)
        val = self.console_widget._left_pressed(None)
        self.assertTrue(val)

    def test_backspace(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText('a = 5')
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()[:-1]
        self.console_widget.moveCursor(QTextCursor.End)
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier, "")
        self.console_widget.keyPressEvent(event)
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)

    def test_backspace_indent(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText(
            ' ' * console_widget.settings.INDENT * 2)
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()[:
            -console_widget.settings.INDENT]
        self.console_widget.moveCursor(QTextCursor.End)
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier, "")
        self.console_widget.keyPressEvent(event)
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)

    def test_backspace_remove_selection(self):
        self.console_widget._write_command()
        self.console_widget._write_command()
        self.console_widget.textCursor().insertText("a = 5")
        self.console_widget.selectAll()
        text = self.console_widget.textCursor().selectedText()[:-2]
        self.console_widget.moveCursor(QTextCursor.End)
        self.console_widget.setCursorPosition(3, QTextCursor.KeepAnchor)
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier, "")
        self.console_widget.keyPressEvent(event)
        self.console_widget.selectAll()
        text_after = self.console_widget.textCursor().selectedText()
        self.assertEqual(text, text_after)

    def test_navigate_history(self):
        lines = ("print 'ninja'", "print 'ide'")
        for line in lines:
            self.console_widget.textCursor().insertText(line)
            self.console_widget._write_command()
        current = 'current_command'
        self.console_widget.textCursor().insertText(current)
        self.console_widget._up_pressed(None)
        line = self.console_widget.document().lastBlock().text()
        self.assertEqual(line, self.console_widget.prompt + lines[1])
        self.assertEqual(self.console_widget.history_index, 1)
        self.console_widget._up_pressed(None)
        line = self.console_widget.document().lastBlock().text()
        self.assertEqual(line, self.console_widget.prompt + lines[0])
        self.assertEqual(self.console_widget.history_index, 0)
        self.console_widget._down_pressed(None)
        line = self.console_widget.document().lastBlock().text()
        self.assertEqual(line, self.console_widget.prompt + lines[1])
        self.assertEqual(self.console_widget.history_index, 2)
        self.console_widget._down_pressed(None)
        line = self.console_widget.document().lastBlock().text()
        self.assertEqual(line, self.console_widget.prompt + current)
        self.assertEqual(self.console_widget.history_index, 2)