# -*- coding: utf-8 -*-

from ninja_ide import translations

# "connect": "function_name"

ACTIONS = (
    #         "weight": 240
    #     "connect": "show_find_in_files_widget"
    {
        "shortcut": "run-file",
        "action": {
            "text": translations.TR_RUN_FILE,
            "image": "run-file",
            "section": (translations.TR_MENU_PROJECT, None),
            "weight": 110
        },
        "connect": "execute_file"
    },
    {
        "shortcut": "run-selection",
        "action": {
            "text": translations.TR_RUN_SELECTION,
            "section": (translations.TR_MENU_PROJECT, None),
            "weight": 110
        },
        "connect": "execute_selection"
    },
    {
        "shortcut": "run-project",
        "action": {
            "text": translations.TR_RUN_PROJECT,
            "image": "run-project",
            "section": (translations.TR_MENU_PROJECT, None),
            "weight": 100
        },
        "connect": "execute_project"
    },
    {
        "shortcut": "stop-execution",
        "action": {
            'text': translations.TR_STOP,
            'image': "stop",
            'section': (translations.TR_MENU_PROJECT, None),
            'weight': 120
        },
        "connect": "kill_application"
    },
    #         "weight": 100
    #     "connect": "change_visibility"
)
