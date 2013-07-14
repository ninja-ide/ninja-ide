# -*- coding: utf-8 -*-

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
    "connect": "show_replace"
    },
    {
    "shortcut": "Find-with-word",
    "connect": "show_with_word"
    },
    {
    "shortcut": "Code-locator",
    "connect": "show_locator"
    },
    {
    "shortcut": "File-Opener",
    "connect": "show_file_opener"
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
)