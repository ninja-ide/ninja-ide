from ninja_tests.gui.editor import create_editor
from ninja_ide.gui.editor import helpers
from ninja_ide.tools import json_manager
json_manager.load_syntax()
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


def test_simple_comment(qtbot):
    editor_ref = create_editor("python")
    editor_ref.text = "this\nis\na\ntext"
    helpers.comment_or_uncomment(editor_ref)
    assert editor_ref.text == "# this\nis\na\ntext"


def test_simple_uncomment(qtbot):
    editor_ref = create_editor("python")
    editor_ref.text = "# this\nis\na\ntext"
    helpers.comment_or_uncomment(editor_ref)
    assert editor_ref.text == "this\nis\na\ntext"


def test_comment_selected_lines(qtbot):
    editor_ref = create_editor("python")
    editor_ref.text = "this\nis\na\ntext"
    editor_ref.selectAll()
    helpers.comment_or_uncomment(editor_ref)
    assert editor_ref.text == "# this\n# is\n# a\n# text"


def test_uncomment_selected_lines(qtbot):
    editor_ref = create_editor("python")
    editor_ref.text = "# this\n# is\n# a\n# text"
    editor_ref.selectAll()
    helpers.comment_or_uncomment(editor_ref)
    assert editor_ref.text == "this\nis\na\ntext"


def test_comment(qtbot):
    editor_ref = create_editor("python")
    editor_ref.text = "# This is a comment\ndef foo():\n    # pass\n    pass"
    editor_ref.selectAll()
    helpers.comment_or_uncomment(editor_ref)
    assert editor_ref.text == ("# # This is a comment\n# def foo():\n#     "
                               "# pass\n#     pass")


def test_uncomment(qtbot):
    editor_ref = create_editor("python")
    editor_ref.text = ("# # This is a comment\n# def foo():\n#     "
                       "# pass\n#     pass")
    editor_ref.selectAll()
    helpers.comment_or_uncomment(editor_ref)
    assert editor_ref.text == ("# This is a comment\ndef foo():\n    "
                               "# pass\n    pass")


def test_uncomment2(qtbot):
    editor_ref = create_editor("python")
    editor_ref.text = "print\n# print"
    editor_ref.selectAll()
    helpers.comment_or_uncomment(editor_ref)
    assert editor_ref.text == "# print\n# # print"
