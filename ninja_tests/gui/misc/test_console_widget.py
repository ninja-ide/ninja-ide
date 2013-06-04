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