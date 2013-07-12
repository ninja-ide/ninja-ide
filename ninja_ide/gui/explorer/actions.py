# -*- coding: utf-8 -*-

from ninja_ide.gui import translations

#{
#"shortcut": "Change-Tab",
#"action": ("text", "Image [string for ninja, Int for qt, None for nothing]"),
#"connect": "function_name"
#}

ACTIONS = (
    {
    "shortcut": "New-project",
    "action": (translations.TR_NEW_PROJECT, 'newProj'),
    "connect": "create_new_project"
    },
    {
    "shortcut": "Open-project",
    "action": (translations.TR_OPEN_PROJECT, 'openProj'),
    "connect": "open_project_folder"
    },
    {
    "shortcut": "Save-project",
    "action": (translations.TR_SAVE_PROJECT, 'saveAll'),
    "connect": "save_project"
    },
)