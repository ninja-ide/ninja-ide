from ninja_ide.gui.editor.side_area import marker_widget
# Need COLOR_SCHEME
from ninja_ide import resources
from ninja_ide.tools import json_manager
all_schemes = json_manager.load_editor_schemes()
resources.COLOR_SCHEME = all_schemes["Ninja Dark"]


def get_marker_area():
    # editor = create_editor()
    return marker_widget.MarkerWidget()
