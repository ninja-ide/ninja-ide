from ninja_tests.gui.editor.side_areas import get_marker_area


def test_1(qtbot):
    area = get_marker_area()
    area.add_bookmark(2)
    area.add_bookmark(5)
    assert area.bookmarks == [2, 5]


def test_2(qtbot):
    area = get_marker_area()
    editor = area.parentWidget()
    for i in range(100):
        editor.textCursor().insertBlock()
    area.add_bookmark(57)
    area.add_bookmark(20)
    area.add_bookmark(5)
    area.add_bookmark(97)
    area.add_bookmark(100)
    editor.cursor_position = 16, 0
    area.next_bookmark()
    line, _ = editor.cursor_position
    assert line == 20
    area.previous_bookmark()
    line, _ = editor.cursor_position
    assert line == 5


def test_3():
    area = get_marker_area()
    editor = area.parentWidget()
    for i in range(190):
        editor.textCursor().insertBlock()
    area.add_bookmark(20)
    area.add_bookmark(5)
    area.add_bookmark(54)
    area.add_bookmark(124)
    area.add_bookmark(189)
    editor.cursor_position = 130, 0
    area.next_bookmark()
    line, _ = editor.cursor_position
    assert line == 189
    area.previous_bookmark()
    line, _ = editor.cursor_position
    assert line == 124
    area.next_bookmark()
    area.next_bookmark()
    area.next_bookmark()
    line, _ = editor.cursor_position
    assert line == 20
