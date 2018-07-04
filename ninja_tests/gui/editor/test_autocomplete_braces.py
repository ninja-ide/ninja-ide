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

from ninja_ide import resources
from ninja_ide.gui.editor import editor

from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import Qt

# FIXME: use mock
from ninja_ide.gui.explorer.tabs import bookmark_manager  # noqa

resources.COLOR_SCHEME = {"colors": []}


@pytest.fixture
def editor_bot(qtbot):
    editable = Mock()
    editable.document = QTextDocument()
    _editor = editor.create_editor(editable)
    return _editor


@pytest.mark.parametrize(
    "text, expected_text, column",
    [
        ("[", "[]", 1),
        ("{", "{}", 1),
        ("(", "()", 1)
    ])
def test_close_braces(qtbot, editor_bot, text, expected_text, column):
    qtbot.keyClicks(editor_bot, text)
    assert editor_bot.text == expected_text
    _, col = editor_bot.cursor_position
    assert col == column


@pytest.mark.parametrize(
    "text, expected_text, column",
    [
        ("[]", "[]", 2),
        ("{}", "{}", 2),
        ("()", "()", 2)
    ])
def test_close_braces2(qtbot, editor_bot, text, expected_text, column):
    qtbot.keyClicks(editor_bot, text)

    assert editor_bot.text == expected_text
    _, col = editor_bot.cursor_position
    assert col == column


@pytest.mark.parametrize(
    "text, expected_text, column",
    [
        ("[[[[[[[[[[", "[[[[[[[[[[]]]]]]]]]]", 10),
        ("{{{{{{{{{{", "{{{{{{{{{{}}}}}}}}}}", 10),
        ("((((((((((", "(((((((((())))))))))", 10)
    ])
def test_close_braces3(qtbot, editor_bot, text, expected_text, column):
    qtbot.keyClicks(editor_bot, text)

    assert editor_bot.text == expected_text
    _, col = editor_bot.cursor_position
    assert col == column


def test_close_braces4(editor_bot, qtbot):
    editor_bot.text = "test content"
    cursor = editor_bot.textCursor()
    cursor.movePosition(cursor.EndOfBlock)
    editor_bot.setTextCursor(cursor)
    # Press '('
    qtbot.keyPress(editor_bot, Qt.Key_ParenLeft)
    assert editor_bot.text == "test content()"


def test_close_braces5(editor_bot, qtbot):
    editor_bot.text = "test content"
    cursor = editor_bot.textCursor()
    cursor.movePosition(cursor.EndOfBlock)
    cursor.movePosition(cursor.Left)
    editor_bot.setTextCursor(cursor)
    # Press '('
    qtbot.keyPress(editor_bot, Qt.Key_ParenLeft)
    assert editor_bot.text == "test conten(t"


if __name__ == "__main__":
    pytest.main()
