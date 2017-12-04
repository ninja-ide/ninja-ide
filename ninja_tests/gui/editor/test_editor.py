from ninja_tests.gui.editor import create_editor

# Test move feature


def test_move_up(qtbot):
    editor_ref = create_editor()
    editor_ref.text = 'print\ntype(str)'
    cursor = editor_ref.textCursor()
    cursor.movePosition(cursor.End)
    editor_ref.setTextCursor(cursor)
    editor_ref.move_up_down(up=True)
    assert editor_ref.text == 'type(str)\nprint\n'


def test_move_down(qtbot):
    editor_ref = create_editor()
    editor_ref.text = 'print\ntype(str)'
    cursor = editor_ref.textCursor()
    cursor.movePosition(cursor.Start)
    editor_ref.setTextCursor(cursor)
    editor_ref.move_up_down()
    assert editor_ref.text == 'type(str)\nprint'


def test_move_up_selection(qtbot):
    editor_ref = create_editor()
    editor_ref.text = 'print\nprint\nprint\nninja\nninja'
    cursor = editor_ref.textCursor()
    cursor.movePosition(cursor.End)
    cursor.movePosition(cursor.StartOfBlock, cursor.KeepAnchor)
    cursor.movePosition(cursor.Up, cursor.KeepAnchor)
    cursor.movePosition(cursor.Up, cursor.KeepAnchor)
    editor_ref.setTextCursor(cursor)
    editor_ref.move_up_down(True)
    editor_ref.move_up_down(True)
    assert editor_ref.text == 'print\nninja\nninja\nprint\nprint\n'


def test_move_down_selection(qtbot):
    editor_ref = create_editor()
    editor_ref.text = 'print\nprint\nprint\nninja\nninja'
    cursor = editor_ref.textCursor()
    cursor.movePosition(cursor.Start)
    cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
    cursor.movePosition(cursor.Down, cursor.KeepAnchor)
    cursor.movePosition(cursor.Down, cursor.KeepAnchor)
    editor_ref.setTextCursor(cursor)
    editor_ref.move_up_down()
    editor_ref.move_up_down()
    assert editor_ref.text == 'ninja\nninja\nprint\nprint\nprint'
