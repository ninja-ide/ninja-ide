# -*- coding: utf-8 -*-
#
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

from ninja_ide import translations


PROJECTS_TREE_ACTIONS = (
    {
        "shortcut": "openproject",
        "action": {
            "text": translations.TR_OPEN_PROJECT,
            "image": "open-project",
            "section": (translations.TR_MENU_FILE, None),
            "weight": 410
        },
        "connect": "open_project_folder"
    },
    {
        "shortcut": "save-project",
        "action": {
            "text": translations.TR_SAVE_PROJECT,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 190
        },
        "connect": "save_project"
    },
    {
        "shortcut": "new-project",
        "action": {
            "text": translations.TR_NEW_PROJECT,
            "image": "new-project",
            "section": (translations.TR_MENU_FILE, None),
            "weight": 110
        },
        "connect": "create_new_project"
    },
    {
        "action": {
            "text": translations.TR_CLOSE_ALL_PROJECTS,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 920
        },
        "connect": "close_opened_projects"
    },
    {
        "action": {
            "text": translations.TR_OPEN_PROJECT_PROPERTIES,
            "section": (translations.TR_MENU_PROJECT, None),
            "weight": 200
        },
        "connect": "open_project_properties"
    },
)
