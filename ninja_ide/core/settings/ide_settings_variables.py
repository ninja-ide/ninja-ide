# -*- coding: utf-8 -*-


"""IDE Settings variables."""


###############################################################################
# IDE
###############################################################################


# UI LAYOUT
#    001 : Central Rotate
#    010 : Panels Rotate
#    100 : Central Orientation
UI_LAYOUT = 0


MAX_OPACITY, TOOLBAR_AREA = 1, 1
MIN_OPACITY = 0.3


NOTIFICATION_POSITION = 0

LANGUAGE, EXECUTION_OPTIONS = "", ""

SHOW_START_PAGE, CONFIRM_EXIT = True, True

HIDE_TOOLBAR, PYTHON_EXEC_CONFIGURED_BY_USER = False, False

NOTIFICATION_COLOR = "#000"

PYTHON_EXEC = "python"

SESSIONS = {}


TOOLBAR_ITEMS = [
    "_MainContainer.show_selector",
    "_MainContainer.add_editor",
    # "ProjectTreeColumn.create_new_project",
    "_MainContainer.open_file",
    "ProjectTreeColumn.open_project_folder",
    "_MainContainer.save_file",
    "_MainContainer.split_vertically",
    "_MainContainer.split_horizontally",
    "IDE.activate_profile",
    "IDE.deactivate_profile",
    "_MainContainer.editor_cut",
    "_MainContainer.editor_copy",
    "_MainContainer.editor_paste",
    "_ToolsDock.execute_file",
    "_ToolsDock.execute_project",
    "_ToolsDock.kill_application",
]


TOOLBAR_ITEMS_DEFAULT = [
    "_MainContainer.show_selector",
    "_MainContainer.add_editor",
    # "ProjectTreeColumn.create_new_project",
    "_MainContainer.open_file",
    "ProjectTreeColumn.open_project_folder",
    "_MainContainer.save_file",
    "_MainContainer.split_vertically",
    "_MainContainer.split_horizontally",
    "IDE.activate_profile",
    "IDE.deactivate_profile",
    "_MainContainer.editor_cut",
    "_MainContainer.editor_copy",
    "_MainContainer.editor_paste",
    "_ToolsDock.execute_file",
    "_ToolsDock.execute_project",
    "_ToolsDock.kill_application",
]


# Hold the toolbar actions added by plugins.
TOOLBAR_ITEMS_PLUGINS = []

LAST_OPENED_FILES = []

NINJA_SKIN = 'Default'

LAST_OPENED_FILES = []

NOTIFICATION_POSITION = 0

LAST_CLEAN_LOCATOR = None
