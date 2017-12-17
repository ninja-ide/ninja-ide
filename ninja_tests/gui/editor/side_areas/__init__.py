from ninja_ide.gui.editor.side_area import marker_area
from ninja_tests.gui.editor import create_editor


def get_marker_area():
    editor = create_editor()
    return marker_area.MarkerArea(editor)
