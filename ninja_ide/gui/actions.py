# -*- coding: utf-8 -*-

from PyQt4.QtGui import QStyle

from ninja_ide import translations

#{
#"shortcut": "Change-Tab",
#"action": ("text", "Image [string for ninja, Int for qt, None for nothing]"),
#"connect": "function_name"
#}

ACTIONS_CENTRAL = (
    {
    "shortcut": "Show-Paste-History",
    "connect": "show_copypaste_history_popup"
    },
    {
    "shortcut": "Hide-all",
    "action": {'text': translations.TR_ALL_VISIBILITY,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 120},
    "connect": "hide_all"
    },
    {
    "shortcut": "Hide-explorer",
    "action": {'text': translations.TR_EXPLORER_VISIBILITY,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 130},
    "connect": "change_lateral_visibility"
    },
)


ACTIONS_STATUS = (
    {
    "shortcut": "Find",
    "action": {'text': translations.TR_FIND,
               'image': 'find',
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 200},
    "connect": "show_search"
    },
    {
    "shortcut": "Find-replace",
    "action": {'text': translations.TR_FIND_REPLACE,
               'image': 'findReplace',
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 210},
    "connect": "show_replace"
    },
    {
    "shortcut": "Find-with-word",
    "action": {'text': translations.TR_FIND_WITH_WORD,
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 220},
    "connect": "show_with_word"
    },
    {
    "shortcut": "Code-locator",
    "action": {'text': translations.TR_CODE_LOCATOR,
               'image': 'locator',
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 230},
    "connect": "show_locator"
    },
    {
    "shortcut": "File-Opener",
    "connect": "show_file_opener"
    },
    {
    "action": {'text': translations.TR_CONVERT_UPPER,
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 300},
    "connect": "editor_upper"
    },
    {
    "action": {'text': translations.TR_CONVERT_LOWER,
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 310},
    "connect": "editor_lower"
    },
    {
    "action": {'text': translations.TR_CONVERT_TITLE,
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 320},
    "connect": "editor_title"
    },
)


ACTIONS_STATUS_SEARCH = (
    {
    "shortcut": "Find-next",
    "connect": "find_next"
    },
    {
    "shortcut": "Find-previous",
    "connect": "find_previous"
    },
)


ACTIONS_GENERAL = (
    #TODO
    #{
    #"action": {'text': translations.TR_MANAGE_PLUGINS,
               #'section': (translations.TR_MENU_EXTENSIONS, None),
               #'weight': 100},
    #"connect": "show_manager"
    #},
    {
    "action": {'text': translations.TR_EDITOR_SCHEMES,
               'section': (translations.TR_MENU_EXTENSIONS, None),
               'weight': 110},
    "connect": "show_themes"
    },
    {
    "action": {'text': translations.TR_LANGUAGE_MANAGER,
               'section': (translations.TR_MENU_EXTENSIONS, None),
               'weight': 120},
    "connect": "show_languages"
    },

    {
    "action": {'text': translations.TR_ABOUT_NINJA,
               'section': (translations.TR_MENU_ABOUT, None),
               'weight': 900},
    "connect": "show_about_ninja"
    },
    {
    "action": {'text': translations.TR_ABOUT_QT,
               'section': (translations.TR_MENU_ABOUT, None),
               'weight': 910},
    "connect": "show_about_qt"
    },
    {
    "action": {'text': translations.TR_PREFERENCES,
               'image': 'pref',
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 900},
    "connect": "show_preferences"
    },
    {
    "action": {'text': translations.TR_ACTIVATE_PROFILE,
               'image': 'activate-profile',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 500},
    "connect": "activate_profile"
    },
    {
    "action": {'text': translations.TR_DEACTIVATE_PROFILE,
               'image': 'deactivate-profile',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 510},
    "connect": "deactivate_profile"
    },
    {
    "action": {'text': translations.TR_EXIT,
               'image': QStyle.SP_DialogCloseButton,
               'section': (translations.TR_MENU_FILE, None),
               'weight': 990},
    "connect": "close"
    },
    {
    "action": {'text': translations.TR_TOOLBAR_VISIBILITY,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 140},
    "connect": "change_toolbar_visibility"
    },
    {
    "shortcut": "Full-screen",
    "action": {'text': translations.TR_FULLSCREEN_VISIBILITY,
               'image': 'fullscreen',
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 150},
    "connect": "fullscreen_mode"
    },
    {
    "shortcut": "Switch-Focus",
    "connect": "switch_focus"
    },
)