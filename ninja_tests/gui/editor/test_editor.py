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

from unittest.mock import Mock

import pytest

from PyQt5.QtGui import QTextCursor

from PyQt5.QtCore import Qt

from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import neditable
from ninja_ide.core.file_handling import nfile
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import json_manager


IDE.register_service("ide", Mock())
import ninja_ide.intellisensei.intellisense_registry  # noqa
# IDE.register_service("intellisense", Mock())
json_manager.load_syntax()


@pytest.fixture
def editor_bot(qtbot):
    editable = neditable.NEditable(nfile.NFile())
    _editor = editor.create_editor(editable)
    return _editor


def test_replace(editor_bot, qtbot):
    editor_bot.text = "this gabo is Gabo a testGaBo aslkd laskd"
    editor_bot.moveCursor(QTextCursor.Start)
    editor_bot.find_match("gabo")
    editor_bot.replace_match("gabo", "gaboxx")
    editor_bot.find_match("gabo")
    editor_bot.replace_match("gabo", "gaboxx")
    assert editor_bot.text == "this gaboxx is gaboxx a testGaBo aslkd laskd"


def test_replace_all(editor_bot, qtbot):
    editor_bot.text = "this gabo is Gabo a testGaBo aslkd laskd"
    editor_bot.moveCursor(QTextCursor.Start)
    editor_bot.replace_all("gabo", "gabox")
    assert editor_bot.text == "this gabox is gabox a testgabox aslkd laskd"


def test_replace_cs(editor_bot, qtbot):
    editor_bot.text = "this gabo is Gabo a testGaBo aslkd laskd"
    editor_bot.moveCursor(QTextCursor.Start)
    editor_bot.find_match("Gabo", case_sensitive=True)
    editor_bot.replace_match("Gabo", "GABO", cs=True)
    assert editor_bot.text == "this gabo is GABO a testGaBo aslkd laskd"


def test_replace_wo(editor_bot, qtbot):
    editor_bot.text = "this gabo is Gabo a testGaBo aslkd laskd"
    editor_bot.moveCursor(QTextCursor.Start)
    editor_bot.replace_all("gabo", "GABO", wo=True)
    assert editor_bot.text == "this GABO is GABO a testGaBo aslkd laskd"


def test_move_up(editor_bot, qtbot):
    editor_bot.text = 'print\ntype(str)'
    cursor = editor_bot.textCursor()
    cursor.movePosition(QTextCursor.End)
    editor_bot.setTextCursor(cursor)
    editor_bot.move_up_down(up=True)
    assert editor_bot.text == 'type(str)\nprint\n'


def test_move_down(editor_bot, qtbot):
    editor_bot.text = 'print\ntype(str)'
    cursor = editor_bot.textCursor()
    cursor.movePosition(QTextCursor.Start)
    editor_bot.setTextCursor(cursor)
    editor_bot.move_up_down()
    assert editor_bot.text == 'type(str)\nprint'


def test_move_up_selection(editor_bot, qtbot):
    editor_bot.text = 'print\nprint\nprint\nninja\nninja'
    cursor = editor_bot.textCursor()
    cursor.movePosition(QTextCursor.End)
    cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
    cursor.movePosition(QTextCursor.Up, QTextCursor.KeepAnchor)
    cursor.movePosition(QTextCursor.Up, QTextCursor.KeepAnchor)
    editor_bot.setTextCursor(cursor)
    editor_bot.move_up_down(True)
    editor_bot.move_up_down(True)
    assert editor_bot.text == 'print\nninja\nninja\nprint\nprint\n'


def test_move_down_selection(editor_bot, qtbot):
    editor_bot.text = 'print\nprint\nprint\nninja\nninja'
    cursor = editor_bot.textCursor()
    cursor.movePosition(QTextCursor.Start)
    cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
    cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
    cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
    editor_bot.setTextCursor(cursor)
    editor_bot.move_up_down()
    editor_bot.move_up_down()
    assert editor_bot.text == 'ninja\nninja\nprint\nprint\nprint'


def test_simple_comment(editor_bot, qtbot):
    editor_bot.text = "this\nis\na\ntext"
    editor_bot.comment_or_uncomment()
    assert editor_bot.text == "# this\nis\na\ntext"


def test_simple_uncomment(editor_bot, qtbot):
    editor_bot.text = "# this\nis\na\ntext"
    editor_bot.comment_or_uncomment()
    assert editor_bot.text == "this\nis\na\ntext"


def test_comment_selected_lines(editor_bot, qtbot):
    editor_bot.text = "this\nis\na\ntext"
    editor_bot.selectAll()
    editor_bot.comment_or_uncomment()
    assert editor_bot.text == "# this\n# is\n# a\n# text"


def test_uncomment_selected_lines(editor_bot, qtbot):
    editor_bot.text = "# this\n# is\n# a\n# text"
    editor_bot.selectAll()
    editor_bot.comment_or_uncomment()
    assert editor_bot.text == "this\nis\na\ntext"


def test_comment(editor_bot, qtbot):
    editor_bot.text = "# This is a comment\ndef foo():\n    # pass\n    pass"
    editor_bot.selectAll()
    editor_bot.comment_or_uncomment()
    assert editor_bot.text == ("# # This is a comment\n# def foo():\n#     "
                               "# pass\n#     pass")


def test_uncomment(editor_bot, qtbot):
    editor_bot.text = ("# # This is a comment\n# def foo():\n#     "
                       "# pass\n#     pass")
    editor_bot.selectAll()
    editor_bot.comment_or_uncomment()
    assert editor_bot.text == ("# This is a comment\ndef foo():\n    "
                               "# pass\n    pass")


def test_uncomment2(editor_bot, qtbot):
    editor_bot.text = "print\n# print"
    editor_bot.selectAll()
    editor_bot.comment_or_uncomment()
    assert editor_bot.text == "# print\n# # print"


def test_complete_declaration(editor_bot, qtbot):
    editor_bot.text = "class Parent(object):"
    cursor = editor_bot.textCursor()
    cursor.movePosition(QTextCursor.End)
    editor_bot.setTextCursor(cursor)
    qtbot.keyPress(editor_bot, Qt.Key_Enter)
    assert editor_bot.text == ("class Parent(object):\n    \n"
                               "    def __init__(self):\n"
                               "        ")


def test_complete_declaration2(editor_bot, qtbot):
    editor_bot.text = "class Parent(object):"
    cursor = editor_bot.textCursor()
    cursor.movePosition(QTextCursor.End)
    editor_bot.setTextCursor(cursor)
    qtbot.keyPress(editor_bot, Qt.Key_Enter)
    assert editor_bot.text == ("class Parent(object):\n    \n"
                               "    def __init__(self):\n"
                               "        ")
    editor_bot.moveCursor(QTextCursor.Start)
    editor_bot.moveCursor(QTextCursor.EndOfLine)
    qtbot.keyPress(editor_bot, Qt.Key_Enter)
    assert editor_bot.text == ("class Parent(object):\n    \n    \n"
                               "    def __init__(self):\n"
                               "        ")


def test_complete_declaration_with_parent(editor_bot, qtbot):
    editor_bot.text = ("class Parent(object):\n"
                       "    pass"
                       "\n"
                       "class Child(Parent):")

    cursor = editor_bot.textCursor()
    cursor.movePosition(QTextCursor.End)
    editor_bot.setTextCursor(cursor)
    qtbot.keyPress(editor_bot, Qt.Key_Enter)
    assert editor_bot.text == ("class Parent(object):\n"
                               "    pass"
                               "\n"
                               "class Child(Parent):\n    \n"
                               "    def __init__(self):\n"
                               "        super(Child, self).__init__()\n"
                               "        ")


if __name__ == "__main__":
    pytest.main()
