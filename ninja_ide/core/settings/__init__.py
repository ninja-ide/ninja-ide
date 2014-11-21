# -*- coding: utf-8 -*-


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


"""Settings for Ninja-IDE."""


# imports
from __future__ import absolute_import

from PyQt4.QtCore import QSettings

from ninja_ide import resources
from ninja_ide.extensions import handlers

# imports of individual setting modules.
from .operating_system_detector import *  # lint:ok
from .ide_settings_variables import *     # lint:ok
from .editor_settings_variables import *  # lint:ok
from .checkers import *                   # lint:ok
from .minimap import *                    # lint:ok
from .filemanager import *                # lint:ok
from .projects_data import *              # lint:ok
from .explorer import *                   # lint:ok
from .workspaces import *                  # lint:ok
from .helper_functions import *           # lint:ok
from .pep8mod_utility_functions import *  # lint:ok
from .locator_knowledge import *          # lint:ok


###############################################################################
# LOAD SETTINGS
###############################################################################


def load_settings():
    """Load all the Settings."""
    qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
    data_qsettings = QSettings(resources.DATA_SETTINGS_PATH,
                               QSettings.IniFormat)

    # Globals
    global ALLOW_WORD_WRAP, BOOKMARKS, BRACES, BREAKPOINTS, CENTER_ON_SCROLL
    global CHECK_FOR_DOCSTRINGS, CHECK_HIGHLIGHT_LINE, CHECK_STYLE
    global CODE_COMPLETION, COMPLETE_DECLARATIONS, CONFIRM_EXIT
    global ERRORS_HIGHLIGHT_LINE, EXECUTION_OPTIONS, FIND_ERRORS, FONT
    global HIDE_TOOLBAR, INDENT, LANGUAGE, LAST_CLEAN_LOCATOR, MARGIN_LINE
    global MINIMAP_MAX_OPACITY, MINIMAP_MIN_OPACITY, NINJA_SKIN
    global NOTIFICATION_COLOR, NOTIFICATION_POSITION, PYTHON_EXEC
    global PYTHON_EXEC_CONFIGURED_BY_USER, REMOVE_TRAILING_SPACES, SESSIONS
    global SHOW_ERRORS_LIST, SHOW_INDENTATION_GUIDE, SHOW_MARGIN_LINE
    global SHOW_MIGRATION_LIST, SHOW_MIGRATION_TIPS, SHOW_MINIMAP
    global SHOW_PROJECT_EXPLORER, SHOW_START_PAGE, SHOW_SYMBOLS_LIST
    global SHOW_TABS_AND_SPACES, SHOW_WEB_INSPECTOR, SIZE_PROPORTION
    global SUPPORTED_EXTENSIONS, TOOLBAR_AREA, TOOLBAR_ITEMS, UI_LAYOUT
    global UNDERLINE_NOT_BACKGROUND, USE_PLATFORM_END_OF_LINE, USE_TABS
    global WORKSPACE

    # General
    HIDE_TOOLBAR = qsettings.value("window/hide_toolbar", False, type=bool)
    TOOLBAR_AREA = qsettings.value('preferences/general/toolbarArea', 1,
                                   type=int)
    LANGUAGE = qsettings.value('preferences/interface/language', '',
                               type='QString')
    SHOW_START_PAGE = qsettings.value(
        'preferences/general/showStartPage', True, type=bool)
    CONFIRM_EXIT = qsettings.value('preferences/general/confirmExit',
                                   True, type=bool)
    UI_LAYOUT = qsettings.value('preferences/interface/uiLayout', 0, type=int)
    PYTHON_EXEC = qsettings.value('preferences/execution/pythonExec',
                                  'python', type='QString')
    PYTHON_EXEC_CONFIGURED_BY_USER = qsettings.value(
        'preferences/execution/pythonExecConfigured', False, type=bool)
    NINJA_SKIN = qsettings.value('preferences/theme/skin',
                                 'Default', type='QString')
    sessionDict = dict(data_qsettings.value('ide/sessions', {}))

    # Fix later
    try:
        for key in sessionDict:
            session_list = list(sessionDict[key])
            files = []
            if session_list:
                files = [item for item in tuple(session_list[0])]
            tempFiles = []
            for file_ in files:
                fileData = tuple(file_)
                if len(fileData) > 0:
                    tempFiles.append(
                        [fileData[0], int(fileData[1]), fileData[2]])
            files = tempFiles
            projects = []
            if len(session_list) > 1:
                projects = [item for item in tuple(session_list[1])]
            SESSIONS[key] = [files, projects]
    except:
        pass

    # TODO: What to do? :P
    # toolbar_items = [
    #     i for i in list(qsettings.value('preferences/interface/toolbar', []))]
    # if toolbar_items:
    #     TOOLBAR_ITEMS = toolbar_items

    # EXECUTION OPTIONS
    EXECUTION_OPTIONS = qsettings.value(
        'preferences/execution/executionOptions',
        defaultValue='', type='QString')
    extensions = [item for item in tuple(qsettings.value(
        'preferences/general/supportedExtensions', []))]
    if extensions:
        SUPPORTED_EXTENSIONS = extensions
    WORKSPACE = qsettings.value(
        'preferences/general/workspace', "", type='QString')

    # Editor
    SHOW_MINIMAP = qsettings.value(
        'preferences/editor/minimapShow', False, type=bool)
    MINIMAP_MAX_OPACITY = float(qsettings.value(
        'preferences/editor/minimapMaxOpacity', 0.8, type=float))
    MINIMAP_MIN_OPACITY = float(qsettings.value(
        'preferences/editor/minimapMinOpacity', 0.1, type=float))
    SIZE_PROPORTION = float(qsettings.value(
        'preferences/editor/minimapSizeProportion', 0.17, type=float))
    INDENT = int(qsettings.value('preferences/editor/indent', 4, type=int))

    USE_PLATFORM_END_OF_LINE = qsettings.value(
        'preferences/editor/platformEndOfLine', False, type=bool)
    MARGIN_LINE = qsettings.value('preferences/editor/marginLine', 80,
                                  type=int)
    pep8mod_update_margin_line_length(MARGIN_LINE)
    REMOVE_TRAILING_SPACES = qsettings.value(
        'preferences/editor/removeTrailingSpaces', True, type=bool)
    SHOW_TABS_AND_SPACES = qsettings.value(
        'preferences/editor/showTabsAndSpaces', False, type=bool)
    USE_TABS = qsettings.value('preferences/editor/useTabs', False, type=bool)
    if USE_TABS:
        pep8mod_add_ignore("W191")
        pep8mod_refresh_checks()
    ALLOW_WORD_WRAP = qsettings.value(
        'preferences/editor/allowWordWrap', False, type=bool)
    COMPLETE_DECLARATIONS = qsettings.value(
        'preferences/editor/completeDeclarations', True, type=bool)
    UNDERLINE_NOT_BACKGROUND = qsettings.value(
        'preferences/editor/errorsUnderlineBackground', True, type=bool)
    font = qsettings.value('preferences/editor/font', None)
    if font:
        FONT = font
    SHOW_MARGIN_LINE = qsettings.value(
        'preferences/editor/showMarginLine', True, type=bool)
    SHOW_INDENTATION_GUIDE = qsettings.value(
        'preferences/editor/showIndentationGuide', True, type=bool)
    FIND_ERRORS = qsettings.value('preferences/editor/errors', True, type=bool)
    SHOW_MIGRATION_TIPS = qsettings.value(
        'preferences/editor/showMigrationTips', True, type=bool)
    ERRORS_HIGHLIGHT_LINE = qsettings.value(
        'preferences/editor/errorsInLine', True, type=bool)
    CHECK_STYLE = qsettings.value('preferences/editor/checkStyle',
                                  True, type=bool)
    CHECK_HIGHLIGHT_LINE = qsettings.value(
        'preferences/editor/checkStyleInline', True, type=bool)
    CODE_COMPLETION = qsettings.value(
        'preferences/editor/codeCompletion', True, type=bool)
    CENTER_ON_SCROLL = qsettings.value(
        'preferences/editor/centerOnScroll', True, type=bool)
    parentheses = qsettings.value('preferences/editor/parentheses', True,
                                  type=bool)
    if not parentheses:
        del BRACES['(']
    brackets = qsettings.value('preferences/editor/brackets', True, type=bool)
    if not brackets:
        del BRACES['[']
    keys = qsettings.value('preferences/editor/keys', True, type=bool)
    if not keys:
        del BRACES['{']
    simpleQuotes = qsettings.value('preferences/editor/simpleQuotes',
                                   True, type=bool)
    if not simpleQuotes:
        del QUOTES["'"]
    doubleQuotes = qsettings.value('preferences/editor/doubleQuotes',
                                   True, type=bool)
    if not doubleQuotes:
        del QUOTES['"']

    # Projects
    SHOW_PROJECT_EXPLORER = qsettings.value(
        'preferences/interface/showProjectExplorer', True, type=bool)
    SHOW_SYMBOLS_LIST = qsettings.value(
        'preferences/interface/showSymbolsList', True, type=bool)
    SHOW_WEB_INSPECTOR = qsettings.value(
        'preferences/interface/showWebInspector', False, type=bool)
    SHOW_ERRORS_LIST = qsettings.value(
        'preferences/interface/showErrorsList', True, type=bool)
    SHOW_MIGRATION_LIST = qsettings.value(
        'preferences/interface/showMigrationList', True, type=bool)

    # Bookmarks and Breakpoints
    bookmarks = dict(qsettings.value('preferences/editor/bookmarks', {}))
    for key in bookmarks:
        if key:
            BOOKMARKS[key] = [int(i) for i in tuple(bookmarks[key])]
    breakpoints = dict(qsettings.value('preferences/editor/breakpoints', {}))
    for key in breakpoints:
        if key:
            BREAKPOINTS[key] = [int(i) for i in tuple(breakpoints[key])]

    # Checkers
    CHECK_FOR_DOCSTRINGS = qsettings.value(
        'preferences/editor/checkForDocstrings', False, type=bool)
    NOTIFICATION_POSITION = qsettings.value(
        'preferences/general/notification_position', 0, type=int)
    NOTIFICATION_COLOR = qsettings.value(
        'preferences/general/notification_color', "#000", type='QString')
    LAST_CLEAN_LOCATOR = qsettings.value(
        'preferences/general/cleanLocator', None)
    handlers.init_basic_handlers()
    clean_locator_db(qsettings)
