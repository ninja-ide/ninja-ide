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

import pytest
from unittest.mock import Mock

from ninja_ide.gui.editor import editor

from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import Qt


@pytest.fixture
def editor_bot(qtbot):
    editable = Mock()
    editable.document = QTextDocument()
    _editor = editor.create_editor(editable)
    return _editor


@pytest.mark.parametrize(
    "text, expected_text, column",
    [
        ("'", "''", 1),
        ("''", "''", 2),
        ('"', '""', 1),
        ('""', '""', 2),
        ("''''", "''''''", 3),
        ('""""', '""""""', 3)
    ])
def test_close_quotes(qtbot, editor_bot, text, expected_text, column):
    qtbot.keyClicks(editor_bot, text)
    assert editor_bot.text == expected_text
    _, col = editor_bot.cursor_position
    assert col == column


def test_autocomplete_single_selection(editor_bot, qtbot):
    editor_bot.text = 'ninja-ide rocks!'
    editor_bot.selectAll()
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    assert editor_bot.text == '"ninja-ide rocks!"'


def test_autocomplete_multiline_selection(editor_bot, qtbot):
    editor_bot.text = 'ninja-ide rocks!\nholaaaa\nkokoko'
    editor_bot.selectAll()
    qtbot.keyPress(editor_bot, Qt.Key_Apostrophe)
    assert editor_bot.text == "'ninja-ide rocks!\nholaaaa\nkokoko'"


def test_autocomplete_multiline_selection2(editor_bot, qtbot):
    editor_bot.text = 'ninja-ide rocks!\nholaaaa\nkokoko'
    editor_bot.selectAll()
    for i in range(5):
        qtbot.keyPress(editor_bot, Qt.Key_Apostrophe)
    assert editor_bot.text == "'''''ninja-ide rocks!\nholaaaa\nkokoko'''''"


def test_autocomplete_triple_double_quotes(editor_bot, qtbot):
    qtbot.keyPress(editor_bot, Qt.Key_Return)
    qtbot.keyPress(editor_bot, Qt.Key_Return)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)

    assert editor_bot.text == '\n\n""""""'
    _, col = editor_bot.cursor_position
    assert col == 3


def test_autocomplete_triple_double_quotes2(editor_bot, qtbot):
    qtbot.keyPress(editor_bot, Qt.Key_Return)
    qtbot.keyPress(editor_bot, Qt.Key_Return)
    for i in range(4):
        qtbot.keyPress(editor_bot, Qt.Key_Space)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)

    assert editor_bot.text == '\n\n    """"""'
    _, col = editor_bot.cursor_position
    assert col == 7


def test_last(editor_bot, qtbot):
    editor_bot.text = "class NINJA(object):\n    "
    cur = editor_bot.textCursor()
    cur.movePosition(cur.End)
    editor_bot.setTextCursor(cur)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_bot, Qt.Key_QuoteDbl)

    assert editor_bot.text == 'class NINJA(object):\n    """"""'
    _, col = editor_bot.cursor_position
    assert col == 7
    editor_bot.textCursor().insertText('docstring')
    assert editor_bot.text == 'class NINJA(object):\n    """docstring"""'


if __name__ == "__main__":
    pytest.main()
