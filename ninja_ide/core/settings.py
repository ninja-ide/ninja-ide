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

PYTHON_PATH = "python"
EXECUTION_OPTIONS = ""

PROFILES = {}

TOOLBAR_ITEMS = [
    "new-file", "new-project", "open-file", "open-project", "save-file",
    "separator", "splith", "splitv", "follow-mode", "separator",
    "cut", "copy", "paste", "separator",
    "run-project", "run-file", "stop", "separator",
    ]

TOOLBAR_ITEMS_DEFAULT = [
    "new-file", "new-project", "open-file", "open-project", "save-file",
    "separator", "splith", "splitv", "follow-mode", "separator",
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
HIGHLIGHT_WHOLE_LINE = True

CENTER_ON_SCROLL = True

SYNTAX = {}

EXTENSIONS = {}

BREAKPOINTS = {}
BOOKMARKS = {}


###############################################################################
# CHECKERS
###############################################################################

CHECK_FOR_DOCSTRINGS = False


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
    return PROJECT_TYPES.keys()


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
    global MARGIN_LINE
    global REMOVE_TRAILING_SPACES
    global SHOW_TABS_AND_SPACES
    global USE_TABS
    global ALLOW_WORD_WRAP
    global COMPLETE_DECLARATIONS
    global HIGHLIGHT_WHOLE_LINE
    global FONT_FAMILY
    global FONT_SIZE
    global SHOW_MARGIN_LINE
    global FIND_ERRORS
    global ERRORS_HIGHLIGHT_LINE
    global CHECK_STYLE
    global CHECK_HIGHLIGHT_LINE
    global CODE_COMPLETION
    global CENTER_ON_SCROLL
    global SHOW_PROJECT_EXPLORER
    global SHOW_SYMBOLS_LIST
    global SHOW_WEB_INSPECTOR
    global SHOW_ERRORS_LIST
    global BOOKMARKS
    global CHECK_FOR_DOCSTRINGS
    global BREAKPOINTS
    global BRACES
    global HIDE_TOOLBAR
    global TOOLBAR_ITEMS
    global SHOW_MINIMAP
    global MINIMAP_MAX_OPACITY
    global MINIMAP_MIN_OPACITY
    global SIZE_PROPORTION
    #General
    HIDE_TOOLBAR = qsettings.value("window/hide_toolbar", False).toBool()
    TOOLBAR_AREA = qsettings.value(
        'preferences/general/toolbarArea', 1).toInt()[0]
    LANGUAGE = unicode(qsettings.value(
        'preferences/interface/language', '').toString())
    SHOW_START_PAGE = qsettings.value(
        'preferences/general/showStartPage', True).toBool()
    CONFIRM_EXIT = qsettings.value('preferences/general/confirmExit',
        True).toBool()
    UI_LAYOUT = qsettings.value('preferences/interface/uiLayout',
        0).toInt()[0]
    NOTIFY_UPDATES = qsettings.value(
        'preferences/general/notifyUpdates', True).toBool()
    PYTHON_PATH = unicode(
        qsettings.value('preferences/execution/pythonPath',
        'python').toString())
    NINJA_SKIN = unicode(
        qsettings.value('preferences/theme/skin', 'Default').toString())
    profileDict = qsettings.value('ide/profiles', {}).toMap()
    for key in profileDict:
        profile_list = list(profileDict[key].toList())
        files = []
        if profile_list:
            files = [item
                for item in profile_list[0].toList()]
        tempFiles = []
        for file_ in files:
            fileData = file_.toList()
            if len(fileData) > 0:
                tempFiles.append([unicode(fileData[0].toString()),
                    fileData[1].toInt()[0]])
        files = tempFiles
        projects = []
        if len(profile_list) > 1:
            projects = [unicode(item.toString())
                for item in profile_list[1].toList()]
        PROFILES[unicode(key)] = [files, projects]
    toolbar_items = [str(item.toString()) for item in qsettings.value(
        'preferences/interface/toolbar', []).toList()]
    if toolbar_items:
        TOOLBAR_ITEMS = toolbar_items
    #EXECUTION OPTIONS
    EXECUTION_OPTIONS = unicode(
        qsettings.value('preferences/execution/executionOptions',
        '').toString())
    extensions = [unicode(item.toString()) for item in qsettings.value(
        'preferences/general/supportedExtensions', []).toList()]
    if extensions:
        SUPPORTED_EXTENSIONS = extensions
    WORKSPACE = unicode(qsettings.value(
        'preferences/general/workspace', "").toString())
    #Editor
    SHOW_MINIMAP = qsettings.value(
        'preferences/editor/minimapShow', False).toBool()
    MINIMAP_MAX_OPACITY = qsettings.value(
        'preferences/editor/minimapMaxOpacity', 0.8).toFloat()[0]
    MINIMAP_MIN_OPACITY = qsettings.value(
        'preferences/editor/minimapMinOpacity', 0.1).toFloat()[0]
    SIZE_PROPORTION = qsettings.value(
        'preferences/editor/minimapSizeProportion', 0.17).toFloat()[0]
    INDENT = qsettings.value('preferences/editor/indent',
        4).toInt()[0]
    MARGIN_LINE = qsettings.value('preferences/editor/marginLine',
        80).toInt()[0]
    pep8mod.MAX_LINE_LENGTH = MARGIN_LINE
    REMOVE_TRAILING_SPACES = qsettings.value(
        'preferences/editor/removeTrailingSpaces', True).toBool()
    SHOW_TABS_AND_SPACES = qsettings.value(
        'preferences/editor/showTabsAndSpaces', True).toBool()
    USE_TABS = qsettings.value(
        'preferences/editor/useTabs', False).toBool()
    if USE_TABS:
        pep8mod.options.ignore.append("W191")
        pep8mod.refresh_checks()
    ALLOW_WORD_WRAP = qsettings.value(
        'preferences/editor/allowWordWrap', False).toBool()
    COMPLETE_DECLARATIONS = qsettings.value(
        'preferences/editor/completeDeclarations', True).toBool()
    HIGHLIGHT_WHOLE_LINE = qsettings.value(
        'preferences/editor/highlightWholeLine', True).toBool()
    font_family = unicode(qsettings.value(
        'preferences/editor/fontFamily', "").toString())
    if font_family:
        FONT_FAMILY = font_family
    font_size = qsettings.value('preferences/editor/fontSize',
        0).toInt()[0]
    if font_size != 0:
        FONT_SIZE = font_size
    SHOW_MARGIN_LINE = qsettings.value(
        'preferences/editor/showMarginLine', True).toBool()
    FIND_ERRORS = qsettings.value('preferences/editor/errors',
        True).toBool()
    ERRORS_HIGHLIGHT_LINE = qsettings.value(
        'preferences/editor/errorsInLine', True).toBool()
    CHECK_STYLE = qsettings.value('preferences/editor/checkStyle',
        True).toBool()
    CHECK_HIGHLIGHT_LINE = qsettings.value(
        'preferences/editor/checkStyleInline', True).toBool()
    CODE_COMPLETION = qsettings.value(
        'preferences/editor/codeCompletion', True).toBool()
    CENTER_ON_SCROLL = qsettings.value(
        'preferences/editor/centerOnScroll', True).toBool()
    parentheses = qsettings.value('preferences/editor/parentheses',
        True).toBool()
    if not parentheses:
        del BRACES['(']
    brackets = qsettings.value('preferences/editor/brackets',
        True).toBool()
    if not brackets:
        del BRACES['[']
    keys = qsettings.value('preferences/editor/keys',
        True).toBool()
    if not keys:
        del BRACES['{']
    simpleQuotes = qsettings.value('preferences/editor/simpleQuotes',
        True).toBool()
    if not simpleQuotes:
        del QUOTES["'"]
    doubleQuotes = qsettings.value('preferences/editor/doubleQuotes',
        True).toBool()
    if not doubleQuotes:
        del QUOTES['"']
    #Projects
    SHOW_PROJECT_EXPLORER = qsettings.value(
        'preferences/interface/showProjectExplorer', True).toBool()
    SHOW_SYMBOLS_LIST = qsettings.value(
        'preferences/interface/showSymbolsList', True).toBool()
    SHOW_WEB_INSPECTOR = qsettings.value(
        'preferences/interface/showWebInspector', False).toBool()
    SHOW_ERRORS_LIST = qsettings.value(
        'preferences/interface/showErrorsList', False).toBool()
    #Bookmarks and Breakpoints
    bookmarks = qsettings.value('preferences/editor/bookmarks', {}).toMap()
    for key in bookmarks:
        if key:
            BOOKMARKS[unicode(key)] = [
                i.toInt()[0] for i in bookmarks[key].toList()]
    breakpoints = qsettings.value('preferences/editor/breakpoints', {}).toMap()
    for key in breakpoints:
        if key:
            BREAKPOINTS[unicode(key)] = [
                i.toInt()[0] for i in breakpoints[key].toList()]
    # Checkers
    CHECK_FOR_DOCSTRINGS = qsettings.value(
        'preferences/editor/checkForDocstrings', False).toBool()
    # Import introspection here, it not needed in the namespace of
    # the rest of the file.
    from ninja_ide.tools import introspection
    #Set Default Symbol Handler
    set_symbols_handler('py', introspection)
