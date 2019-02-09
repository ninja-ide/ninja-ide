# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import datetime
import enum

from PyQt5.QtGui import QFont
from PyQt5.QtGui import QImageReader
from PyQt5.QtCore import QMimeDatabase
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QDir
from PyQt5.QtCore import QFileInfo

from ninja_ide import resources
# from ninja_ide.dependencies import pycodestyle


###############################################################################
# OS DETECTOR
###############################################################################

# Use this flags instead of sys.platform spreaded in the source code
IS_WINDOWS = IS_MAC_OS = False


OS_KEY = "Ctrl"
# Font
FONT = QFont("Source Code Pro")
if sys.platform == "darwin":
    from PyQt5.QtGui import QKeySequence
    from PyQt5.QtCore import Qt

    FONT = QFont("Monaco")
    OS_KEY = QKeySequence(Qt.CTRL).toString(QKeySequence.NativeText)
    IS_MAC_OS = True
elif sys.platform == "win32":
    FONT = QFont("Courier")
    IS_WINDOWS = True

FONT.setStyleHint(QFont.TypeWriter)
FONT.setPointSize(12)

FONT_ANTIALIASING = True


def detect_python_path():
    if (IS_WINDOWS and PYTHON_EXEC_CONFIGURED_BY_USER) or not IS_WINDOWS:
        return []

    suggested = []
    dirs = []
    try:
        drives = [QDir.toNativeSeparators(d.absolutePath())
                  for d in QDir.drives()]

        for drive in drives:
            info = QFileInfo(drive)
            if info.isReadable():
                dirs += [os.path.join(drive, folder)
                         for folder in os.listdir(drive)]
        for folder in dirs:
            file_path = os.path.join(folder, "python.exe")
            if ("python" in folder.lower()) and os.path.exists(file_path):
                suggested.append(file_path)
    except:
        print("Detection couldnt be executed")
    finally:
        return suggested

###############################################################################
# IDE
###############################################################################


HDPI = False
CUSTOM_SCREEN_RESOLUTION = ""
# Swap File

AUTOSAVE = True
AUTOSAVE_DELAY = 1500
# 0: Disable
# 1: Enable
# 2: Alternative Dir
# SWAP_FILE = 1
# SWAP_FILE_INTERVAL = 15  # seconds

MAX_OPACITY = TOOLBAR_AREA = 1
# MIN_OPACITY = 0.3

# UI LAYOUT
# 001 : Central Rotate
# 010 : Panels Rotate
# 100 : Central Orientation
NOTIFICATION_ON_SAVE = True
# UI_LAYOUT = NOTIFICATION_POSITION = 0

LANGUAGE = EXECUTION_OPTIONS = ""

SHOW_START_PAGE = CONFIRM_EXIT = True

HIDE_TOOLBAR = PYTHON_EXEC_CONFIGURED_BY_USER = False


PYTHON_EXEC = sys.executable

SESSIONS = {}

TOOLBAR_ITEMS = [
    "_MainContainer.show_selector",
    "_MainContainer.add_editor",
    "ProjectTreeColumn.create_new_project",
    "_MainContainer.open_file",
    "ProjectTreeColumn.open_project_folder",
    "IDE.show_preferences",
    # "_MainContainer.save_file",
    # "_MainContainer.split_vertically",
    # "_MainContainer.split_horizontally",
    # "IDE.activate_profile",
    # "IDE.deactivate_profile",
    # "_MainContainer.editor_cut",
    # "_MainContainer.editor_copy",
    # "_MainContainer.editor_paste",
    # "_ToolsDock.execute_file",
    # "_ToolsDock.execute_project",
    # "_ToolsDock.kill_application",
]

ACTIONBAR_ITEMS = [
    "_ToolsDock.execute_file",
    "_ToolsDock.execute_project",
    "_ToolsDock.kill_application"
]

TOOLBAR_ITEMS_DEFAULT = [
    "_MainContainer.show_selector",
    "_MainContainer.add_editor",
    # "ProjectTreeColumn.create_new_project",
    "_MainContainer.open_file",
    "ProjectTreeColumn.open_project_folder",
    "_MainContainer.save_file",
    "_MainContainer.split_vertically",
    "_MainContainer.split_horizontally",
    "IDE.activate_profile",
    "IDE.deactivate_profile",
    "_MainContainer.editor_cut",
    "_MainContainer.editor_copy",
    "_MainContainer.editor_paste",
    "_ToolsDock.execute_file",
    "_ToolsDock.execute_project",
    "_ToolsDock.kill_application",
]

# hold the toolbar actions added by plugins
# TOOLBAR_ITEMS_PLUGINS = LAST_OPENED_FILES = []

NINJA_SKIN = 'Dark'
LAST_OPENED_FILES = []

NOTIFICATION_POSITION = 0
NOTIFICATION_COLOR = "#000"

LAST_CLEAN_LOCATOR = None


###############################################################################
# EDITOR
###############################################################################

EDITOR_SCHEME = "Ninja Dark"
# IntelliSense
AUTOCOMPLETE_BRACKETS = AUTOCOMPLETE_QUOTES = True
# by default Unix (\n) is used
USE_TABS = ALLOW_WORD_WRAP = USE_PLATFORM_END_OF_LINE = False

REMOVE_TRAILING_SPACES = True

SHOW_INDENTATION_GUIDES = SHOW_TABS_AND_SPACES = False

ADD_NEW_LINE_AT_EOF = HIDE_MOUSE_CURSOR = SCROLL_WHEEL_ZOMMING = True

# Current Line
HIGHLIGHT_CURRENT_LINE = True
# 0: Full background
# 1: Simple
HIGHLIGHT_CURRENT_LINE_MODE = 0

INDENT = 4

SHOW_MARGIN_LINE = True
MARGIN_LINE = 79
MARGIN_LINE_BACKGROUND = False  # The background after the column limit

BRACE_MATCHING = True
# BRACES = {'{': '}', '[': ']', '(': ')'}
# QUOTES = {'"': '"', "'": "'"}

# FONT_MAX_SIZE = 28
# FONT_MIN_SIZE = 6
MAX_REMEMBER_EDITORS = 50
# MAX_REMEMBER_TABS = 50
# COPY_HISTORY_BUFFER = 20

# IGNORE_PEP8_LIST = []
CHECK_STYLE = FIND_ERRORS = True
# FIND_ERRORS = ERRORS_HIGHLIGHT_LINE = CHECK_STYLE = CHECK_HIGHLIGHT_LINE = False
# CODE_COMPLETION = COMPLETE_DECLARATIONS = SHOW_MIGRATION_TIPS = True
# UNDERLINE_NOT_BACKGROUND = VALID_2TO3 = AND_AT_LAST_LINE = True
# Widgets on side area of editor
SHOW_LINE_NUMBERS = True
SHOW_TEXT_CHANGES = True
# SHOW_TEXT_CHANGE_AREA = True
# SHOW_LINT_AREA = True

SYNTAX = {}
EXTENSIONS = {}
# BREAKPOINTS = {}
# BOOKMARKS = {}

# 0: Always ask
# 1: Reload
# 2: Ignore
RELOAD_FILE = 0

###############################################################################
# CHECKERS
###############################################################################

# CHECK_FOR_DOCSTRINGS = True


###############################################################################
# MINIMAP
###############################################################################

# SHOW_MINIMAP = False
# MINIMAP_MAX_OPACITY = 0.8
# MINIMAP_MIN_OPACITY = 0.1
# SIZE_PROPORTION = 0.17


###############################################################################
# FILE MANAGER
###############################################################################

# File types supported by Ninja-IDE
FILE_TYPES = [
    ("Python files", (".py", ".pyw")),
    ("QML files", (".qml",)),
    ("HTML document", (".html", ".htm")),
    ("JavaScript program", (".js", ".jsm")),
    ("Ninja project", (".nja",))
]
# Mime types
image_mimetypes = [f.data().decode()
                   for f in QImageReader.supportedMimeTypes()][1:]

db = QMimeDatabase()
for mt in image_mimetypes:
    mimetype = db.mimeTypeForName(mt)
    suffixes = [".{}".format(s) for s in mimetype.suffixes()]
    FILE_TYPES.append((mimetype.comment(), suffixes))

LANGUAGE_MAP = {
    "py": "python",
    "pyw": "python",
    "js": "javascript",
    "html": "html",
    "md": "markdown",
    "yml": "yaml",
    "qml": "qml",
    "json": "json"
}

###############################################################################
# PROJECTS DATA
###############################################################################

# PROJECT_TYPES = {'Python': None}
# PROJECT_TYPES = {}

# LANGS = []


###############################################################################
# EXPLORER
###############################################################################

SHOW_PROJECT_EXPLORER = SHOW_SYMBOLS_LIST = True
SHOW_ERRORS_LIST = SHOW_MIGRATION_LIST = SHOW_WEB_INSPECTOR = True


###############################################################################
# WORKSPACE
###############################################################################

WORKSPACE = ""


###############################################################################
# FUNCTIONS
###############################################################################


def get_supported_extensions():
    return [item for _, sub in FILE_TYPES for item in sub]


def get_supported_extensions_filter():
    filters = []
    for title, extensions in FILE_TYPES:
        filters.append("%s (*%s)" % (title, " *".join(extensions)))
    if IS_WINDOWS:
        all_filter = "All Files (*.*)"
    else:
        all_filter = "All Files (*)"
    filters.append(all_filter)
    return ";;".join(sorted(filters))


# def set_project_type_handler(project_type, project_type_handler):
#     """
#     Set a project type handler for the given project_type
#     """
#     global PROJECT_TYPES
#     PROJECT_TYPES[project_type] = project_type_handler


# def get_project_type_handler(project_type):
#     """
#     Returns the handler for the given project_type
#     """
#     global PROJECT_TYPES
#     return PROJECT_TYPES.get(project_type)


# def get_all_project_types():
#     """
#     Returns the availables project types
#     """
#     global PROJECT_TYPES
#     return list(PROJECT_TYPES.keys())


# def add_toolbar_item_for_plugins(toolbar_action):
#     """
#     Add a toolbar action set from some plugin
#     """
#     global TOOLBAR_ITEMS_PLUGINS
#     TOOLBAR_ITEMS_PLUGINS.append(toolbar_action)


# def get_toolbar_item_for_plugins():
#     """
#     Returns the toolbar actions set by plugins
#     """
#     global TOOLBAR_ITEMS_PLUGINS
#     return TOOLBAR_ITEMS_PLUGINS


def use_platform_specific_eol():
    global USE_PLATFORM_END_OF_LINE
    return USE_PLATFORM_END_OF_LINE

###############################################################################
# Utility functions to update (patch at runtime) pep8mod.py
###############################################################################


# def pycodestylemod_refresh_checks():
#    """
#    Force to reload all checks in pep8mod.py
#    """
#    # pep8mod.refresh_checks()


# def pycodestylemod_add_ignore(ignore_code):
#    """
#    Patch pycodestyle.py to ignore a given check by code
#    EXAMPLE:
#        pycodestylemod_add_ignore('W191')
#        'W1919': 'indentation contains tabs'
#    """
#    if ignore_code not in pycodestylemod.DEFAULT_IGNORE:
#        default_ignore = pycodestylemod.DEFAULT_IGNORE.split(',')
#        default_ignore.append(ignore_code)
#        pycodestylemod.DEFAULT_IGNORE = ','.join(default_ignore)


# def pycodestylemod_remove_ignore(ignore_code):
#    """
#     Patch pycodestylemod.py to remove the ignore of a give check
#    EXAMPLE:
#        pycodestylemod_remove_ignore('W191')
#        'W1919': 'indentation contains tabs'
#    """
#    if ignore_code in pycodestylemod.DEFAULT_IGNORE:
#        default_ignore = pycodestylemod.DEFAULT_IGNORE.split(',')
#        default_ignore.remove(ignore_code)
#        pycodestylemod.DEFAULT_IGNORE = ','.join(default_ignore)


# def pycodestylemod_update_margin_line_length(new_margin_line):
#    """
#    Patch pycodestylemod.py to update the margin line length with a new value
#    """
#    pycodestylemod.MAX_LINE_LENGTH = new_margin_line

###############################################################################
# LOAD SETTINGS
###############################################################################


def should_clean_locator_knowledge():
    value = None
    if LAST_CLEAN_LOCATOR is not None:
        delta = datetime.date.today() - LAST_CLEAN_LOCATOR
        if delta.days >= 10:
            value = datetime.date.today()
    elif LAST_CLEAN_LOCATOR is None:
        value = datetime.date.today()
    return value


def clean_locator_db(qsettings):
    """Clean Locator Knowledge"""

    last_clean = should_clean_locator_knowledge()
    if last_clean is not None:
        file_path = os.path.join(resources.NINJA_KNOWLEDGE_PATH, 'locator.db')
        if os.path.isfile(file_path):
            os.remove(file_path)
        qsettings.setValue("ide/cleanLocator", last_clean)


def load_settings():
    qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
    data_qsettings = QSettings(resources.DATA_SETTINGS_PATH,
                               QSettings.IniFormat)
    # Globals
    # global TOOLBAR_AREA
    # global LANGUAGE
    # global SHOW_START_PAGE
    # global CONFIRM_EXIT
    # global UI_LAYOUT
    global PYTHON_EXEC
    global EXECUTION_OPTIONS
    # global SWAP_FILE
    # global SWAP_FILE_INTERVAL
    # global PYTHON_EXEC_CONFIGURED_BY_USER
    # global SESSIONS
    global NINJA_SKIN
    # global SUPPORTED_EXTENSIONS
    global WORKSPACE
    global INDENT
    global USE_PLATFORM_END_OF_LINE
    # global REMOVE_TRAILING_SPACES
    # global ADD_NEW_LINE_AT_EOF
    # global HIDE_MOUSE_CURSOR
    # global SCROLL_WHEEL_ZOMMING
    # global SHOW_TABS_AND_SPACES
    global USE_TABS
    global ALLOW_WORD_WRAP
    # global COMPLETE_DECLARATIONS
    # global UNDERLINE_NOT_BACKGROUND
    global FONT
    global FONT_ANTIALIASING
    global MARGIN_LINE
    global SHOW_MARGIN_LINE
    global MARGIN_LINE_BACKGROUND
    global SHOW_INDENTATION_GUIDES
    # global IGNORE_PEP8_LIST
    # global ERRORS_HIGHLIGHT_LINE
    global FIND_ERRORS
    global CHECK_STYLE
    # global CHECK_HIGHLIGHT_LINE
    # global SHOW_MIGRATION_TIPS
    # global CODE_COMPLETION
    # global END_AT_LAST_LINE
    # global SHOW_PROJECT_EXPLORER
    # global SHOW_SYMBOLS_LIST
    global SHOW_WEB_INSPECTOR
    global SHOW_ERRORS_LIST
    # global SHOW_MIGRATION_LIST
    # global BOOKMARKS
    # global CHECK_FOR_DOCSTRINGS
    # global BREAKPOINTS
    # global BRACES
    global HIDE_TOOLBAR
    global AUTOCOMPLETE_BRACKETS
    global AUTOCOMPLETE_QUOTES
    # global TOOLBAR_ITEMS
    # global SHOW_MINIMAP
    # global MINIMAP_MAX_OPACITY
    # global MINIMAP_MIN_OPACITY
    # global SIZE_PROPORTION
    # global SHOW_DOCMAP
    # global DOCMAP_SLIDER
    # global EDITOR_SCROLLBAR
    # global DOCMAP_WIDTH
    # global DOCMAP_CURRENT_LINE
    # global DOCMAP_SEARCH_LINES
    # global NOTIFICATION_POSITION
    global NOTIFICATION_ON_SAVE
    # global NOTIFICATION_COLOR
    global LAST_CLEAN_LOCATOR
    global SHOW_LINE_NUMBERS
    global SHOW_TEXT_CHANGES
    global RELOAD_FILE
    global CUSTOM_SCREEN_RESOLUTION
    global HDPI
    global HIGHLIGHT_CURRENT_LINE
    global HIGHLIGHT_CURRENT_LINE_MODE
    global BRACE_MATCHING
    global EDITOR_SCHEME
    # General
    HIDE_TOOLBAR = qsettings.value("window/hide_toolbar", False, type=bool)
    # TOOLBAR_AREA = qsettings.value('preferences/general/toolbarArea', 1,
    #                               type=int)
    # LANGUAGE = qsettings.value('preferences/interface/language', '',
    #                           type='QString')
    # SHOW_START_PAGE = qsettings.value(
    #    'preferences/general/showStartPage', True, type=bool)
    # CONFIRM_EXIT = qsettings.value('preferences/general/confirmExit',
    #                               True, type=bool)
    # UI_LAYOUT = qsettings.value('preferences/interface/uiLayout', 0, type=int)
    PYTHON_EXEC = qsettings.value('execution/pythonExec',
                                  sys.executable, type=str)
    # PYTHON_EXEC_CONFIGURED_BY_USER = qsettings.value(
    #    'preferences/execution/pythonExecConfigured', False, type=bool)
    # SWAP_FILE = qsettings.value("ide/swapFile", 1, type=int)
    # SWAP_FILE_INTERVAL = qsettings.value("ide/swapFileInterval", 15, type=int)

    NINJA_SKIN = qsettings.value("ide/interface/skin", "Dark", type=str)
    # sessionDict = dict(data_qsettings.value('ide/sessions', {}))
    RELOAD_FILE = qsettings.value("ide/reloadSetting", 0, type=int)
    CUSTOM_SCREEN_RESOLUTION = qsettings.value(
        "ide/interface/customScreenResolution", "", type=str)
    HDPI = qsettings.value("ide/interface/autoHdpi", False, type=bool)
    # Fix later
    # try:
    # for key in sessionDict:
    #    session_list = sessionDict[key]
    #    files = []
    #    if session_list:
    #        files = [item for item in session_list[0]]
    #    temp_files = []
    #    for file_ in files:
    #        file_data = file_
    #        if len(file_data) > 0:
    #            temp_files.append((file_data[0], file_data[1], file_data[2]))
    #    files = temp_files
    #    projects = []
    #    if len(session_list) > 1:
    #        projects = [item for item in session_list[1]]
    #    SESSIONS[key] = (files, projects)
    # TODO
    # toolbar_items = [item for item in list(qsettings.value(
        # 'preferences/interface/toolbar', []))]
    # if toolbar_items:
        # TOOLBAR_ITEMS = toolbar_items
    # EXECUTION OPTIONS
    EXECUTION_OPTIONS = qsettings.value(
        'execution/executionOptions', defaultValue='', type=str)
    # extensions = [item for item in tuple(qsettings.value(
    #    'preferences/general/supportedExtensions', []))]
    # if extensions:
    #    SUPPORTED_EXTENSIONS = extensions
    WORKSPACE = qsettings.value("ide/workspace", "", type=str)
    # Editor
    # SHOW_MINIMAP = qsettings.value(
    #    'preferences/editor/minimapShow', False, type=bool)
    # MINIMAP_MAX_OPACITY = float(qsettings.value(
    #    'preferences/editor/minimapMaxOpacity', 0.8, type=float))
    # MINIMAP_MIN_OPACITY = float(qsettings.value(
    #    'preferences/editor/minimapMinOpacity', 0.1, type=float))
    # SIZE_PROPORTION = float(qsettings.value(
    #    'preferences/editor/minimapSizeProportion', 0.17, type=float))
    # SHOW_DOCMAP = qsettings.value(
    #    'preferences/editor/docmapShow', True, type=bool)
    # DOCMAP_SLIDER = qsettings.value(
    #    'preferences/editor/docmapSlider', False, type=bool)
    # EDITOR_SCROLLBAR = qsettings.value(
    #    'preferences/editor/editorScrollBar', True, type=bool)
    # DOCMAP_WIDTH = int(qsettings.value(
    #    'preferences/editor/docmapWidth', 15, type=int))
    HIGHLIGHT_CURRENT_LINE = qsettings.value(
        'editor/display/highlightCurrentLine', True, type=bool)
    HIGHLIGHT_CURRENT_LINE_MODE = qsettings.value(
        "editor/display/current_line_mode", 0, type=int)
    BRACE_MATCHING = qsettings.value(
        "editor/display/brace_matching", True, type=bool)
    # DOCMAP_SEARCH_LINES = qsettings.value(
    #    'preferences/editor/docmapSearchLines', True, type=bool)
    INDENT = int(qsettings.value(
        'editor/behavior/indentation_width', 4, type=int))

    USE_PLATFORM_END_OF_LINE = qsettings.value(
        'editor/general/platformEndOfLine', False, type=bool)
    SHOW_MARGIN_LINE = qsettings.value(
        'editor/display/margin_line', True, type=bool)
    MARGIN_LINE = qsettings.value('editor/display/margin_line_position', 79,
                                  type=int)
    MARGIN_LINE_BACKGROUND = qsettings.value(
        "editor/display/margin_line_background", False, type=bool)
    # FIXME:
    # pycodestylemod_update_margin_line_length(MARGIN_LINE)
    SHOW_LINE_NUMBERS = qsettings.value(
        'editor/display/show_line_numbers', True, type=bool)
    SHOW_TEXT_CHANGES = qsettings.value(
        "editor/display/show_text_changes", True, type=bool)
    EDITOR_SCHEME = qsettings.value(
        "editor/general/scheme", "Ninja Dark", type=str)
    # REMOVE_TRAILING_SPACES = qsettings.value(
    #    'preferences/editor/removeTrailingSpaces', True, type=bool)
    # ADD_NEW_LINE_AT_EOF = qsettings.value(
    #    "preferences/editor/addNewLineAtEnd", True, type=bool)
    # SHOW_TABS_AND_SPACES = qsettings.value(
    #    'preferences/editor/show_whitespaces', False, type=bool)
    USE_TABS = qsettings.value('editor/behavior/use_tabs', False, type=bool)
    # HIDE_MOUSE_CURSOR = qsettings.value(
    #    "preferences/editor/hideMouseCursor", True, type=bool)
    # SCROLL_WHEEL_ZOMMING = qsettings.value(
    #    "preferences/editor/scrollWheelZomming", True, type=bool)
    # FIXME:
    # if USE_TABS:
    #    pycodestylemod_add_ignore("W191")
    #    pycodestylemod_refresh_checks()
    ALLOW_WORD_WRAP = qsettings.value(
        'editor/display/allow_word_wrap', False, type=bool)
    # COMPLETE_DECLARATIONS = qsettings.value(
    #    'preferences/editor/completeDeclarations', True, type=bool)
    # UNDERLINE_NOT_BACKGROUND = qsettings.value(
    #    'preferences/editor/errorsUnderlineBackground', True, type=bool)
    font = qsettings.value('editor/general/default_font', None)
    if font:
        FONT = font
    FONT_ANTIALIASING = qsettings.value("editor/general/font_antialiasing",
                                        True, type=bool)
    SHOW_INDENTATION_GUIDES = qsettings.value(
        "editor/display/show_indentation_guides", False, type=bool)
    # IGNORE_PEP8_LIST = list(qsettings.value(
    #    'preferences/editor/defaultIgnorePep8', [], type='QStringList'))
    # FIXME:
    # for ignore_code in IGNORE_PEP8_LIST:
    #    pycodestylemod_add_ignore(ignore_code)
    FIND_ERRORS = qsettings.value(
        "editor/display/check_errors", True, type=bool)
    # SHOW_MIGRATION_TIPS = qsettings.value(
    #    'preferences/editor/showMigrationTips', True, type=bool)
    # ERRORS_HIGHLIGHT_LINE = qsettings.value(
    #    'preferences/editor/errorsInLine', True, type=bool)
    CHECK_STYLE = qsettings.value('editor/display/check_style',
                                  True, type=bool)
    AUTOCOMPLETE_BRACKETS = qsettings.value(
        "editor/intellisense/autocomplete_brackets", True, type=bool)
    AUTOCOMPLETE_QUOTES = qsettings.value(
        "editor/intellisense/autocomplete_quotes", True, type=bool)
    # CHECK_HIGHLIGHT_LINE = qsettings.value(
    #    'preferences/editor/checkStyleInline', True, type=bool)
    # CODE_COMPLETION = qsettings.value(
    #    'preferences/editor/codeCompletion', True, type=bool)
    # END_AT_LAST_LINE = qsettings.value(
    #    'preferences/editor/endAtLastLine', True, type=bool)
    # parentheses = qsettings.value('preferences/editor/parentheses', True,
    #                              type=bool)
    # if not parentheses:
    #    del BRACES['(']
    # brackets = qsettings.value('preferences/editor/brackets', True, type=bool)
    # if not brackets:
    #    del BRACES['[']
    # keys = qsettings.value('preferences/editor/keys', True, type=bool)
    # if not keys:
    #    del BRACES['{']
    # simpleQuotes = qsettings.value('preferences/editor/simpleQuotes',
    #                               True, type=bool)
    # if not simpleQuotes:
    #    del QUOTES["'"]
    # doubleQuotes = qsettings.value('preferences/editor/doubleQuotes',
    #                               True, type=bool)
    # if not doubleQuotes:
    #    del QUOTES['"']
    # Projects
    # SHOW_PROJECT_EXPLORER = qsettings.value(
    #    'preferences/interface/showProjectExplorer', True, type=bool)
    # SHOW_SYMBOLS_LIST = qsettings.value(
    #    'preferences/interface/showSymbolsList', True, type=bool)
    SHOW_WEB_INSPECTOR = qsettings.value(
        "interface/showWebInspector", False, type=bool)
    SHOW_ERRORS_LIST = qsettings.value(
        "interface/showErrorsList", True, type=bool)
    # SHOW_MIGRATION_LIST = qsettings.value(
    #    'preferences/interface/showMigrationList', True, type=bool)
    # Bookmarks and Breakpoints
    # bookmarks = dict(qsettings.value('preferences/editor/bookmarks', {}))
    # for key in bookmarks:
    #    if key:
    #        BOOKMARKS[key] = [int(i) for i in tuple(bookmarks[key])]
    # breakpoints = dict(qsettings.value('preferences/editor/breakpoints', {}))
    # for key in breakpoints:
    #    if key:
    #         BREAKPOINTS[key] = [int(i) for i in tuple(breakpoints[key])]
    NOTIFICATION_ON_SAVE = qsettings.value(
        "editor/general/notificate_on_save", True, type=bool)
    # Checkers
    # CHECK_FOR_DOCSTRINGS = qsettings.value(
    #    'preferences/editor/checkForDocstrings', False, type=bool)
    # NOTIFICATION_POSITION = qsettings.value(
    #    'interface/notification_position', 1, type=int)
    # NOTIFICATION_COLOR = qsettings.value(
    #    'preferences/general/notification_color', "#222", type='QString')
    LAST_CLEAN_LOCATOR = qsettings.value("ide/cleanLocator", None)
    from ninja_ide.extensions import handlers
    handlers.init_basic_handlers()
    clean_locator_db(qsettings)
