import pytest

from PyQt5.QtWidgets import QPlainTextEdit

from ninja_ide.gui.editor.indenter import base


class DummyEditor(QPlainTextEdit):

    def __enter__(self):
        self.textCursor().beginEditBlock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.textCursor().endEditBlock()


@pytest.fixture
def code_editor():
    editor = DummyEditor()
    indenter = base.BasicIndenter(editor)
    return editor, indenter


@pytest.mark.parametrize(
    'text, expected',
    [
        ('  def foo():', '  def foo():\n  '),
        ('   def foo():', '   def foo():\n   '),
        ('def foo():', 'def foo():\n'),
        ('          def foo():', '          def foo():\n          ')
    ]
)
def test_basic_indenter(code_editor, text, expected):
    editor, indenter = code_editor
    editor.setPlainText(text)
    cursor = editor.textCursor()
    cursor.movePosition(cursor.EndOfLine)
    editor.setTextCursor(cursor)
    indenter.indent_block(cursor)
    assert editor.toPlainText() == expected


@pytest.mark.parametrize(
    'text, use_tab, expected',
    [
        ('  def foo():', False, '  def foo():\n  '),
        ('\tdef foo():', True, '\tdef foo():\n\t')
    ]
)
def test_text(code_editor, text, use_tab, expected):
    editor, indenter = code_editor
    editor.setPlainText(text)
    cursor = editor.textCursor()
    cursor.movePosition(cursor.EndOfLine)
    editor.setTextCursor(cursor)

    indenter.use_tabs = use_tab
    if use_tab:
        text = '\t'
    else:
        text = '    '
    assert indenter.text() == text
    indenter.indent_block(cursor)
    assert editor.toPlainText() == expected


@pytest.mark.parametrize(
    'text, width, expected, use_tab',
    [
        ('def foo():', 4, 'def foo():  ', False),
        ('def foo():', 2, 'def foo():  ', False),
        ('def foooo():', 4, 'def foooo():    ', False),
        ('def foo():', 1, 'def foo():\t', True)
    ]
)
def test_indent(code_editor, text, width, expected, use_tab):
    editor, indenter = code_editor
    editor.setPlainText(text)
    cursor = editor.textCursor()
    cursor.movePosition(cursor.EndOfLine)
    editor.setTextCursor(cursor)
    indenter.width = width
    indenter.use_tabs = use_tab
    indenter.indent()
    assert editor.toPlainText() == expected


@pytest.mark.parametrize(
    'text, n, expected',
    [
        ('ninja\nide', 1, '    ninja\n    ide'),
        ('ninja\nide', 2, '        ninja\n        ide'),
        ('ninja', 4, '                ninja')
    ]
)
def test_indent_selection(code_editor, text, n, expected):
    editor, indenter = code_editor
    editor.setPlainText(text)
    editor.selectAll()
    for i in range(n):
        indenter.indent_selection()
    assert editor.toPlainText() == expected
