# -*- coding: utf-8 -*-


# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.


"""IDE Settings variables."""


###############################################################################
# IDE
###############################################################################


# UI LAYOUT
#    001 : Central Rotate
#    010 : Panels Rotate
#    100 : Central Orientation
UI_LAYOUT = 0


MAX_OPACITY = 1

TOOLBAR_AREA = 1

MIN_OPACITY = 0.3


NOTIFICATION_POSITION = 0

LANGUAGE, EXECUTION_OPTIONS = "", ""

SHOW_START_PAGE = True

CONFIRM_EXIT = True

HIDE_TOOLBAR = False

PYTHON_EXEC_CONFIGURED_BY_USER = False

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
