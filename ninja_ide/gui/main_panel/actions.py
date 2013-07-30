# -*- coding: utf-8 -*-

from PyQt4.QtGui import QStyle

from ninja_ide.gui import translations

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

ACTIONS = (
    {
    "shortcut": "Change-Tab",
    "connect": "change_tab"
    },
    {
    "shortcut": "Move-Tab-to-right",
    "connect": "move_tab_right"
    },
    {
    "shortcut": "Move-Tab-to-left",
    "connect": "move_tab_left"
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
               'weight:': 470},
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
    "shortcut": "Close-tab",
    "action": {'text': translations.TR_CLOSE_TAB,
               'image': QStyle.SP_DialogCloseButton,
               'section': (translations.TR_MENU_FILE, None),
               'weight': 910},
    "connect": "close_tab"
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
    "action": {'text': translations.TR_HORIZONTAL_LINE,
               'image': None,
               'section': (translations.TR_MENU_SOURCE, None),
               'weight': 150},
    "connect": "editor_insert_horizontal_line"
    },
    {
    "shortcut": "Title-comment",
    "action": {'text': translations.TR_TITLE_COMMENT,
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
    "shortcut": "Split-horizontal",
    "action": {'text': translations.TR_SPLIT_HORIZONTALLY,
               'image': 'splitH',
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 200},
    "connect": "split_tabh"
    },
    {
    "shortcut": "Split-vertical",
    "action": {'text': translations.TR_SPLIT_VERTICALLY,
               'image': 'splitV',
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 210},
    "connect": "split_tabv"
    },
    {
    "shortcut": "Close-Split",
    "connect": "close_split"
    },
    {
    "shortcut": "Split-assistance",
    "connect": "split_assistance"
    },
    {
    "shortcut": "Follow-mode",
    "action": {'text': translations.TR_FOLLOW_MODE,
               'image': 'follow',
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 220},
    "connect": "show_follow_mode"
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
               'section': (translations.TR_MENU_ABOUT, None),
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
    "action": {'text': translations.TR_GROUP_TABS,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 300},
    "connect": "group_tabs_together"
    },
    {
    "action": {'text': translations.TR_DEACTIVATE_GROUP_TABS,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 310},
    "connect": "deactivate_tabs_groups"
    },
    {
    "action": {'text': translations.TR_ZOOM_IN,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 400},
    "connect": "zoom_in_editor"
    },
    {
    "action": {'text': translations.TR_ZOOM_OUT,
               'section': (translations.TR_MENU_VIEW, None),
               'weight': 410},
    "connect": "zoom_out_editor"
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
    },
    {
    "action": {'text': translations.TR_INSERT_PDB,
               'section': (translations.TR_MENU_SOURCE,
                           translations.TR_DEBUGGING_TRICKS),
               'weight': 320},
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
)