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
    "action": (translations.TR_DUPLICATE, None),
    "connect": "editor_duplicate"
    },
    {
    "shortcut": "Remove-line",
    "action": (translations.TR_REMOVE_LINE, None),
    "connect": "editor_remove_line"
    },
    {
    "shortcut": "Move-up",
    "action": (translations.TR_MOVE_UP, None),
    "connect": "editor_move_up"
    },
    {
    "shortcut": "Move-down",
    "action": (translations.TR_MOVE_UP, None),
    "connect": "editor_move_down"
    },
    {
    "shortcut": "Close-tab",
    "action": (translations.TR_CLOSE_TAB, QStyle.SP_DialogCloseButton),
    "connect": "close_tab"
    },
    {
    "shortcut": "New-file",
    "action": (translations.TR_NEW_FILE, None),
    "connect": "add_editor"
    },
    {
    "shortcut": "Open-file",
    "action": (translations.TR_OPEN, 'open'),
    "connect": "open_file"
    },
    {
    "shortcut": "Save-file",
    "action": (translations.TR_SAVE, 'save'),
    "connect": "save_file"
    },
    {
    "action": (translations.TR_SAVE_AS, 'saveAs'),
    "connect": "save_file_as"
    },
    {
    "action": (translations.TR_SAVE_ALL, 'saveAll'),
    "connect": "save_all"
    },
    {
    "shortcut": "Redo",
    "action": (translations.TR_REDO, 'redo'),
    "connect": "editor_redo"
    },
    {
    "shortcut": "Add-Bookmark-or-Breakpoint",
    "connect": "add_bookmark_breakpoint"
    },
    {
    "shortcut": "Comment",
    "action": (translations.TR_COMMENT, 'comment-code'),
    "connect": "editor_comment"
    },
    {
    "shortcut": "Uncomment",
    "action": (translations.TR_UNCOMMENT, 'uncomment-code'),
    "connect": "editor_uncomment"
    },
    {
    "shortcut": "Horizontal-line",
    "action": (translations.TR_HORIZONTAL_LINE, None),
    "connect": "editor_insert_horizontal_line"
    },
    {
    "shortcut": "Title-comment",
    "action": (translations.TR_TITLE_COMMENT, None),
    "connect": "editor_insert_title_comment"
    },
    {
    "shortcut": "Indent-less",
    "action": (translations.TR_INDENT_LESS, 'indent-less'),
    "connect": "editor_indent_less"
    },
    {
    "shortcut": "Split-horizontal",
    "action": (translations.TR_SPLIT_HORIZONTALLY, 'splitH'),
    "connect": "split_tabh"
    },
    {
    "shortcut": "Split-vertical",
    "action": (translations.TR_SPLIT_VERTICALLY, 'splitV'),
    "connect": "split_tabv"
    },
    {
    "shortcut": "Follow-mode",
    "action": (translations.TR_FOLLOW_MODE, 'follow'),
    "connect": "show_follow_mode"
    },
    {
    "shortcut": "Reload-file",
    "action": (translations.TR_RELOAD_FILE, 'reload-file'),
    "connect": "reload_file"
    },
    {
    "shortcut": "Import",
    "action": (translations.TR_INSERT_IMPORT, 'insert-import'),
    "connect": "import_from_everywhere"
    },
    {
    "shortcut": "Go-to-definition",
    "action": (translations.TR_GO_TO_DEFINITION, 'go-to-definition'),
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
    "action": (translations.TR_HELP, None),
    "connect": "show_python_doc"
    },
    {
    "shortcut": "Highlight-Word",
    "connect": "editor_highlight_word"
    },
    {
    "shortcut": "Print-file",
    "action": (translations.TR_PRINT_FILE, 'print'),
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