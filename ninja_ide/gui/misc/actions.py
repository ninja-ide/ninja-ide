# -*- coding: utf-8 -*-

from ninja_ide.gui import translations

#{
#"shortcut": "Change-Tab",
#"action": ("text", "Image [string for ninja, Int for qt, None for nothing]"),
#"connect": "function_name"
#}

ACTIONS = (
    {
    "shortcut": "Find-in-files",
    "action": (translations.TR_FIND_IN_FILES, 'find'),
    "connect": "show_find_in_files_widget"
    },
    {
    "shortcut": "Run-file",
    "action": (translations.TR_RUN_FILE, 'file-run'),
    "connect": "execute_file"
    },
    {
    "shortcut": "Run-project",
    "action": (translations.TR_RUN_PROJECT, 'play'),
    "connect": "execute_project"
    },
    {
    "shortcut": "Stop-execution",
    "action": (translations.TR_STOP, 'stop'),
    "connect": "kill_application"
    },
)