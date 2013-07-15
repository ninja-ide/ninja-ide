# -*- coding: utf-8 -*-

from PyQt4.QtGui import QStyle

from ninja_ide.gui import translations

#{
#"shortcut": "Change-Tab",
#"action": ("text", "Image [string for ninja, Int for qt, None for nothing]"),
#"connect": "function_name"
#}

ACTIONS_CENTRAL = (
    {
    "shortcut": "Hide-misc",
    "connect": "view_region1_visibility"
    },
    {
    "shortcut": "Hide-editor",
    "connect": "view_region0_visibility"
    },
    {
    "shortcut": "Hide-explorer",
    "connect": "view_region2_visibility"
    },
    {
    "shortcut": "Hide-all",
    "connect": "hide_all"
    },
    {
    "shortcut": "Show-Paste-History",
    "connect": "show_copypaste_history_popup"
    },
)


ACTIONS_STATUS = (
    {
    "shortcut": "Find",
    "action": {'text': translations.TR_FIND,
               'image': 'find',
               'section': translations.TR_MENU_EDIT,
               'weight': 200},
    "connect": "show"
    },
    {
    "shortcut": "Find-next",
    "connect": "find_next_result"
    },
    {
    "shortcut": "Find-previous",
    "connect": "find_previous_result"
    },
    {
    "shortcut": "Find-replace",
    "action": {'text': translations.TR_FIND_REPLACE,
               'image': 'findReplace',
               'section': translations.TR_MENU_EDIT,
               'weight': 210},
    "connect": "show_replace"
    },
    {
    "shortcut": "Find-with-word",
    "action": {'text': translations.TR_FIND_WITH_WORD,
               'section': translations.TR_MENU_EDIT,
               'weight': 220},
    "connect": "show_with_word"
    },
    {
    "shortcut": "Code-locator",
    "action": {'text': translations.TR_CODE_LOCATOR,
               'image': 'locator',
               'section': translations.TR_MENU_EDIT,
               'weight': 230},
    "connect": "show_locator"
    },
    {
    "shortcut": "File-Opener",
    "connect": "show_file_opener"
    },
    {
    "action": {'text': translations.TR_CONVERT_UPPER,
               'section': translations.TR_MENU_EDIT,
               'weight': 300},
    "connect": "editor_upper"
    },
    {
    "action": {'text': translations.TR_CONVERT_LOWER,
               'section': translations.TR_MENU_EDIT,
               'weight': 310},
    "connect": "editor_lower"
    },
    {
    "action": {'text': translations.TR_CONVERT_TITLE,
               'section': translations.TR_MENU_EDIT,
               'weight': 320},
    "connect": "editor_title"
    },
)


ACTIONS_GENERAL = (
    {
    "action": {'text': translations.TR_MANAGE_PLUGINS,
               'section': translations.TR_MENU_ADDINS,
               'weight': 100},
    "connect": "show_manager"
    },
    {
    "action": {'text': translations.TR_EDITOR_SCHEMES,
               'section': translations.TR_MENU_ADDINS,
               'weight': 110},
    "connect": "show_themes"
    },
    {
    "action": {'text': translations.TR_LANGUAGE_MANAGER,
               'section': translations.TR_MENU_ADDINS,
               'weight': 120},
    "connect": "show_languages"
    },

    {
    "action": {'text': translations.TR_ABOUT_NINJA,
               'section': translations.TR_MENU_ABOUT,
               'weight': 900},
    "connect": "show_about_ninja"
    },
    {
    "action": {'text': translations.TR_ABOUT_QT,
               'section': translations.TR_MENU_ABOUT,
               'weight': 910},
    "connect": "show_about_qt"
    },
    {
    "action": {'text': translations.TR_PREFERENCES,
               'image': 'pref',
               'section': translations.TR_MENU_EDIT,
               'weight': 900},
    "connect": "show_preferences"
    },
    {
    "action": {'text': translations.TR_ACTIVATE_PROFILE,
               'image': 'activate-profile',
               'section': translations.TR_MENU_FILE,
               'weight': 500},
    "connect": "activate_profile"
    },
    {
    "action": {'text': translations.TR_DEACTIVATE_PROFILE,
               'image': 'deactivate-profile',
               'section': translations.TR_MENU_FILE,
               'weight': 510},
    "connect": "deactivate_profile"
    },
    {
    "action": {'text': translations.TR_EXIT,
               'image': QStyle.SP_DialogCloseButton,
               'section': translations.TR_MENU_FILE,
               'weight': 990},
    "connect": "close"
    },
)