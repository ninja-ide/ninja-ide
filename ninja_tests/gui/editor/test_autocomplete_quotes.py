import pytest  # noqa
from PyQt5.QtCore import Qt
from ninja_tests.gui.editor import create_editor


def test_autocomplete_single_selection(qtbot):
    editor_ref = create_editor()
    editor_ref.text = 'ninja-ide rocks!'
    editor_ref.selectAll()
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    assert editor_ref.text == '"ninja-ide rocks!"'


def test_autocomplete_multiline_selection(qtbot):
    editor_ref = create_editor()
    editor_ref.text = 'ninja-ide rocks!\nholaaaa\nkokoko'
    editor_ref.selectAll()
    qtbot.keyPress(editor_ref, Qt.Key_Apostrophe)
    assert editor_ref.text == "'ninja-ide rocks!\nholaaaa\nkokoko'"


def test_autocomplete_multiline_selection2(qtbot):
    editor_ref = create_editor()
    editor_ref.text = 'ninja-ide rocks!\nholaaaa\nkokoko'
    editor_ref.selectAll()
    for i in range(5):
        qtbot.keyPress(editor_ref, Qt.Key_Apostrophe)
    assert editor_ref.text == "'''''ninja-ide rocks!\nholaaaa\nkokoko'''''"


def test_autocomplete_double_quote(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    assert editor_ref.text == '""'
    _, col = editor_ref.cursor_position
    assert col == 1


def test_autocomplete_double_quote2(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    assert editor_ref.text == '""'
    _, col = editor_ref.cursor_position
    assert col == 2


def test_autocomplete_triple_double_quotes(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    assert editor_ref.text == '""""""'
    _, col = editor_ref.cursor_position
    assert col == 3


def test_autocomplete_triple_simple_quotes(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_Apostrophe)
    qtbot.keyPress(editor_ref, Qt.Key_Apostrophe)
    qtbot.keyPress(editor_ref, Qt.Key_Apostrophe)
    qtbot.keyPress(editor_ref, Qt.Key_Apostrophe)
    assert editor_ref.text == "''''''"
    _, col = editor_ref.cursor_position
    assert col == 3


def test_autocomplete_triple_double_quotes2(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_Return)
    qtbot.keyPress(editor_ref, Qt.Key_Return)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)

    assert editor_ref.text == '\n\n""""""'
    _, col = editor_ref.cursor_position
    assert col == 3


def test_autocomplete_triple_double_quotes3(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_Return)
    qtbot.keyPress(editor_ref, Qt.Key_Return)
    for i in range(4):
        qtbot.keyPress(editor_ref, Qt.Key_Space)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)

    assert editor_ref.text == '\n\n    """"""'
    _, col = editor_ref.cursor_position
    assert col == 7


def test_last(qtbot):
    editor_ref = create_editor()
    editor_ref.text = "class NINJA(object):\n    "
    cur = editor_ref.textCursor()
    cur.movePosition(cur.End)
    editor_ref.setTextCursor(cur)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)
    qtbot.keyPress(editor_ref, Qt.Key_QuoteDbl)

    assert editor_ref.text == 'class NINJA(object):\n    """"""'
    _, col = editor_ref.cursor_position
    assert col == 7
    editor_ref.textCursor().insertText('docstring')
    assert editor_ref.text == 'class NINJA(object):\n    """docstring"""'
