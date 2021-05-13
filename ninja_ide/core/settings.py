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
    except BaseException:
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

MAX_OPACITY = TOOLBAR_AREA = 1

# UI LAYOUT
# 001 : Central Rotate
# 010 : Panels Rotate
# 100 : Central Orientation
NOTIFICATION_ON_SAVE = True

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

MAX_REMEMBER_EDITORS = 50

CHECK_STYLE = FIND_ERRORS = True
# Widgets on side area of editor
SHOW_LINE_NUMBERS = True
SHOW_TEXT_CHANGES = True

SYNTAX = {}
EXTENSIONS = {}

# 0: Always ask
# 1: Reload
# 2: Ignore
RELOAD_FILE = 0

###############################################################################
# CHECKERS
###############################################################################

###############################################################################
# MINIMAP
###############################################################################

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


#     """
#     Set a project type handler for the given project_type
#     """
#     global PROJECT_TYPES


#     """
#     Returns the handler for the given project_type
#     """
#     global PROJECT_TYPES


#     """
#     Returns the availables project types
#     """
#     global PROJECT_TYPES


#     """
#     Add a toolbar action set from some plugin
#     """
#     global TOOLBAR_ITEMS_PLUGINS


#     """
#     Returns the toolbar actions set by plugins
#     """
#     global TOOLBAR_ITEMS_PLUGINS


def use_platform_specific_eol():
    global USE_PLATFORM_END_OF_LINE
    return USE_PLATFORM_END_OF_LINE

###############################################################################
# Utility functions to update (patch at runtime) pep8mod.py
###############################################################################


#    """
#    Force to reload all checks in pep8mod.py
#    """


#    """
#    Patch pycodestyle.py to ignore a given check by code
#    EXAMPLE:
#        'W1919': 'indentation contains tabs'
#    """


#    """
#     Patch pycodestylemod.py to remove the ignore of a give check
#    EXAMPLE:
#        'W1919': 'indentation contains tabs'
#    """


#    """
#    Patch pycodestylemod.py to update the margin line length with a new value
#    """

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
    #    'preferences/general/showStartPage', True, type=bool)
    # CONFIRM_EXIT = qsettings.value('preferences/general/confirmExit',
    #                               True, type=bool)
    PYTHON_EXEC = qsettings.value('execution/pythonExec',
                                  sys.executable, type=str)
    #    'preferences/execution/pythonExecConfigured', False, type=bool)

    NINJA_SKIN = qsettings.value("ide/interface/skin", "Dark", type=str)
    RELOAD_FILE = qsettings.value("ide/reloadSetting", 0, type=int)
    CUSTOM_SCREEN_RESOLUTION = qsettings.value(
        "ide/interface/customScreenResolution", "", type=str)
    HDPI = qsettings.value("ide/interface/autoHdpi", False, type=bool)
    # Fix later
    # TODO
    # 'preferences/interface/toolbar', []))]
    # EXECUTION OPTIONS
    EXECUTION_OPTIONS = qsettings.value(
        'execution/executionOptions', defaultValue='', type=str)
    #    'preferences/general/supportedExtensions', []))]
    WORKSPACE = qsettings.value("ide/workspace", "", type=str)
    # Editor
    #    'preferences/editor/minimapShow', False, type=bool)
    #    'preferences/editor/minimapMaxOpacity', 0.8, type=float))
    #    'preferences/editor/minimapMinOpacity', 0.1, type=float))
    #    'preferences/editor/minimapSizeProportion', 0.17, type=float))
    #    'preferences/editor/docmapShow', True, type=bool)
    #    'preferences/editor/docmapSlider', False, type=bool)
    #    'preferences/editor/editorScrollBar', True, type=bool)
    #    'preferences/editor/docmapWidth', 15, type=int))
    HIGHLIGHT_CURRENT_LINE = qsettings.value(
        'editor/display/highlightCurrentLine', True, type=bool)
    HIGHLIGHT_CURRENT_LINE_MODE = qsettings.value(
        "editor/display/current_line_mode", 0, type=int)
    BRACE_MATCHING = qsettings.value(
        "editor/display/brace_matching", True, type=bool)
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
    SHOW_LINE_NUMBERS = qsettings.value(
        'editor/display/show_line_numbers', True, type=bool)
    SHOW_TEXT_CHANGES = qsettings.value(
        "editor/display/show_text_changes", True, type=bool)
    EDITOR_SCHEME = qsettings.value(
        "editor/general/scheme", "Ninja Dark", type=str)
    #    'preferences/editor/removeTrailingSpaces', True, type=bool)
    #    "preferences/editor/addNewLineAtEnd", True, type=bool)
    #    'preferences/editor/show_whitespaces', False, type=bool)
    USE_TABS = qsettings.value('editor/behavior/use_tabs', False, type=bool)
    #    "preferences/editor/hideMouseCursor", True, type=bool)
    #    "preferences/editor/scrollWheelZomming", True, type=bool)
    # FIXME:
    ALLOW_WORD_WRAP = qsettings.value(
        'editor/display/allow_word_wrap', False, type=bool)
    #    'preferences/editor/completeDeclarations', True, type=bool)
    #    'preferences/editor/errorsUnderlineBackground', True, type=bool)
    font = qsettings.value('editor/general/default_font', None)
    if font:
        FONT = font
    FONT_ANTIALIASING = qsettings.value("editor/general/font_antialiasing",
                                        True, type=bool)
    SHOW_INDENTATION_GUIDES = qsettings.value(
        "editor/display/show_indentation_guides", False, type=bool)
    #    'preferences/editor/defaultIgnorePep8', [], type='QStringList'))
    # FIXME:
    FIND_ERRORS = qsettings.value(
        "editor/display/check_errors", True, type=bool)
    #    'preferences/editor/showMigrationTips', True, type=bool)
    #    'preferences/editor/errorsInLine', True, type=bool)
    CHECK_STYLE = qsettings.value('editor/display/check_style',
                                  True, type=bool)
    AUTOCOMPLETE_BRACKETS = qsettings.value(
        "editor/intellisense/autocomplete_brackets", True, type=bool)
    AUTOCOMPLETE_QUOTES = qsettings.value(
        "editor/intellisense/autocomplete_quotes", True, type=bool)
    #    'preferences/editor/checkStyleInline', True, type=bool)
    #    'preferences/editor/codeCompletion', True, type=bool)
    #    'preferences/editor/endAtLastLine', True, type=bool)
    # parentheses = qsettings.value('preferences/editor/parentheses', True,
    #                              type=bool)
    # simpleQuotes = qsettings.value('preferences/editor/simpleQuotes',
    #                               True, type=bool)
    # doubleQuotes = qsettings.value('preferences/editor/doubleQuotes',
    #                               True, type=bool)
    # Projects
    #    'preferences/interface/showProjectExplorer', True, type=bool)
    #    'preferences/interface/showSymbolsList', True, type=bool)
    SHOW_WEB_INSPECTOR = qsettings.value(
        "interface/showWebInspector", False, type=bool)
    SHOW_ERRORS_LIST = qsettings.value(
        "interface/showErrorsList", True, type=bool)
    #    'preferences/interface/showMigrationList', True, type=bool)
    # Bookmarks and Breakpoints
    NOTIFICATION_ON_SAVE = qsettings.value(
        "editor/general/notificate_on_save", True, type=bool)
    # Checkers
    #    'preferences/editor/checkForDocstrings', False, type=bool)
    #    'interface/notification_position', 1, type=int)
    #    'preferences/general/notification_color', "#222", type='QString')
    LAST_CLEAN_LOCATOR = qsettings.value("ide/cleanLocator", None)
    from ninja_ide.extensions import handlers
    handlers.init_basic_handlers()
    clean_locator_db(qsettings)
