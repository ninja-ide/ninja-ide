from ninja_ide.gui.editor.side_area import marker_widget
from ninja_tests.gui.editor import create_editor


def get_marker_area():
    # editor = create_editor()
    return marker_widget.MarkerWidget()
