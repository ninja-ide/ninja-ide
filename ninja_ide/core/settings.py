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

import sys

from PyQt4.QtCore import QSettings

from ninja_ide.dependencies import pep8mod


###############################################################################
# OS DETECTOR
###############################################################################

# Use this flags instead of sys.platform spreaded in the source code
IS_WINDOWS = False

OS_KEY = "Ctrl"

FONT_FAMILY = 'Monospace'
FONT_SIZE = 11
if sys.platform == "darwin":
    from PyQt4.QtGui import QKeySequence
    from PyQt4.QtCore import Qt

    FONT_FAMILY = 'Monaco'
    FONT_SIZE = 11
    OS_KEY = QKeySequence(Qt.CTRL).toString(QKeySequence.NativeText)
elif sys.platform == "win32":
    FONT_FAMILY = 'Courier'
    FONT_SIZE = 10
    IS_WINDOWS = True

###############################################################################
# IDE
###############################################################################

MAX_OPACITY = 1
MIN_OPACITY = 0.3

TOOLBAR_AREA = 1
#UI LAYOUT
#001 : Central Rotate
#010 : Panels Rotate
#100 : Central Orientation
UI_LAYOUT = 0

LANGUAGE = ""

SHOW_START_PAGE = True

CONFIRM_EXIT = True
NOTIFY_UPDATES = True
HIDE_TOOLBAR = False
SHOW_STATUS_NOTIFICATIONS = True

PYTHON_PATH = "python"
EXECUTION_OPTIONS = ""

PROFILES = {}

TOOLBAR_ITEMS = [
    "new-file", "new-project", "open-file", "open-project", "save-file",
    "separator", "splitv", "splith", "follow-mode", "separator",
    "cut", "copy", "paste", "separator",
    "run-project", "run-file", "stop", "separator",
    ]

TOOLBAR_ITEMS_DEFAULT = [
    "new-file", "new-project", "open-file", "open-project", "save-file",
    "separator", "splitv", "splith", "follow-mode", "separator",
    "cut", "copy", "paste", "separator",
    "run-project", "run-file", "stop", "separator",
    ]

#hold the toolbar actions added by plugins
TOOLBAR_ITEMS_PLUGINS = []

NINJA_SKIN = 'Default'


###############################################################################
# EDITOR
###############################################################################

USE_TABS = False
ALLOW_WORD_WRAP = False
INDENT = 4
# by default Unix (\n) is used
USE_PLATFORM_END_OF_LINE = False
MARGIN_LINE = 80
SHOW_MARGIN_LINE = True
REMOVE_TRAILING_SPACES = True
SHOW_TABS_AND_SPACES = True

BRACES = {'{': '}',
    '[': ']',
    '(': ')'}
QUOTES = {'"': '"',
    "'": "'"}

FONT_MAX_SIZE = 28
FONT_MIN_SIZE = 6
MAX_REMEMBER_TABS = 50
COPY_HISTORY_BUFFER = 20

FIND_ERRORS = True
ERRORS_HIGHLIGHT_LINE = True
CHECK_STYLE = True
CHECK_HIGHLIGHT_LINE = True
CODE_COMPLETION = True
COMPLETE_DECLARATIONS = True
SHOW_MIGRATION_TIPS = True
VALID_2TO3 = True
UNDERLINE_NOT_BACKGROUND = True

CENTER_ON_SCROLL = True

SYNTAX = {}

EXTENSIONS = {}

BREAKPOINTS = {}
BOOKMARKS = {}


###############################################################################
# CHECKERS
###############################################################################

CHECK_FOR_DOCSTRINGS = True


###############################################################################
# MINIMAP
###############################################################################

SHOW_MINIMAP = False
MINIMAP_MAX_OPACITY = 0.8
MINIMAP_MIN_OPACITY = 0.1
SIZE_PROPORTION = 0.17


###############################################################################
# FILE MANAGER
###############################################################################

SUPPORTED_EXTENSIONS = [
    '.py',
    '.html',
    '.jpg',
    '.png',
    '.ui',
    '.css',
    '.json',
    '.js',
    '.ini']


###############################################################################
# PROJECTS DATA
###############################################################################

#PROJECT_TYPES = {'Python': None}
PROJECT_TYPES = {}

LANGS = []


###############################################################################
# EXPLORER
###############################################################################

SHOW_PROJECT_EXPLORER = True
SHOW_SYMBOLS_LIST = True
SHOW_WEB_INSPECTOR = False
SHOW_ERRORS_LIST = False
SHOW_MIGRATION_LIST = True

#Symbols handler per language (file extension)
SYMBOLS_HANDLER = {}

#Backward compatibility with older Qt versions
WEBINSPECTOR_SUPPORTED = True


###############################################################################
# WORKSPACE
###############################################################################

WORKSPACE = ""


###############################################################################
# FUNCTIONS
###############################################################################


def set_project_type_handler(project_type, project_type_handler):
    """
    Set a project type handler for the given project_type
    """
    global PROJECT_TYPES
    PROJECT_TYPES[project_type] = project_type_handler


def get_project_type_handler(project_type):
    """
    Returns the handler for the given project_type
    """
    global PROJECT_TYPES
    return PROJECT_TYPES.get(project_type)


def get_all_project_types():
    """
    Returns the availables project types
    """
    global PROJECT_TYPES
    return list(PROJECT_TYPES.keys())


def set_symbols_handler(file_extension, symbols_handler):
    """
    Set a symbol handler for the given file_extension
    """
    global SYMBOLS_HANDLER
    SYMBOLS_HANDLER[file_extension] = symbols_handler


def get_symbols_handler(file_extension):
    """
    Returns the symbol handler for the given file_extension
    """
    global SYMBOLS_HANDLER
    return SYMBOLS_HANDLER.get(file_extension, None)


def add_toolbar_item_for_plugins(toolbar_action):
    """
    Add a toolbar action set from some plugin
    """
    global TOOLBAR_ITEMS_PLUGINS
    TOOLBAR_ITEMS_PLUGINS.append(toolbar_action)


def get_toolbar_item_for_plugins():
    """
    Returns the toolbar actions set by plugins
    """
    global TOOLBAR_ITEMS_PLUGINS
    return TOOLBAR_ITEMS_PLUGINS


def use_platform_specific_eol():
    global USE_PLATFORM_END_OF_LINE
    return USE_PLATFORM_END_OF_LINE

###############################################################################
# Utility functions to update (patch at runtime) pep8mod.py
###############################################################################


def pep8mod_refresh_checks():
    """
    Force to reload all checks in pep8mod.py
    """
    pep8mod.refresh_checks()


def pep8mod_add_ignore(ignore_code):
    """
    Patch pep8mod.py to ignore a given check by code
    EXAMPLE:
        pep8mod_add_ignore('W191')
        'W1919': 'indentation contains tabs'
    """
    pep8mod.options.ignore.append(ignore_code)


def pep8mod_remove_ignore(ignore_code):
    """
    Patch pep8mod.py to remove the ignore of a give check
    EXAMPLE:
        pep8mod_remove_ignore('W191')
        'W1919': 'indentation contains tabs'
    """
    if ignore_code in pep8mod.options.ignore:
        pep8mod.options.ignore.remove(ignore_code)


def pep8mod_update_margin_line_length(new_margin_line):
    """
    Patch pep8mod.py to update the margin line length with a new value
    """
    pep8mod.MAX_LINE_LENGTH = new_margin_line
    pep8mod.options.max_line_length = new_margin_line

###############################################################################
# LOAD SETTINGS
###############################################################################


def load_settings():
    qsettings = QSettings()
    #Globals
    global TOOLBAR_AREA
    global LANGUAGE
    global SHOW_START_PAGE
    global CONFIRM_EXIT
    global UI_LAYOUT
    global NOTIFY_UPDATES
    global PYTHON_PATH
    global PROFILES
    global NINJA_SKIN
    global EXECUTION_OPTIONS
    global SUPPORTED_EXTENSIONS
    global WORKSPACE
    global INDENT
    global USE_PLATFORM_END_OF_LINE
    global MARGIN_LINE
    global REMOVE_TRAILING_SPACES
    global SHOW_TABS_AND_SPACES
    global USE_TABS
    global ALLOW_WORD_WRAP
    global COMPLETE_DECLARATIONS
    global UNDERLINE_NOT_BACKGROUND
    global FONT_FAMILY
    global FONT_SIZE
    global SHOW_MARGIN_LINE
    global FIND_ERRORS
    global ERRORS_HIGHLIGHT_LINE
    global CHECK_STYLE
    global CHECK_HIGHLIGHT_LINE
    global SHOW_MIGRATION_TIPS
    global CODE_COMPLETION
    global CENTER_ON_SCROLL
    global SHOW_PROJECT_EXPLORER
    global SHOW_SYMBOLS_LIST
    global SHOW_WEB_INSPECTOR
    global SHOW_ERRORS_LIST
    global SHOW_MIGRATION_LIST
    global BOOKMARKS
    global CHECK_FOR_DOCSTRINGS
    global BREAKPOINTS
    global BRACES
    global HIDE_TOOLBAR
    global SHOW_STATUS_NOTIFICATIONS
    global TOOLBAR_ITEMS
    global SHOW_MINIMAP
    global MINIMAP_MAX_OPACITY
    global MINIMAP_MIN_OPACITY
    global SIZE_PROPORTION
    #General
    HIDE_TOOLBAR = qsettings.value("window/hide_toolbar", 'false') == 'true'
    SHOW_STATUS_NOTIFICATIONS = qsettings.value(
        "preferences/interface/showStatusNotifications", 'true') == 'true'
    TOOLBAR_AREA = int(qsettings.value('preferences/general/toolbarArea', 1))
    LANGUAGE = qsettings.value('preferences/interface/language', '')
    SHOW_START_PAGE = qsettings.value(
        'preferences/general/showStartPage', 'true') == 'true'
    CONFIRM_EXIT = qsettings.value('preferences/general/confirmExit',
        'true') == 'true'
    UI_LAYOUT = int(qsettings.value('preferences/interface/uiLayout', 0))
    NOTIFY_UPDATES = qsettings.value(
        'preferences/general/notifyUpdates', 'true') == 'true'
    PYTHON_PATH = qsettings.value('preferences/execution/pythonPath',
        'python')
    NINJA_SKIN = qsettings.value('preferences/theme/skin',
        'Default')
    profileDict = dict(qsettings.value('ide/profiles', {}))
    for key in profileDict:
        profile_list = list(profileDict[key])
        files = []
        if profile_list:
            files = [item
                for item in list(profile_list[0])]
        tempFiles = []
        for file_ in files:
            fileData = list(file_)
            if len(fileData) > 0:
                tempFiles.append([fileData[0], int(fileData[1])])
        files = tempFiles
        projects = []
        if len(profile_list) > 1:
            projects = [item for item in list(profile_list[1])]
        PROFILES[key] = [files, projects]
    toolbar_items = [item for item in list(qsettings.value(
        'preferences/interface/toolbar', []))]
    if toolbar_items:
        TOOLBAR_ITEMS = toolbar_items
    #EXECUTION OPTIONS
    EXECUTION_OPTIONS = qsettings.value(
        'preferences/execution/executionOptions', '')
    extensions = [item for item in list(qsettings.value(
        'preferences/general/supportedExtensions', []))]
    if extensions:
        SUPPORTED_EXTENSIONS = extensions
    WORKSPACE = qsettings.value(
        'preferences/general/workspace', "")
    #Editor
    SHOW_MINIMAP = qsettings.value(
        'preferences/editor/minimapShow', 'false') == 'true'
    MINIMAP_MAX_OPACITY = float(qsettings.value(
        'preferences/editor/minimapMaxOpacity', 0.8))
    MINIMAP_MIN_OPACITY = float(qsettings.value(
        'preferences/editor/minimapMinOpacity', 0.1))
    SIZE_PROPORTION = float(qsettings.value(
        'preferences/editor/minimapSizeProportion', 0.17))
    INDENT = int(qsettings.value('preferences/editor/indent', 4))
    eol = qsettings.value('preferences/editor/platformEndOfLine', 'false')
    USE_PLATFORM_END_OF_LINE = eol == 'true'
    MARGIN_LINE = int(qsettings.value('preferences/editor/marginLine', 80))
    pep8mod_update_margin_line_length(MARGIN_LINE)
    REMOVE_TRAILING_SPACES = qsettings.value(
        'preferences/editor/removeTrailingSpaces', 'true') == 'true'
    SHOW_TABS_AND_SPACES = qsettings.value(
        'preferences/editor/showTabsAndSpaces', 'true') == 'true'
    USE_TABS = qsettings.value('preferences/editor/useTabs', 'false') == 'true'
    if USE_TABS:
        pep8mod_add_ignore("W191")
        pep8mod_refresh_checks()
    ALLOW_WORD_WRAP = qsettings.value(
        'preferences/editor/allowWordWrap', 'false') == 'true'
    COMPLETE_DECLARATIONS = qsettings.value(
        'preferences/editor/completeDeclarations', 'true') == 'true'
    UNDERLINE_NOT_BACKGROUND = qsettings.value(
        'preferences/editor/errorsUnderlineBackground', 'true') == 'true'
    font_family = qsettings.value(
        'preferences/editor/fontFamily', "")
    if font_family:
        FONT_FAMILY = font_family
    font_size = int(qsettings.value('preferences/editor/fontSize', 0))
    if font_size != 0:
        FONT_SIZE = font_size
    SHOW_MARGIN_LINE = qsettings.value(
        'preferences/editor/showMarginLine', 'true') == 'true'
    FIND_ERRORS = qsettings.value('preferences/editor/errors',
        'true') == 'true'
    SHOW_MIGRATION_TIPS = qsettings.value(
        'preferences/editor/showMigrationTips', 'true') == 'true'
    ERRORS_HIGHLIGHT_LINE = qsettings.value(
        'preferences/editor/errorsInLine', 'true') == 'true'
    CHECK_STYLE = qsettings.value('preferences/editor/checkStyle',
        'true') == 'true'
    CHECK_HIGHLIGHT_LINE = qsettings.value(
        'preferences/editor/checkStyleInline', 'true') == 'true'
    CODE_COMPLETION = qsettings.value(
        'preferences/editor/codeCompletion', 'true') == 'true'
    CENTER_ON_SCROLL = qsettings.value(
        'preferences/editor/centerOnScroll', 'true') == 'true'
    parentheses = qsettings.value('preferences/editor/parentheses',
        'true') == 'true'
    if not parentheses:
        del BRACES['(']
    brackets = qsettings.value('preferences/editor/brackets', 'true') == 'true'
    if not brackets:
        del BRACES['[']
    keys = qsettings.value('preferences/editor/keys', 'true') == 'true'
    if not keys:
        del BRACES['{']
    simpleQuotes = qsettings.value('preferences/editor/simpleQuotes',
        'true') == 'true'
    if not simpleQuotes:
        del QUOTES["'"]
    doubleQuotes = qsettings.value('preferences/editor/doubleQuotes',
        'true') == 'true'
    if not doubleQuotes:
        del QUOTES['"']
    #Projects
    SHOW_PROJECT_EXPLORER = qsettings.value(
        'preferences/interface/showProjectExplorer', 'true') == 'true'
    SHOW_SYMBOLS_LIST = qsettings.value(
        'preferences/interface/showSymbolsList', 'true') == 'true'
    SHOW_WEB_INSPECTOR = qsettings.value(
        'preferences/interface/showWebInspector', 'false') == 'true'
    SHOW_ERRORS_LIST = qsettings.value(
        'preferences/interface/showErrorsList', 'false') == 'true'
    SHOW_MIGRATION_LIST = qsettings.value(
        'preferences/interface/showMigrationList', 'true') == 'true'
    #Bookmarks and Breakpoints
    bookmarks = dict(qsettings.value('preferences/editor/bookmarks', {}))
    for key in bookmarks:
        if key:
            BOOKMARKS[key] = [int(i) for i in list(bookmarks[key])]
    breakpoints = dict(qsettings.value('preferences/editor/breakpoints', {}))
    for key in breakpoints:
        if key:
            BREAKPOINTS[key] = [int(i) for i in list(breakpoints[key])]
    # Checkers
    CHECK_FOR_DOCSTRINGS = qsettings.value(
        'preferences/editor/checkForDocstrings', 'false') == 'true'
    # Import introspection here, it not needed in the namespace of
    # the rest of the file.
    from ninja_ide.tools import introspection
    #Set Default Symbol Handler
    set_symbols_handler('py', introspection)
