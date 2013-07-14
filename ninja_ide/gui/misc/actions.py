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
    "action": {'text': translations.TR_FIND_IN_FILES,
               'image': 'find',
               'section': 'Edit',
               'weight': 240},
    "connect": "show_find_in_files_widget"
    },
    {
    "shortcut": "Run-file",
    "action": {'text': translations.TR_RUN_FILE,
               'image': 'file-run',
               'section': 'Project',
               'weight': 110},
    "connect": "execute_file"
    },
    {
    "shortcut": "Run-project",
    "action": {'text': translations.TR_RUN_PROJECT,
               'image': 'play',
               'section': 'Project',
               'weight': 100},
    "connect": "execute_project"
    },
    {
    "shortcut": "Stop-execution",
    "action": {'text': translations.TR_STOP,
               'image': 'stop',
               'section': 'Project',
               'weight': 120},
    "connect": "kill_application"
    },
)