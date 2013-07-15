# -*- coding: utf-8 -*-

from PyQt4.QtGui import QStyle

from ninja_ide.gui import translations

#{
#"shortcut": "Change-Tab",
#"action": ("text", "Image [string for ninja, Int for qt, None for nothing]"),
#"connect": "function_name"
#}

ACTIONS = (
    {
    "shortcut": "New-project",
    "action": {'text': translations.TR_NEW_PROJECT,
               'image': 'newProj',
               'section': translations.TR_MENU_FILE,
               'weight': 110},
    "connect": "create_new_project"
    },
    {
    "shortcut": "Open-project",
    "action": {'text': translations.TR_OPEN_PROJECT,
               'image': 'openProj',
               'section': translations.TR_MENU_FILE,
               'weight': 410},
    "connect": "open_project_folder"
    },
    {
    "shortcut": "Save-project",
    "action": {'text': translations.TR_SAVE_PROJECT,
               'image': 'saveAll',
               'section': translations.TR_MENU_FILE,
               'weight': 240},
    "connect": "save_project"
    },
    {
    "action": {'text': translations.TR_CLOSE_ALL_PROJECTS,
               'image': QStyle.SP_DialogCloseButton,
               'section': translations.TR_MENU_FILE,
               'weight': 920},
    "connect": "close_opened_projects"
    },
    {
    "action": {'text': translations.TR_OPEN_PROJECT_PROPERTIES,
               'section': translations.TR_MENU_PROJECT,
               'weight': 200},
    "connect": "open_project_properties"
    },
)