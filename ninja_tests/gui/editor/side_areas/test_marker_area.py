from ninja_tests.gui import editor

editor_ref = editor.create_editor()
widget = editor_ref.side_widgets.get("MarkerWidget")


def test_1(qtbot):
    widget.add_bookmark(2)
    widget.add_bookmark(5)
    assert widget.bookmarks == [2, 5]


def test_2(qtbot):
    for i in range(100):
        editor_ref.textCursor().insertBlock()
    widget.add_bookmark(57)
    widget.add_bookmark(20)
    widget.add_bookmark(5)
    widget.add_bookmark(97)
    widget.add_bookmark(100)
    editor_ref.cursor_position = 16, 0
    widget.next_bookmark()
    line, _ = editor_ref.cursor_position
    assert line == 20
    widget.previous_bookmark()
    line, _ = editor_ref.cursor_position
    assert line == 5


def test_3():
    for i in range(190):
        editor_ref.textCursor().insertBlock()
    widget.add_bookmark(20)
    widget.add_bookmark(5)
    widget.add_bookmark(54)
    widget.add_bookmark(124)
    widget.add_bookmark(189)
    editor_ref.cursor_position = 130, 0
    widget.next_bookmark()
    line, _ = editor_ref.cursor_position
    assert line == 189
    widget.previous_bookmark()
    line, _ = editor_ref.cursor_position
    assert line == 124
    widget.next_bookmark()
    widget.next_bookmark()
    widget.next_bookmark()
    line, _ = editor_ref.cursor_position
    assert line == 5
