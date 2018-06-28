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


def make_editor():
    editable = Mock()
    editable.document = QTextDocument()
    editable.language = lambda: "python"
    _editor = editor.create_editor(editable)
    return _editor


def make_indent(text):
    """Indent last line of text"""

    editor_bot = make_editor()
    editor_bot.text = text
    cursor = editor_bot.textCursor()
    cursor.movePosition(cursor.End)
    editor_bot.setTextCursor(cursor)
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    return editor_bot.text


def make_indent_with_tab(text, selection=False, n=1):
    editor_bot = make_editor()
    editor_bot.text = text
    for i in range(n):
        if selection:
            editor_bot.selectAll()
            editor_bot._indenter.indent_selection()
        else:
            editor_bot._indenter.indent()
    return editor_bot.text


def test_1():
    assert make_indent('ninja') == 'ninja\n'


def test_2():
    assert make_indent('  ninjas') == '  ninjas\n  '


def test_3():
    text = make_indent('def foo():')
    assert text == 'def foo():\n    '


def test_4():
    text = make_indent('def foo():\n    pass')
    assert text == 'def foo():\n    pass\n'


def test_5():
    text = make_indent('def foo():\n    def inner():')
    assert text == 'def foo():\n    def inner():\n        '


def test_6():
    text = make_indent("def foo():\n    def inner():\n        pass")
    assert text == 'def foo():\n    def inner():\n        pass\n    '


def test_7():
    text = make_indent_with_tab('ninja-ide')
    assert text == '    ninja-ide'


def test_8():
    text = make_indent_with_tab('ninja-ide', n=3)
    assert text == '            ninja-ide'


def test_9():
    text = make_indent_with_tab('ninja-ide\nninja-ide', True)
    assert text == '    ninja-ide\n    ninja-ide'


def test_10():
    text = make_indent("lista = [23,")
    assert text == 'lista = [23,\n         '


def test_11():
    text = make_indent('def foo(*args,')
    assert text == 'def foo(*args,\n        '


def test_12():
    a_text = "def foo(arg1,\n        arg2, arg3):"
    text = make_indent(a_text)
    assert text == 'def foo(arg1,\n        arg2, arg3):\n    '


def test_13():
    a_text = """# Comment
    class A(object):
        def __init__(self):
            self._val = 0

        def foo(self):
            def bar(arg1,
                    arg2):"""

    text = make_indent(a_text)
    expected = """# Comment
    class A(object):
        def __init__(self):
            self._val = 0

        def foo(self):
            def bar(arg1,
                    arg2):
                """
    assert text == expected


def test_14():
    a_text = """# comment
    lista = [32,
             3232332323, [3232,"""
    text = make_indent(a_text)
    expected = """# comment
    lista = [32,
             3232332323, [3232,
                          """
    assert text == expected


def test_15():
    # Hang indent
    # text = make_indent('tupla = (')
    # assert text == 'tupla = (\n    '
    pass


def test_16():
    a_text = "def foo():\n    def inner():\n        return foo()"
    text = make_indent(a_text)
    expected = "def foo():\n    def inner():\n        return foo()\n    "
    assert text == expected


def test_17():
    a_text = """if __name__ == "__main__":
    nombre = input('Nombre: ')
    print(nombre)"""
    text = make_indent(a_text)
    expected = """if __name__ == "__main__":
    nombre = input('Nombre: ')
    print(nombre)
    """
    assert text == expected


def test_18():
    a_text = "d = []"
    editor_bot = make_editor()
    editor_bot.text = a_text
    editor_bot.cursor_position = 1, 5
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    expected = "d = [\n    \n]"
    assert editor_bot.text == expected


def test_19():
    a_text = "d = ['one', 'two']"
    editor_bot = make_editor()
    editor_bot.text = a_text
    editor_bot.cursor_position = 1, 5
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    expected = "d = [\n    'one', 'two']"
    assert editor_bot.text == expected


def test_20():
    """
    {
        {
        },
        | <-- cursor
    }
    """
    a_text = "{\n    {\n    },\n}"
    editor_bot = make_editor()
    editor_bot.text = a_text
    editor_bot.cursor_position = 2, 6
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    expected = '{\n    {\n    },\n    \n}'
    assert editor_bot.text == expected
    assert editor_bot.cursor_position == (3, 4)


def test_21():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,"
    editor_bot = make_editor()
    editor_bot.text = a_text
    editor_bot.cursor_position = 1, 13
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    expected = "x = [0, 1, 2,\n     "
    assert editor_bot.text == expected


def test_22():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,\n     [3, 4, 5,"
    editor_bot = make_editor()
    editor_bot.text = a_text
    editor_bot.cursor_position = 2, 14
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    expected = "x = [0, 1, 2,\n     [3, 4, 5,\n      "
    assert editor_bot.text == expected


def test_23():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,\n     [3, 4, 5,\n      6, 7, 8],"
    editor_bot = make_editor()
    editor_bot.text = a_text
    editor_bot.cursor_position = 3, 15
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    expected = "x = [0, 1, 2,\n     [3, 4, 5,\n      6, 7, 8],\n     "
    assert editor_bot.text == expected


def test_24():
    """
    x = [
        0, 1, 2, [3, 4, 5,
                  6, 7, 8],
        9, 10, 11
    ]
    """

    a_text = "x = [\n    0, 1, 2, [3, 4, 5,"
    editor_bot = make_editor()
    editor_bot.text = a_text
    editor_bot.cursor_position = 1, 22
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    expected = "x = [\n    0, 1, 2, [3, 4, 5,\n              "
    assert editor_bot.text == expected


def test_25():
    """
    x = [
        0, 1, 2, [3, 4, 5,
                  6, 7, 8],
        9, 10, 11
    ]
    """

    a_text = "x = [\n    0, 1, 2, [3, 4, 5,\n              6, 7, 8],"
    editor_bot = make_editor()
    editor_bot.text = a_text
    editor_bot.cursor_position = 2, 23
    editor_bot._indenter.indent_block(editor_bot.textCursor())
    expected = "x = [\n    0, 1, 2, [3, 4, 5,\n              6, 7, 8],\n    "
    assert editor_bot.text == expected


if __name__ == "__main__":
    pytest.main()
