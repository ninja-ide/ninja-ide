# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QStyle

from ninja_ide import translations

#{
#"shortcut": "Change-Tab",
#"action": {'text': string,
               #'image': [string for ninja, Int for qt, None for nothing],
               #'section': string,
               #'weight': int},
#"connect": "function_name"
#}


#FIXME: add open recent projects
#FIXME: add organize import
#FIXME: add remove unused imports
#FIXME: add extract method

"""
Actions included here are those that are associated with the main
IDE window, in other words, these are all actions the signals of which
must ultimately connect to slots in main_container.py

The weight attribute is used to determine the order in which the actions
are added to the menus.  The first digit determines the menu section it
must be placed in and the subsequent digits its position in that section,
i.e. everything 1** will be in the same section (a section being an area in
the menu between separators) everything 2** in another section LOWER than
the section determined by 1** and so forth.
"""


ACTIONS = (
    # {
    #    "shortcut": "show-selector",
    #    "action": {
    #        "text": translations.TR_SHOW_SELECTOR,
    #        "image": "selector",
    #        "section": (translations.TR_MENU_FILE, None),
    #        "weight": 500
    #    },
    #    "connect": "show_selector"

    # },
    {
        "shortcut": "new-file",
        "action": {
            "text": translations.TR_NEW_FILE,
            "image": "new-file",
            "section": (translations.TR_MENU_FILE, None),
            "weight": 100
        },
        "connect": "add_editor"
    },
    {
        "action": {
            "text": translations.TR_RECENT_FILES,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 420,
            "is_menu": True
        }
    },
    {
        "shortcut": "close-file",
        "action": {
            "text": translations.TR_CLOSE_FILE,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 910
        },
        "connect": "close_file"
    },
    {
        "shortcut": "open-file",
        "action": {
            "text": translations.TR_OPEN,
            "image": "open-file",
            "section": (translations.TR_MENU_FILE, None),
            "weight": 400
        },
        "connect": "open_file"
    },
    {
        "shortcut": "save-file",
        "action": {
            "text": translations.TR_SAVE,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 150
        },
        "connect": "save_file"
    },
    {
        "shortcut": "locator",
        "action": {
            "text": translations.TR_CODE_LOCATOR,
            "section": (translations.TR_MENU_EDIT, None),
            "weight": 230
        },
        "connect": "show_locator"
    },
    {
        "action": {
            "text": translations.TR_SAVE_AS,
            "section": (translations.TR_MENU_FILE, None),
            "weight": 160
        },
        "connect": "save_file_as"
    },
    {
        "shortcut": "split-assistance",
        "action": {
            "text": translations.TR_SHOW_SPLIT_ASSISTANCE,
            "section": (translations.TR_MENU_VIEW, None),
            "weight": 430
        },
        "connect": "split_assistance"
    },
    {
        "shortcut": "zoom-in",
        "action": {
            "text": translations.TR_ZOOM_IN,
            "section": (translations.TR_MENU_VIEW, None),
            "weight": 400
        },
        "connect": "zoom_in_editor"
    },
    {
        "shortcut": "zoom-out",
        "action": {
            "text": translations.TR_ZOOM_OUT,
            "section": (translations.TR_MENU_VIEW, None),
            "weight": 410
        },
        "connect": "zoom_out_editor"
    },
    {
        "shortcut": "zoom-reset",
        "connect": "reset_zoom_editor"
    },
    {
        "action": {
            "text": translations.TR_TABS_SPACES_VISIBILITY,
            "section": (translations.TR_MENU_VIEW, None),
            "weight": 110
        },
        "connect": "toggle_tabs_and_spaces"
    },
    {
        "shortcut": "move-up",
        "action": {
            "text": translations.TR_MOVE_UP,
            "section": (translations.TR_MENU_SOURCE, None),
            "weight": 440
        },
        "connect": "editor_move_up"
    },
    {
        "shortcut": "move-down",
        "action": {
            "text": translations.TR_MOVE_DOWN,
            "section": (translations.TR_MENU_SOURCE, None),
            "weight": 450
        },
        "connect": "editor_move_down"
    },
    {
        "shortcut": "duplicate-line",
        "action": {
            "text": translations.TR_DUPLICATE,
            "section": (translations.TR_MENU_SOURCE, None),
            "weight": 470
        },
        "connect": "editor_duplicate_line"
    },
    {
        "shortcut": "comment",
        "action": {
            "text": translations.TR_COMMENT,
            "section": (translations.TR_MENU_SOURCE, None),
            "weight": 130
        },
        "connect": "editor_toggle_comment"
    },
    # {
    #     "shortcut": "uncomment",
    #     "action": {
    #         "text": translations.TR_UNCOMMENT,
    #         "section": (translations.TR_MENU_SOURCE, None),
    #         "weight": 140
    #     },
    #     "connect": "editor_uncomment"
    # },
    {
        "shortcut": "navigate-back",
        "connect": "navigate_back"
    },
    {
        "shortcut": "navigate-forward",
        "connect": "navigate_forward"
    },
    {
        "shortcut": "import",
        "action": {
            "text": translations.TR_INSERT_IMPORT,
            "section": (translations.TR_MENU_SOURCE, None),
            "weight": 310
        },
        "connect": "import_from_everywhere"
    }
)
"""
ACTIONS = (
    {
    "shortcut": "Show-Selector",
    "action": {'text': translations.TR_SHOW_SELECTOR,
               'image': 'selector',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 500},
    "connect": "show_selector"
    },
    {
    "shortcut": "Change-Tab",
    "connect": "change_tab"
    },
    {
    "shortcut": "expand-file-combo",
    "connect": "expand_file_combo"
    },
    {
    "shortcut": "expand-symbol-combo",
    "connect": "expand_symbol_combo"
    },
    {
    "shortcut": "Change-Tab-Reverse",
    "connect": "change_tab_reverse"
    },
    {
    "shortcut": "Duplicate",
    "action": {'text': translations.TR_DUPLICATE,
               'image': None,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 470},
    "connect": "editor_duplicate"
    },
    {
    "shortcut": "Remove-line",
    "action": {'text': translations.TR_REMOVE_LINE,
               'image': None,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 480},
    "connect": "editor_remove_line"
    },
    {
    "shortcut": "Move-up",
    "action": {'text': translations.TR_MOVE_UP,
               'image': None,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 440},
    "connect": "editor_move_up"
    },
    {
    "shortcut": "Move-down",
    "action": {'text': translations.TR_MOVE_DOWN,
               'image': None,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 450},
    "connect": "editor_move_down"
    },
    {
    "shortcut": "Close-file",
    "action": {'text': translations.TR_CLOSE_FILE,
               'image': QStyle.SP_DialogCloseButton,
               'section': (translations.TR_MENU_FILE, None),
               'weight': 910},
    "connect": "close_file"
    },
    {
    "shortcut": "New-file",
    "action": {'text': translations.TR_NEW_FILE,
               'image': 'new',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 100},
    "connect": "add_editor"
    },
    {
    "shortcut": "Open-file",
    "action": {'text': translations.TR_OPEN,
               'image': 'open',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 400},
    "connect": "open_file"
    },
    {
    "shortcut": "Save-file",
    "action": {'text': translations.TR_SAVE,
               'image': 'save',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 150},
    "connect": "save_file"
    },
    {
    "action": {'text': translations.TR_SAVE_AS,
               'image': 'saveAs',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 160},
    "connect": "save_file_as"
    },
    {
    "action": {'text': translations.TR_SAVE_ALL,
               'image': 'saveAll',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 170},
    "connect": "save_all"
    },
    {
    "action": {'text': translations.TR_UNDO,
               'image': 'undo',
               'section': (translations.TR_MENU_EDIT, None),
               'keysequence': 'undo',
               'weight': 100},
    "connect": "editor_undo"
    },
    {
    "shortcut": "Redo",
    "action": {'text': translations.TR_REDO,
               'image': 'redo',
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 110},
    "connect": "editor_redo"
    },
    {
    "shortcut": "Add-Bookmark-or-Breakpoint",
    "connect": "add_bookmark_breakpoint"
    },
    {
    "shortcut": "Comment",
    "action": {'text': translations.TR_COMMENT,
               'image': 'comment-code',
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 130},
    "connect": "editor_comment"
    },
    {
    "shortcut": "Uncomment",
    "action": {'text': translations.TR_UNCOMMENT,
               'image': 'uncomment-code',
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 140},
    "connect": "editor_uncomment"
    },
    {
    "shortcut": "Horizontal-line",
    "action": {'text': translations.TR_INSERT_HORIZONTAL_LINE,
               'image': None,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 150},
    "connect": "editor_insert_horizontal_line"
    },
    {
    "shortcut": "Title-comment",
    "action": {'text': translations.TR_INSERT_TITLE_COMMENT,
               'image': None,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 160},
    "connect": "editor_insert_title_comment"
    },
    {
    "action": {'text': translations.TR_COUNT_LINES,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 160},
    "connect": "count_file_code_lines"
    },
    {
    "action": {'text': translations.TR_INDENT_MORE,
               'image': 'indent-more',
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 100,
               'keysequence': 'Indent-more'},
    "connect": "editor_indent_more"
    },
    {
    "shortcut": "Indent-less",
    "action": {'text': translations.TR_INDENT_LESS,
               'image': 'indent-less',
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 110},
    "connect": "editor_indent_less"
    },
    {
    "shortcut": "Close-Split",
    "action": {'text': translations.TR_CLOSE_CURRENT_SPLIT,
               'image': None,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 460},
    "connect": "close_split"
    },
    {
    "shortcut": "Split-assistance",
    "action": {'text': translations.TR_SHOW_SPLIT_ASSISTANCE,
               'image': None,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 430},
    "connect": "split_assistance"
    },
    {
    "action": {'text': translations.TR_SPLIT_VERTICALLY,
               'image': 'splitV',
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 440},
    "connect": "split_vertically"
    },
    {
    "action": {'text': translations.TR_SPLIT_HORIZONTALLY,
               'image': 'splitH',
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 450},
    "connect": "split_horizontally"
    },
    {
    "shortcut": "Reload-file",
    "action": {'text': translations.TR_RELOAD_FILE,
               'image': 'reload-file',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 300},
    "connect": "reload_file"
    },
    {
    "shortcut": "Import",
    "action": {'text': translations.TR_INSERT_IMPORT,
               'image': 'insert-import',
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 310},
    "connect": "import_from_everywhere"
    },
    {
    "shortcut": "Go-to-definition",
    "action": {'text': translations.TR_GO_TO_DEFINITION,
               'image': 'go-to-definition',
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 300},
    "connect": "editor_go_to_definition"
    },
    {
    "shortcut": "Complete-Declarations",
    "connect": "editor_complete_declaration"
    },
    {
    "shortcut": "Navigate-back",
    "connect": "navigate_back"
    },
    {
    "shortcut": "Navigate-forward",
    "connect": "navigate_forward"
    },
    {
    "shortcut": "Open-recent-closed",
    "connect": "reopen_last_tab"
    },
    {
    "shortcut": "Show-Code-Nav",
    "connect": "show_navigation_buttons"
    },
    #{
    #"shortcut": "change-split-focus",
    #"connect": "change_split_focus"
    #},
    {
    "shortcut": "change-tab-visibility",
    "connect": "change_tabs_visibility"
    },
    {
    "shortcut": "Help",
    "action": {'text': translations.TR_HELP,
               'image': None,
               'section': (translations.TR_MENU_ABOUT, None),
               'weight': 110},
    "connect": "show_python_doc"
    },
    {
    # "shortcut": "Highlight-Word",
    "connect": "editor_highlight_word"
    },
    {
    "shortcut": "Print-file",
    "action": {'text': translations.TR_PRINT_FILE,
               'image': 'print',
               'section': (translations.TR_MENU_FILE, None),
               'weight': 900},
    "connect": "print_file"
    },
    {
    "shortcut": "History-Copy",
    "connect": "copy_history"
    },
    {
    "shortcut": "History-Paste",
    "connect": "paste_history"
    },
    {
    "action": {'text': translations.TR_SHOW_START_PAGE,
               'section': (translations.TR_MENU_ABOUT, None),
               'weight': 100},
    "connect": "show_start_page"
    },
    {
    "action": {'text': translations.TR_REPORT_BUGS,
               'section': (translations.TR_MENU_ABOUT, None),
               'weight': 200},
    "connect": "show_report_bugs"
    },
    {
    "action": {'text': translations.TR_PLUGINS_DOCUMENTATION,
               'section': (translations.TR_MENU_ABOUT, None),
               'weight': 210},
    "connect": "show_plugins_doc"
    },
    {
    "action": {'text': translations.TR_CUT,
               'section': (translations.TR_MENU_EDIT, None),
               'image': 'cut',
               'keysequence': 'cut',
               'weight': 120},
    "connect": "editor_cut"
    },
    {
    "action": {'text': translations.TR_COPY,
               'section': (translations.TR_MENU_EDIT, None),
               'image': 'copy',
               'keysequence': 'copy',
               'weight': 130},
    "connect": "editor_copy"
    },
    {
    "action": {'text': translations.TR_PASTE,
               'section': (translations.TR_MENU_EDIT, None),
               'image': 'paste',
               'keysequence': 'paste',
               'weight': 140},
    "connect": "editor_paste"
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
    {
    "action": {'text': translations.TR_PREVIEW_IN_BROWSER,
               'image': 'preview-web',
               'section': (translations.TR_MENU_PROJECT, None),
               'weight': 300},
    "connect": "preview_in_browser"
    },
    {
    "shortcut": "Hide-editor",
    "action": {'text': translations.TR_EDITOR_VISIBILITY,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 110},
    "connect": "change_visibility"
    },
    {
    "action": {'text': translations.TR_TABS_SPACES_VISIBILITY,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 110},
    "connect": "toggle_tabs_and_spaces"
    },
    {
    "shortcut": "Zoom-In",
    "action": {'text': translations.TR_ZOOM_IN,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 400},
    "connect": "zoom_in_editor"
    },
    {
    "shortcut": "Zoom-Out",
    "action": {'text': translations.TR_ZOOM_OUT,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 410},
    "connect": "zoom_out_editor"
    },
    {
        "shortcut": "zoom-reset",
        "connect": "reset_zoom"
    },
    {
    "action": {'text': translations.TR_DEBUGGING_TRICKS,
               'section': (translations.TR_MENU_SOURCE, None),
               'is_menu': True,
               'weight': 320},
    },
    {
    "action": {'text': translations.TR_PRINT_PER_LINE,
               'section': (translations.TR_MENU_SOURCE,
                           translations.TR_DEBUGGING_TRICKS),
               'weight': 320},
    "connect": "editor_insert_debugging_prints"
    },
    {
    "action": {'text': translations.TR_INSERT_PDB,
               'section': (translations.TR_MENU_SOURCE,
                           translations.TR_DEBUGGING_TRICKS),
               'weight': 320},
    "connect": "editor_insert_pdb"
    },
    {
    "action": {'text': translations.TR_REMOVE_TRAILING_SPACES,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 400},
    "connect": "editor_remove_trailing_spaces"
    },
    {
    "action": {'text': translations.TR_REPLACE_TABS_SPACES,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 410},
    "connect": "editor_replace_tabs_with_spaces"
    },
    {
    "shortcut": "Code-locator",
    "action": {'text': translations.TR_CODE_LOCATOR,
               'image': 'locator',
               'section': (translations.TR_MENU_EDIT, None),
               'weight': 230},
    "connect": "show_locator"
    }
)

"""
