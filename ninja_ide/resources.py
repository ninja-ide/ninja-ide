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
import json

from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import (
    QDir,
    QSettings,
    Qt
)

from ninja_ide.core.file_handling import file_manager

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
# Only for py2exe
frozen = getattr(sys, 'frozen', '')
if frozen in ('dll', 'console_exe', 'windows_exe'):
    # py2exe:
    PRJ_PATH = os.path.abspath(os.path.dirname(sys.executable))

HOME_NINJA_PATH = os.path.join(HOME_PATH, ".ninja_ide")

NINJA_KNOWLEDGE_PATH = os.path.join(HOME_NINJA_PATH, 'knowledge')

SETTINGS_PATH = os.path.join(HOME_NINJA_PATH, 'ninja_settings.ini')

DATA_SETTINGS_PATH = os.path.join(HOME_NINJA_PATH, 'data_settings.ini')

EXTENSIONS_PATH = os.path.join(HOME_NINJA_PATH, "extensions")

SYNTAX_FILES = os.path.join(PRJ_PATH, "gui", "editor", "syntaxes")

PLUGINS = os.path.join(HOME_NINJA_PATH, "extensions", "plugins")

PLUGINS_DESCRIPTOR = os.path.join(EXTENSIONS_PATH,
                                  "plugins", "descriptor.json")

LANGS = os.path.join(EXTENSIONS_PATH, "languages")

EDITOR_SKINS = os.path.join(EXTENSIONS_PATH, "schemes")

EDITOR_SCHEMES = os.path.join(PRJ_PATH, "extensions", "styles")

NINJA_THEMES_DOWNLOAD = os.path.join(EXTENSIONS_PATH, "theme")

NINJA_THEMES = os.path.join(PRJ_PATH, "extensions", "theme")

# NINJA_THEME = os.path.join(PRJ_PATH, "extensions", "theme", "ninja_dark.qss")
NINJA_QSS = os.path.join(PRJ_PATH, "extensions", "theme", "qss")

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

COLOR_SCHEME = {}
CUSTOM_SCHEME = {}
QML_COLORS = {}


def _get_color(key):
    if key in COLOR_SCHEME:
        return CUSTOM_SCHEME.get(key, COLOR_SCHEME[key])['color']
    return None


def get_color_scheme(key):
    if key in COLOR_SCHEME:
        return CUSTOM_SCHEME.get(key, COLOR_SCHEME[key])
    return None


def get_color_hex(key):
    if key in COLOR_SCHEME:
        return CUSTOM_SCHEME.get(key, COLOR_SCHEME.get(key)).lstrip("#")
    return None


###############################################################################
# SHORTCUTS
###############################################################################

# default shortcuts

SHORTCUTS = {
    "duplicate-line": QKeySequence(Qt.CTRL + Qt.Key_D),  # Replicate
    "remove-line": QKeySequence(Qt.CTRL + Qt.Key_E),  # Eliminate
    "move-up": QKeySequence(Qt.ALT + Qt.Key_Up),
    "move-down": QKeySequence(Qt.ALT + Qt.Key_Down),
    "close-file": QKeySequence(Qt.CTRL + Qt.Key_W),
    "new-file": QKeySequence(Qt.CTRL + Qt.Key_N),
    "new-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_N),
    "open-file": QKeySequence(Qt.CTRL + Qt.Key_O),
    "openproject": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_O),
    "save-file": QKeySequence(Qt.CTRL + Qt.Key_S),
    "save-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S),
    "print-file": QKeySequence(Qt.CTRL + Qt.Key_P),
    "redo": QKeySequence(Qt.CTRL + Qt.Key_Y),
    "comment": QKeySequence(Qt.CTRL + Qt.Key_Slash),
    # "uncomment": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_G),
    "horizontal-line": QKeySequence(),
    "title-comment": QKeySequence(),
    "indent-less": QKeySequence(Qt.SHIFT + Qt.Key_Tab),
    "hide-misc": QKeySequence(Qt.Key_F4),
    "hide-editor": QKeySequence(Qt.Key_F3),
    "hide-explorer": QKeySequence(Qt.Key_F2),
    "run-file": QKeySequence(Qt.CTRL + Qt.Key_F6),
    "run-selection": QKeySequence(Qt.CTRL + Qt.Key_F7),
    "run-project": QKeySequence(Qt.Key_F6),
    "debug": QKeySequence(Qt.Key_F7),
    "show-selector": QKeySequence(Qt.CTRL + Qt.Key_QuoteLeft),
    "stop-execution": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F6),
    "hide-all": QKeySequence(Qt.Key_F11),
    "full-screen": QKeySequence(Qt.CTRL + Qt.Key_F11),
    "zoom-in": QKeySequence(Qt.CTRL + Qt.Key_Plus),
    "zoom-out": QKeySequence(Qt.CTRL + Qt.Key_Minus),
    "zoom-reset": QKeySequence(Qt.CTRL + Qt.Key_0),
    "find": QKeySequence(Qt.CTRL + Qt.Key_F),
    "find-replace": QKeySequence(Qt.CTRL + Qt.Key_H),
    "find-with-word": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F),
    "find-next": QKeySequence(Qt.CTRL + Qt.Key_F3),
    "find-previous": QKeySequence(Qt.SHIFT + Qt.Key_F3),
    "help": QKeySequence(Qt.Key_F1),
    "split-horizontal": QKeySequence(Qt.Key_F9),
    "split-vertical": QKeySequence(Qt.CTRL + Qt.Key_F9),
    "close-Split": QKeySequence(Qt.SHIFT + Qt.Key_F9),
    "split-assistance": QKeySequence(Qt.Key_F10),
    "follow-mode": QKeySequence(Qt.CTRL + Qt.Key_F10),
    "reload-file": QKeySequence(Qt.Key_F5),
    "find-in-files": QKeySequence(Qt.CTRL + Qt.Key_L),
    "import": QKeySequence(Qt.CTRL + Qt.Key_I),
    "go-to-definition": QKeySequence(Qt.CTRL + Qt.Key_Return),
    "complete-declarations": QKeySequence(Qt.ALT + Qt.Key_Return),
    "locator": QKeySequence(Qt.CTRL + Qt.Key_K),
    # "show-completions": QKeySequence(Qt.CTRL + Qt.Key_Space),
    "file-Opener": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_O),
    "navigate-back": QKeySequence(Qt.ALT + Qt.Key_Left),
    "navigate-forward": QKeySequence(Qt.ALT + Qt.Key_Right),
    "open-recent-closed": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_T),
    "change-Tab": QKeySequence(Qt.CTRL + Qt.Key_PageDown),
    "change-Tab-Reverse": QKeySequence(Qt.CTRL + Qt.Key_PageUp),
    "show-Code-Nav": QKeySequence(Qt.CTRL + Qt.Key_3),
    "show-Paste-History": QKeySequence(Qt.CTRL + Qt.Key_4),
    "history-Copy": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_C),
    "history-Paste": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_V),
    "add-bookmark-or-breakpoint": QKeySequence(Qt.CTRL + Qt.Key_B),
    # "change-split-focus": QKeySequence(Qt.CTRL + Qt.Key_Tab),
    "move-tab-to-right": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_0),
    "move-tab-to-left": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_9),
    "change-tab-visibility": QKeySequence(Qt.SHIFT + Qt.Key_F1),
    # "Highlight-Word": QKeySequence(Qt.CTRL + Qt.Key_Down),
    "undo": QKeySequence(Qt.CTRL + Qt.Key_Z),
    "indent-more": QKeySequence(Qt.Key_Tab),
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
        # default shortcut
        default_action = SHORTCUTS[action].toString()
        # get the custom shortcut or the default
        shortcut_action = settings.value("shortcuts/%s" % action,
                                         default_action)
        # set the shortcut
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
                      LANGS, NINJA_THEMES_DOWNLOAD, NINJA_KNOWLEDGE_PATH):
        if not os.path.isdir(directory):
            os.mkdir(directory)


def load_theme(name="Dark"):
    themes = {}
    for theme_dir in (NINJA_THEMES, NINJA_THEMES_DOWNLOAD):
        files = file_manager.get_files_from_folder(theme_dir, ".ninjatheme")
        for theme_file in files:
            filename = os.path.join(theme_dir, theme_file)
            with open(filename) as json_f:
                content = json.load(json_f)
                theme_name = content["name"]
                themes[theme_name] = content
    ninja_theme = themes[name]
    global QML_COLORS
    QML_COLORS = ninja_theme["qml"]
    return ninja_theme
