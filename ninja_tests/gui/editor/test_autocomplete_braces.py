from PyQt5.QtCore import Qt
from ninja_tests.gui.editor import create_editor


def test_1(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_ParenLeft)
    assert editor_ref.text == '()'
    _, col = editor_ref.cursor_position
    assert col == 1


def test_2(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_BraceLeft)
    assert editor_ref.text == '{}'
    _, col = editor_ref.cursor_position
    assert col == 1


def test_3(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_BracketLeft)
    assert editor_ref.text == '[]'
    _, col = editor_ref.cursor_position
    assert col == 1


def test_4(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_BracketLeft)
    assert editor_ref.text == '[]'
    qtbot.keyPress(editor_ref, Qt.Key_BracketRight)
    assert editor_ref.text == '[]'
    _, col = editor_ref.cursor_position
    assert col == 2


def test_5(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_BraceLeft)
    assert editor_ref.text == '{}'
    qtbot.keyPress(editor_ref, Qt.Key_BraceRight)
    assert editor_ref.text == '{}'
    _, col = editor_ref.cursor_position
    assert col == 2


def test_6(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_ParenLeft)
    assert editor_ref.text == '()'
    qtbot.keyPress(editor_ref, Qt.Key_ParenRight)
    assert editor_ref.text == '()'
    _, col = editor_ref.cursor_position
    assert col == 2


def test_7(qtbot):
    editor_ref = create_editor()
    qtbot.keyPress(editor_ref, Qt.Key_BracketLeft)
    qtbot.keyPress(editor_ref, Qt.Key_Backspace)
    assert editor_ref.text == ''


def test_8(qtbot):
    editor_ref = create_editor()
    repeat = 10
    for i in range(repeat):
        qtbot.keyPress(editor_ref, Qt.Key_BraceLeft)
    assert editor_ref.text == '{{{{{{{{{{}}}}}}}}}}'
    for i in range(repeat - 1):
        qtbot.keyPress(editor_ref, Qt.Key_Backspace)
    assert editor_ref.text == '{}'


def test_9(qtbot):
    editor_ref = create_editor()
    editor_ref.text = "test content"
    cursor = editor_ref.textCursor()
    cursor.movePosition(cursor.EndOfBlock)
    editor_ref.setTextCursor(cursor)
    # Press '('
    qtbot.keyPress(editor_ref, Qt.Key_ParenLeft)
    assert editor_ref.text == "test content()"


def test_10(qtbot):
    editor_ref = create_editor()
    editor_ref.text = "test content"
    cursor = editor_ref.textCursor()
    cursor.movePosition(cursor.EndOfBlock)
    cursor.movePosition(cursor.Left)
    editor_ref.setTextCursor(cursor)
    # Press '('
    qtbot.keyPress(editor_ref, Qt.Key_ParenLeft)
    assert editor_ref.text == "test conten(t"
