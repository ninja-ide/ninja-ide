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

from ninja_ide.gui.editor.base import BaseTextEditor
from ninja_ide.gui.editor.indenter.python_indenter import PythonIndenter


def make_editor():
    editor = BaseTextEditor()
    indenter = PythonIndenter(editor)
    return editor, indenter


def make_indent(text):
    editor, indenter = make_editor()
    editor.text = text
    cursor = editor.textCursor()
    cursor.movePosition(cursor.End)
    editor.setTextCursor(cursor)
    indenter.indent_block(cursor)
    return editor.text


def test_1():
    assert make_indent('def foo():') == 'def foo():\n    '


def test_2():
    text = make_indent('def foo():\n    pass')
    assert text == 'def foo():\n    pass\n'


def test_3():
    text = make_indent('def foo():\n    def inner():')
    assert text == 'def foo():\n    def inner():\n        '


def test_4():
    text = make_indent("def foo():\n    def inner():\n        pass")
    assert text == 'def foo():\n    def inner():\n        pass\n    '


def test_5():
    text = make_indent("lista = [23,")
    assert text == 'lista = [23,\n         '


def test_6():
    text = make_indent('def foo(*args,')
    assert text == 'def foo(*args,\n        '


def test_7():
    a_text = "def foo(arg1,\n        arg2, arg3):"
    text = make_indent(a_text)
    assert text == 'def foo(arg1,\n        arg2, arg3):\n    '


def test_8():
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


def test_9():
    a_text = """# comment
    lista = [32,
             3232332323, [3232,"""
    text = make_indent(a_text)
    expected = """# comment
    lista = [32,
             3232332323, [3232,
                          """
    assert text == expected


def test_10():
    # Hang indent
    # text = make_indent('tupla = (')
    # assert text == 'tupla = (\n    '
    pass


def test_11():
    a_text = "def foo():\n    def inner():\n        return foo()"
    text = make_indent(a_text)
    expected = "def foo():\n    def inner():\n        return foo()\n    "
    assert text == expected


def test_12():
    a_text = """if __name__ == "__main__":
    nombre = input('Nombre: ')
    print(nombre)"""
    text = make_indent(a_text)
    expected = """if __name__ == "__main__":
    nombre = input('Nombre: ')
    print(nombre)
    """
    assert text == expected


def test_13():
    a_text = "d = []"
    editor, indenter = make_editor()
    editor.text = a_text
    editor.cursor_position = 1, 5
    indenter.indent_block(editor.textCursor())
    expected = "d = [\n    \n]"
    assert editor.text == expected


def test_14():
    a_text = "d = ['one', 'two']"
    editor, indenter = make_editor()
    editor.text = a_text
    editor.cursor_position = 1, 5
    indenter.indent_block(editor.textCursor())
    expected = "d = [\n    'one', 'two']"
    assert editor.text == expected


def test_15():
    """
    {
        {
        },
        | <-- cursor
    }
    """
    a_text = "{\n    {\n    },\n}"
    editor, indenter = make_editor()
    editor.text = a_text
    editor.cursor_position = 2, 6
    indenter.indent_block(editor.textCursor())
    expected = '{\n    {\n    },\n    \n}'
    assert editor.text == expected
    assert editor.cursor_position == (3, 4)


def test_16():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,"
    editor, indenter = make_editor()
    editor.text = a_text
    editor.cursor_position = 1, 13
    indenter.indent_block(editor.textCursor())
    expected = "x = [0, 1, 2,\n     "
    assert editor.text == expected


def test_22():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,\n     [3, 4, 5,"
    editor, indenter = make_editor()
    editor.text = a_text
    editor.cursor_position = 2, 14
    indenter.indent_block(editor.textCursor())
    expected = "x = [0, 1, 2,\n     [3, 4, 5,\n      "
    assert editor.text == expected


def test_23():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,\n     [3, 4, 5,\n      6, 7, 8],"
    editor, indenter = make_editor()
    editor.text = a_text
    editor.cursor_position = 3, 15
    indenter.indent_block(editor.textCursor())
    expected = "x = [0, 1, 2,\n     [3, 4, 5,\n      6, 7, 8],\n     "
    assert editor.text == expected


def test_24():
    """
    x = [
        0, 1, 2, [3, 4, 5,
                  6, 7, 8],
        9, 10, 11
    ]
    """

    a_text = "x = [\n    0, 1, 2, [3, 4, 5,"
    editor, indenter = make_editor()
    editor.text = a_text
    editor.cursor_position = 1, 22
    indenter.indent_block(editor.textCursor())
    expected = "x = [\n    0, 1, 2, [3, 4, 5,\n              "
    assert editor.text == expected


def test_25():
    """
    x = [
        0, 1, 2, [3, 4, 5,
                  6, 7, 8],
        9, 10, 11
    ]
    """

    a_text = "x = [\n    0, 1, 2, [3, 4, 5,\n              6, 7, 8],"
    editor, indenter = make_editor()
    editor.text = a_text
    editor.cursor_position = 2, 23
    indenter.indent_block(editor.textCursor())
    expected = "x = [\n    0, 1, 2, [3, 4, 5,\n              6, 7, 8],\n    "
    assert editor.text == expected


def test_26():
    expected = 'def foo():\n    {}\n'
    for kw in ('break', 'continue', 'raise', 'pass', 'return'):
        assert make_indent('def foo():\n    {}'.format(kw)) == expected.format(kw)