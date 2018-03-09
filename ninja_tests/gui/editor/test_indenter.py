from ninja_tests.gui.editor import create_editor


def make_indent(text, language=None):
    """Indent last line of text"""
    editor_ref = create_editor(language)

    editor_ref.text = text
    cursor = editor_ref.textCursor()
    cursor.movePosition(cursor.End)
    editor_ref.setTextCursor(cursor)
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    return editor_ref.text


def make_indent_with_tab(text, selection=False, n=1):
    editor_ref = create_editor()
    editor_ref.text = text
    for i in range(n):
        if selection:
            editor_ref.selectAll()
            editor_ref._indenter.indent_selection()
        else:
            editor_ref._indenter.indent()
    return editor_ref.text


def test_1():
    assert make_indent('ninja') == 'ninja\n'


def test_2():
    assert make_indent('  ninjas') == '  ninjas\n  '


def test_3():
    text = make_indent('def foo():', language='python')
    assert text == 'def foo():\n    '


def test_4():
    text = make_indent('def foo():\n    pass', language='python')
    assert text == 'def foo():\n    pass\n'


def test_5():
    text = make_indent('def foo():\n    def inner():', language='python')
    assert text == 'def foo():\n    def inner():\n        '


def test_6():
    text = make_indent("def foo():\n    def inner():\n        pass", "python")
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
    text = make_indent("lista = [23,", 'python')
    assert text == 'lista = [23,\n         '


def test_11():
    text = make_indent('def foo(*args,', 'python')
    assert text == 'def foo(*args,\n        '


def test_12():
    a_text = "def foo(arg1,\n        arg2, arg3):"
    text = make_indent(a_text, 'python')
    assert text == 'def foo(arg1,\n        arg2, arg3):\n    '


def test_13():
    a_text = """# Comment
    class A(object):
        def __init__(self):
            self._val = 0

        def foo(self):
            def bar(arg1,
                    arg2):"""

    text = make_indent(a_text, 'python')
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
    text = make_indent(a_text, 'python')
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
    text = make_indent(a_text, 'python')
    expected = "def foo():\n    def inner():\n        return foo()\n    "
    assert text == expected


def test_17():
    a_text = """if __name__ == "__main__":
    nombre = input('Nombre: ')
    print(nombre)"""
    text = make_indent(a_text, 'python')
    expected = """if __name__ == "__main__":
    nombre = input('Nombre: ')
    print(nombre)
    """
    assert text == expected


def test_18():
    a_text = "d = []"
    editor_ref = create_editor('python')
    editor_ref.text = a_text
    editor_ref.cursor_position = 1, 5
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    expected = "d = [\n    \n]"
    assert editor_ref.text == expected


def test_19():
    a_text = "d = ['one', 'two']"
    editor_ref = create_editor('python')
    editor_ref.text = a_text
    editor_ref.cursor_position = 1, 5
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    expected = "d = [\n    'one', 'two']"
    assert editor_ref.text == expected


def test_20():
    """
    {
        {
        },
        | <-- cursor
    }
    """
    a_text = "{\n    {\n    },\n}"
    editor_ref = create_editor("python")
    editor_ref.text = a_text
    editor_ref.cursor_position = 2, 6
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    expected = '{\n    {\n    },\n    \n}'
    assert editor_ref.text == expected
    assert editor_ref.cursor_position == (3, 4)


def test_21():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,"
    editor_ref = create_editor("python")
    editor_ref.text = a_text
    editor_ref.cursor_position = 1, 13
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    expected = "x = [0, 1, 2,\n     "
    assert editor_ref.text == expected


def test_22():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,\n     [3, 4, 5,"
    editor_ref = create_editor("python")
    editor_ref.text = a_text
    editor_ref.cursor_position = 2, 14
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    expected = "x = [0, 1, 2,\n     [3, 4, 5,\n      "
    assert editor_ref.text == expected


def test_23():
    """
    x = [0, 1, 2,
         [3, 4, 5,
          6, 7, 8],
         9, 10, 11]
    """

    a_text = "x = [0, 1, 2,\n     [3, 4, 5,\n      6, 7, 8],"
    editor_ref = create_editor("python")
    editor_ref.text = a_text
    editor_ref.cursor_position = 3, 15
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    expected = "x = [0, 1, 2,\n     [3, 4, 5,\n      6, 7, 8],\n     "
    assert editor_ref.text == expected


def test_24():
    """
    x = [
        0, 1, 2, [3, 4, 5,
                  6, 7, 8],
        9, 10, 11
    ]
    """

    a_text = "x = [\n    0, 1, 2, [3, 4, 5,"
    editor_ref = create_editor("python")
    editor_ref.text = a_text
    editor_ref.cursor_position = 1, 22
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    expected = "x = [\n    0, 1, 2, [3, 4, 5,\n              "
    assert editor_ref.text == expected


def test_25():
    """
    x = [
        0, 1, 2, [3, 4, 5,
                  6, 7, 8],
        9, 10, 11
    ]
    """

    a_text = "x = [\n    0, 1, 2, [3, 4, 5,\n              6, 7, 8],"
    editor_ref = create_editor("python")
    editor_ref.text = a_text
    editor_ref.cursor_position = 2, 23
    editor_ref._indenter.indent_block(editor_ref.textCursor())
    expected = "x = [\n    0, 1, 2, [3, 4, 5,\n              6, 7, 8],\n    "
    assert editor_ref.text == expected
