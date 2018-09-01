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

# {
#   "shortcut": "Change-Tab",
#   "action": {
#       "text",
#       "Image [string for ninja, Int for qt, None for nothing]"
#   },
#   "connect": "function_name"
# }

ACTIONS_CENTRAL = (
    {
        "shortcut": "hide-explorer",
        "action": {
            "text": translations.TR_EXPLORER_VISIBILITY,
            "section": (translations.TR_MENU_VIEW, None),
            "weight": 130
        },
        "connect": "change_lateral_visibility"
    },
)
# ACTIONS_CENTRAL = (
#    {
#    "shortcut": "Show-Paste-History",
#    "connect": "show_copypaste_history_popup"
#    },
#    {
#    "shortcut": "Hide-all",
#    "action": {'text': translations.TR_ALL_VISIBILITY,
#               'section': (translations.TR_MENU_VIEW, None),
#               'weight': 120},
#    "connect": "hide_all"
#    },
#    {
#    "shortcut": "Hide-explorer",
#    "action": {'text': translations.TR_EXPLORER_VISIBILITY,
#               'section': (translations.TR_MENU_VIEW, None),
#               'weight': 130},
#    "connect": "change_lateral_visibility"
#    },
# )


ACTIONS_STATUS = (
    {
        "shortcut": "find",
        "action": {
            "text": translations.TR_FIND,
            "section": (translations.TR_MENU_EDIT, None),
            "weight": 200
        },
        "connect": "show_search"
    },
    {
        "shortcut": "find-replace",
        "action": {
            "text": translations.TR_FIND_REPLACE,
            "section": (translations.TR_MENU_EDIT, None),
            "weight": 210
        },
        "connect": "show_replace"
    }
)
#    "shortcut": "Find-with-word",
#    "action": {'text': translations.TR_FIND_WORD_UNDER_CURSOR,
#               'section': (translations.TR_MENU_EDIT, None),
#               'weight': 220},
#    "connect": "show_with_word"
#    },
#    {
#       "shortcut": "Code-locator",
#       "action": {'text': translations.TR_CODE_LOCATOR,
#               'image': 'locator',
#               'section': (translations.TR_MENU_EDIT, None),
#               'weight': 230},
#     "connect": "show_locator"
#     },
#    {
#    "shortcut": "File-Opener",
#    "connect": "show_file_opener"
#    },
# )


ACTIONS_STATUS_SEARCH = (
    {
        "shortcut": "find-next",
        "connect": "find_next"
    },
    {
        "shortcut": "find-previous",
        "connect": "find_previous"
    }
)


ACTIONS_GENERAL = (
    {
        "action": {
            "text": translations.TR_MANAGE_PLUGINS,
            "section": (translations.TR_MENU_EXTENSIONS, None),
            "weight": 100
        },
        "connect": "show_plugins_store"
    },
    {
        "action": {
            "text": translations.TR_EDITOR_SCHEMES,
            "section": (translations.TR_MENU_EXTENSIONS, None),
            "weight": 110
        },
        "connect": "show_schemes"
    },
    {
        "action": {
            "text": translations.TR_LANGUAGE_MANAGER,
            "section": (translations.TR_MENU_EXTENSIONS, None),
            "weight": 120
        },
        "connect": "show_languages"
    },
    {
        "action": {
            "text": translations.TR_ABOUT_NINJA,
            "section": (translations.TR_MENU_ABOUT, None),
            "weight": 900
        },
        "connect": "show_about_ninja"
    },
    {
        "action": {
            "text": translations.TR_ABOUT_QT,
            "section": (translations.TR_MENU_ABOUT, None),
            "weight": 910
        },
        "connect": "show_about_qt"
    },
    {
        "action": {
            "text": translations.TR_PREFERENCES,
            "image": "preferences",
            "section": (translations.TR_MENU_EDIT, None),
            "weight": 900
        },
        "connect": "show_preferences"
    },
    {
        "action": {
            "text": translations.TR_ACTIVATE_PROFILE,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 510},
        "connect": "activate_profile"
    },
    {
        "action": {
            "text": translations.TR_DEACTIVATE_PROFILE,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 520
        },
        "connect": "deactivate_profile"
    },
    {
        "action": {
            "text": translations.TR_EXIT,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 990
        },
        "connect": "close"
    },
    {
        "action": {
            "text": translations.TR_TOOLBAR_VISIBILITY,
            "section": (translations.TR_MENU_VIEW, None),
            "weight": 140
        },
        "connect": "change_toolbar_visibility"
    },
    {
        "action": {
            "text": translations.TR_TOOLSDOCK_VISIBILITY,
            "section": (translations.TR_MENU_VIEW, None),
            "weight": 150
        },
        "connect": "change_toolsdock_visibility"
    },
    {
        "shortcut": "full-screen",
        "action": {
            "text": translations.TR_FULLSCREEN_VISIBILITY,
            "section": (translations.TR_MENU_VIEW, None),
            "weight": 160
        },
        "connect": "fullscreen_mode"
    },
)
