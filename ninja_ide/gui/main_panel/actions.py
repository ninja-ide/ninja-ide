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
    "shortcut": "Change-Tab",
    "connect": "change_tab"
    },
    {
    "shortcut": "Change-Tab-Reverse",
    "connect": "change_tab_reverse"
    },
    {
    "shortcut": "Duplicate",
    "action": {'text': translations.TR_DUPLICATE,
               'image': None,
               'section': 'Source',
               'weight:': 470},
    "connect": "editor_duplicate"
    },
    {
    "shortcut": "Remove-line",
    "action": {'text': translations.TR_REMOVE_LINE,
               'image': None,
               'section': 'Source',
               'weight': 480},
    "connect": "editor_remove_line"
    },
    {
    "shortcut": "Move-up",
    "action": {'text': translations.TR_MOVE_UP,
               'image': None,
               'section': 'Source',
               'weight': 440},
    "connect": "editor_move_up"
    },
    {
    "shortcut": "Move-down",
    "action": {'text': translations.TR_MOVE_DOWN,
               'image': None,
               'section': 'Source',
               'weight': 450},
    "connect": "editor_move_down"
    },
    {
    "shortcut": "Close-tab",
    "action": {'text': translations.TR_CLOSE_TAB,
               'image': QStyle.SP_DialogCloseButton,
               'section': 'File',
               'weight': 910},
    "connect": "close_tab"
    },
    {
    "shortcut": "New-file",
    "action": {'text': translations.TR_NEW_FILE,
               'image': 'new',
               'section': 'File',
               'weight': 100},
    "connect": "add_editor"
    },
    {
    "shortcut": "Open-file",
    "action": {'text': translations.TR_OPEN,
               'image': 'open',
               'section': 'File',
               'weight': 410},
    "connect": "open_file"
    },
    {
    "shortcut": "Save-file",
    "action": {'text': translations.TR_SAVE,
               'image': 'save',
               'section': 'File',
               'weight': 150},
    "connect": "save_file"
    },
    {
    "action": {'text': translations.TR_SAVE_AS,
               'image': 'saveAs',
               'section': 'Source',
               'weight': 160},
    "connect": "save_file_as"
    },
    {
    "action": {'text': translations.TR_SAVE_ALL,
               'image': 'saveAll',
               'section': 'Source',
               'weight': 170},
    "connect": "save_all"
    },
    {
    "action": {'text': translations.TR_UNDO,
               'image': 'undo',
               'section': 'Edit',
               'weight': 100},
    "connect": "editor_undo"
    },
    {
    "shortcut": "Redo",
    "action": {'text': translations.TR_REDO,
               'image': 'redo',
               'section': 'Edit',
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
               'section': 'Source',
               'weight': 130},
    "connect": "editor_comment"
    },
    {
    "shortcut": "Uncomment",
    "action": {'text': translations.TR_UNCOMMENT,
               'image': 'uncomment-code',
               'section': 'Source',
               'weight': 140},
    "connect": "editor_uncomment"
    },
    {
    "shortcut": "Horizontal-line",
    "action": {'text': translations.TR_HORIZONTAL_LINE,
               'image': None,
               'section': 'Source',
               'weight': 150},
    "connect": "editor_insert_horizontal_line"
    },
    {
    "shortcut": "Title-comment",
    "action": {'text': translations.TR_TITLE_COMMENT,
               'image': None,
               'section': 'Source',
               'weight': 160},
    "connect": "editor_insert_title_comment"
    },
    {
    "action": {'text': translations.TR_INDENT_MORE,
               'image': 'indent-more',
               'section': 'Source',
               'weight': 100},
    "connect": "editor_indent_more"
    },
    {
    "shortcut": "Indent-less",
    "action": {'text': translations.TR_INDENT_LESS,
               'image': 'indent-less',
               'section': 'Source',
               'weight': 110},
    "connect": "editor_indent_less"
    },
    {
    "shortcut": "Split-horizontal",
    "action": {'text': translations.TR_SPLIT_HORIZONTALLY,
               'image': 'splitH',
               'section': 'View',
               'weight': 200},
    "connect": "split_tabh"
    },
    {
    "shortcut": "Split-vertical",
    "action": {'text': translations.TR_SPLIT_VERTICALLY,
               'image': 'splitV',
               'section': 'View',
               'weight': 210},
    "connect": "split_tabv"
    },
    {
    "shortcut": "Follow-mode",
    "action": {'text': translations.TR_FOLLOW_MODE,
               'image': 'follow',
               'section': 'View',
               'weight': 220},
    "connect": "show_follow_mode"
    },
    {
    "shortcut": "Reload-file",
    "action": {'text': translations.TR_RELOAD_FILE,
               'image': 'reload-file',
               'section': 'File',
               'weight': 300},
    "connect": "reload_file"
    },
    {
    "shortcut": "Import",
    "action": {'text': translations.TR_INSERT_IMPORT,
               'image': 'insert-import',
               'section': 'Source',
               'weight': 310},
    "connect": "import_from_everywhere"
    },
    {
    "shortcut": "Go-to-definition",
    "action": {'text': translations.TR_GO_TO_DEFINITION,
               'image': 'go-to-definition',
               'section': 'Source',
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
    {
    "shortcut": "change-split-focus",
    "connect": "change_split_focus"
    },
    {
    "shortcut": "move-tab-to-next-split",
    "connect": "move_tab_to_next_split"
    },
    {
    "shortcut": "change-tab-visibility",
    "connect": "change_tabs_visibility"
    },
    {
    "shortcut": "Help",
    "action": {'text': translations.TR_HELP,
               'image': None,
               'section': 'About',
               'weight': 110},
    "connect": "show_python_doc"
    },
    {
    "shortcut": "Highlight-Word",
    "connect": "editor_highlight_word"
    },
    {
    "shortcut": "Print-file",
    "action": {'text': translations.TR_PRINT_FILE,
               'image': 'print',
               'section': 'File',
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
)