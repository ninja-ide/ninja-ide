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


from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys

from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import QDir
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import Qt


###############################################################################
# CHECK PYTHON VERSION
###############################################################################

IS_PYTHON3 = sys.version_info.major == 3

###############################################################################
# PATHS
###############################################################################

HOME_PATH = QDir.toNativeSeparators(QDir.homePath())

NINJA_EXECUTABLE = os.path.realpath(sys.argv[0])

PRJ_PATH = os.path.abspath(os.path.dirname(__file__))
if not IS_PYTHON3:
    PRJ_PATH = PRJ_PATH.decode('utf-8')
#Only for py2exe
frozen = getattr(sys, 'frozen', '')
if frozen in ('dll', 'console_exe', 'windows_exe'):
    # py2exe:
    PRJ_PATH = os.path.abspath(os.path.dirname(sys.executable))

HOME_NINJA_PATH = os.path.join(HOME_PATH, ".ninja_ide")

NINJA_KNOWLEDGE_PATH = os.path.join(HOME_NINJA_PATH, 'knowledge')

SETTINGS_PATH = os.path.join(HOME_NINJA_PATH, 'ninja_settings.ini')

DATA_SETTINGS_PATH = os.path.join(HOME_NINJA_PATH, 'data_settings.ini')

EXTENSIONS_PATH = os.path.join(HOME_NINJA_PATH, "extensions")

SYNTAX_FILES = os.path.join(PRJ_PATH, "extensions", "syntax")

PLUGINS = os.path.join(HOME_NINJA_PATH, "extensions", "plugins")

PLUGINS_DESCRIPTOR = os.path.join(EXTENSIONS_PATH,
                                  "plugins", "descriptor.json")

LANGS = os.path.join(EXTENSIONS_PATH, "languages")

EDITOR_SKINS = os.path.join(EXTENSIONS_PATH, "schemes")

NINJA_THEME = os.path.join(PRJ_PATH, "extensions", "theme", "ninja_dark.qss")

NINJA_THEME_CLASSIC = os.path.join(
    PRJ_PATH, "extensions", "theme", "ninja_theme.qss")

NINJA_THEME_DOWNLOAD = os.path.join(EXTENSIONS_PATH, "theme")

LOG_FILE_PATH = os.path.join(HOME_NINJA_PATH, 'ninja_ide.log')

GET_SYSTEM_PATH = os.path.join(PRJ_PATH, 'tools', 'get_system_path.py')

QML_FILES = os.path.join(PRJ_PATH, "gui", "qml")

###############################################################################
# URLS
###############################################################################

BUGS_PAGE = "https://github.com/ninja-ide/ninja-ide/issues"

PLUGINS_DOC = "http://ninja-ide.readthedocs.org/en/latest/"

UPDATES_URL = 'http://ninja-ide.org/updates'

SCHEMES_URL = 'http://ninja-ide.org/schemes/api/'

LANGUAGES_URL = 'http://ninja-ide.org/plugins/languages'

PLUGINS_WEB = 'http://ninja-ide.org/plugins/api/official'

PLUGINS_COMMUNITY = 'http://ninja-ide.org/plugins/api/community'


###############################################################################
# COLOR SCHEMES
###############################################################################

COLOR_SCHEME = {
    "Default": "#c5c8c6",
    "Keyword": "#83c1fb",
    "Operator": "#FFFFFF",
    "Brace": "#FFFFFF",
    "Caret": "#FFFFFF",
    "FunctionMethodName": "#fdff74",
    "ClassName": "#fdff74",
    "Identifier": "#c5c8c6",
    "DoubleQuotedString": "#d07cd3",
    "SingleQuotedString": "#d07cd3",
    "TripleDoubleQuotedString": "#86d986",
    "TripleSingleQuotedString": "#86d986",
    "Comment": "#7c7c7c",
    "CommentBlock": "#7c7c7c",
    "SelfReference": "#6EC7D7",
    "HighlightedIdentifier": "#6EC7D7",
    "Number": "#F8A008",
    "Decorator": "#fdb269",
    "EditorBackground": "#1d1f21",
    "EditorSelectionColor": "#000000",
    "EditorSelectionBackground": "#aaaaaa",
    "CurrentLine": "#313233",
    "SelectedWord": "a8ff60",
    "Pending": "red",
    "SelectedWordBackground": "#009B00",
    "FoldArea": "#292c2f",
    "FoldArrowExpanded": "#696c6e",
    "FoldArrowCollapsed": "white",
    "LinkNavigate": "005aff",
    "BraceBackground": "#5BC85B",
    "BraceForeground": "red",
    "ErrorUnderline": "0000ff",
    "Pep8Underline": "00ffff",
    "SidebarBackground": "#292c2f",
    "SidebarSelectedBackground": "#46484b",
    "SidebarForeground": "#868989",
    "SidebarSelectedForeground": "#c5c8c6",
    "MigrationUnderline": "ff0000",
    "MarginLine": '#7c7c7c',
}

CUSTOM_SCHEME = {}


def get_color(key):
    if key in COLOR_SCHEME:
        return CUSTOM_SCHEME.get(key, COLOR_SCHEME.get(key))
    return None


###############################################################################
# SHORTCUTS
###############################################################################

#default shortcuts

SHORTCUTS = {
    "Duplicate": QKeySequence(Qt.CTRL + Qt.Key_R),  # Replicate
    "Remove-line": QKeySequence(Qt.CTRL + Qt.Key_E),  # Eliminate
    "Move-up": QKeySequence(Qt.ALT + Qt.Key_Up),
    "Move-down": QKeySequence(Qt.ALT + Qt.Key_Down),
    "Close-file": QKeySequence(Qt.CTRL + Qt.Key_W),
    "New-file": QKeySequence(Qt.CTRL + Qt.Key_N),
    "New-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_N),
    "Open-file": QKeySequence(Qt.CTRL + Qt.Key_O),
    "Open-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_O),
    "Save-file": QKeySequence(Qt.CTRL + Qt.Key_S),
    "Save-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S),
    "Print-file": QKeySequence(Qt.CTRL + Qt.Key_P),
    "Redo": QKeySequence(Qt.CTRL + Qt.Key_Y),
    "Comment": QKeySequence(Qt.CTRL + Qt.Key_G),
    "Uncomment": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_G),
    "Horizontal-line": QKeySequence(),
    "Title-comment": QKeySequence(),
    "Indent-less": QKeySequence(Qt.SHIFT + Qt.Key_Tab),
    "Hide-misc": QKeySequence(Qt.Key_F4),
    "Hide-editor": QKeySequence(Qt.Key_F3),
    "Hide-explorer": QKeySequence(Qt.Key_F2),
    "Run-file": QKeySequence(Qt.CTRL + Qt.Key_F6),
    "Run-project": QKeySequence(Qt.Key_F6),
    "Debug": QKeySequence(Qt.Key_F7),
    "Show-Selector": QKeySequence(Qt.CTRL + Qt.Key_QuoteLeft),
    "Stop-execution": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F6),
    "Hide-all": QKeySequence(Qt.Key_F11),
    "Full-screen": QKeySequence(Qt.CTRL + Qt.Key_F11),
    "Find": QKeySequence(Qt.CTRL + Qt.Key_F),
    "Find-replace": QKeySequence(Qt.CTRL + Qt.Key_H),
    "Find-with-word": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F),
    "Find-next": QKeySequence(Qt.CTRL + Qt.Key_F3),
    "Find-previous": QKeySequence(Qt.SHIFT + Qt.Key_F3),
    "Help": QKeySequence(Qt.Key_F1),
    "Split-horizontal": QKeySequence(Qt.Key_F9),
    "Split-vertical": QKeySequence(Qt.CTRL + Qt.Key_F9),
    "Close-Split": QKeySequence(Qt.SHIFT + Qt.Key_F9),
    "Split-assistance": QKeySequence(Qt.Key_F10),
    "Follow-mode": QKeySequence(Qt.CTRL + Qt.Key_F10),
    "Reload-file": QKeySequence(Qt.Key_F5),
    "Find-in-files": QKeySequence(Qt.CTRL + Qt.Key_L),
    "Import": QKeySequence(Qt.CTRL + Qt.Key_I),
    "Go-to-definition": QKeySequence(Qt.CTRL + Qt.Key_Return),
    "Complete-Declarations": QKeySequence(Qt.ALT + Qt.Key_Return),
    "Code-locator": QKeySequence(Qt.CTRL + Qt.Key_K),
    "File-Opener": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_O),
    "Navigate-back": QKeySequence(Qt.ALT + Qt.Key_Left),
    "Navigate-forward": QKeySequence(Qt.ALT + Qt.Key_Right),
    "Open-recent-closed": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_T),
    "Change-Tab": QKeySequence(Qt.CTRL + Qt.Key_PageDown),
    "Change-Tab-Reverse": QKeySequence(Qt.CTRL + Qt.Key_PageUp),
    "Show-Code-Nav": QKeySequence(Qt.CTRL + Qt.Key_3),
    "Show-Paste-History": QKeySequence(Qt.CTRL + Qt.Key_4),
    "History-Copy": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_C),
    "History-Paste": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_V),
    "Add-Bookmark-or-Breakpoint": QKeySequence(Qt.CTRL + Qt.Key_B),
    #"change-split-focus": QKeySequence(Qt.CTRL + Qt.Key_Tab),
    "Move-Tab-to-right": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_0),
    "Move-Tab-to-left": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_9),
    "change-tab-visibility": QKeySequence(Qt.SHIFT + Qt.Key_F1),
    "Highlight-Word": QKeySequence(Qt.CTRL + Qt.Key_Down),
    "undo": QKeySequence(Qt.CTRL + Qt.Key_Z),
    "Indent-more": QKeySequence(Qt.Key_Tab),
    "cut": QKeySequence(Qt.CTRL + Qt.Key_X),
    "copy": QKeySequence(Qt.CTRL + Qt.Key_C),
    "paste": QKeySequence(Qt.CTRL + Qt.Key_V),
    "expand-symbol-combo": QKeySequence(Qt.CTRL + Qt.Key_2),
    "expand-file-combo": QKeySequence(Qt.CTRL + Qt.Key_Tab)}

CUSTOM_SHORTCUTS = {}

###############################################################################
# FUNCTIONS
###############################################################################


def load_shortcuts():
    """
    Loads the shortcuts from QSettings
    """
    global SHORTCUTS, CUSTOM_SHORTCUTS
    settings = QSettings(SETTINGS_PATH, QSettings.IniFormat)
    for action in SHORTCUTS:
        #default shortcut
        default_action = SHORTCUTS[action].toString()
        #get the custom shortcut or the default
        shortcut_action = settings.value("shortcuts/%s" % action,
                                         default_action)
        #set the shortcut
        CUSTOM_SHORTCUTS[action] = QKeySequence(shortcut_action)


def get_shortcut(shortcut_name):
    """
    Returns the shortcut looking into CUSTOM_SHORTCUTS and
    SHORTCUTS
    """
    global SHORTCUTS, CUSTOM_SHORTCUTS
    return CUSTOM_SHORTCUTS.get(shortcut_name, SHORTCUTS.get(shortcut_name))


def clean_custom_shortcuts():
    """
    Cleans CUSTOMS_SHORTCUTS
    """
    global CUSTOM_SHORTCUTS
    CUSTOM_SHORTCUTS = {}


def create_home_dir_structure():
    """
    Create the necesary directories structure for NINJA-IDE
    """
    for directory in (HOME_NINJA_PATH, EXTENSIONS_PATH, PLUGINS, EDITOR_SKINS,
                      LANGS, NINJA_THEME_DOWNLOAD, NINJA_KNOWLEDGE_PATH):
        if not os.path.isdir(directory):
            os.mkdir(directory)
