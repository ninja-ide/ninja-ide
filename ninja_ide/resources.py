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

from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import QDir
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import Qt

import os
import sys


###############################################################################
# PATHS
###############################################################################

HOME_PATH = QDir.toNativeSeparators(QDir.homePath())

NINJA_EXECUTABLE = os.path.realpath(sys.argv[0])

PRJ_PATH = os.path.abspath(os.path.dirname(__file__))
#Only for py2exe
frozen = getattr(sys, 'frozen', '')
if frozen in ('dll', 'console_exe', 'windows_exe'):
    # py2exe:
    PRJ_PATH = os.path.abspath(os.path.dirname(sys.executable))

HOME_NINJA_PATH = os.path.join(HOME_PATH, ".ninja_ide")

ADDINS = os.path.join(HOME_NINJA_PATH, "addins")

SYNTAX_FILES = os.path.join(PRJ_PATH, "addins", "syntax")

PLUGINS = os.path.join(HOME_NINJA_PATH, "addins", "plugins")

PLUGINS_DESCRIPTOR = os.path.join(HOME_NINJA_PATH, "addins",
                                    "plugins", "descriptor.json")

LANGS = os.path.join(PRJ_PATH, "addins", "lang")

LANGS_DOWNLOAD = os.path.join(HOME_NINJA_PATH, "addins", "languages")

EDITOR_SKINS = os.path.join(HOME_NINJA_PATH, "addins", "schemes")

START_PAGE_URL = os.path.join(PRJ_PATH, "doc", "startPage.html")

NINJA_THEME = os.path.join(PRJ_PATH, "addins", "theme", "ninja_dark.qss")

NINJA__THEME_CLASSIC = os.path.join(
    PRJ_PATH, "addins", "theme", "ninja_theme.qss")

NINJA_THEME_DOWNLOAD = os.path.join(HOME_NINJA_PATH, "addins", "theme")

LOG_FILE_PATH = os.path.join(HOME_NINJA_PATH, 'ninja_ide.log')

GET_SYSTEM_PATH = os.path.join(PRJ_PATH, 'tools', 'get_system_path.py')

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
# IMAGES
###############################################################################

IMAGES = {
    "splash": os.path.join(PRJ_PATH, "img", "splash.png"),
    "icon": os.path.join(PRJ_PATH, "img", "icon.png"),
    "iconUpdate": os.path.join(PRJ_PATH, "img", "icon.png"),
    "new": os.path.join(PRJ_PATH, "img", "document-new.png"),
    "newProj": os.path.join(PRJ_PATH, "img", "project-new.png"),
    "open": os.path.join(PRJ_PATH, "img", "document-open.png"),
    "openProj": os.path.join(PRJ_PATH, "img", "project-open.png"),
    "favProj": os.path.join(PRJ_PATH, "img", "favorite-project.png"),
    "unfavProj": os.path.join(PRJ_PATH, "img", "unfavorite-project.png"),
    "delProj": os.path.join(PRJ_PATH, "img", "delete-project.png"),
    "openFolder": os.path.join(PRJ_PATH, "img", "folder-open.png"),
    "save": os.path.join(PRJ_PATH, "img", "document-save.png"),
    "saveAs": os.path.join(PRJ_PATH, "img", "document-save-as.png"),
    "saveAll": os.path.join(PRJ_PATH, "img", "document-save-all.png"),
    "activate-profile": os.path.join(PRJ_PATH, "img", "activate_profile.png"),
    "deactivate-profile": os.path.join(PRJ_PATH, "img",
        "deactivate_profile.png"),
    "copy": os.path.join(PRJ_PATH, "img", "edit-copy.png"),
    "cut": os.path.join(PRJ_PATH, "img", "edit-cut.png"),
    "paste": os.path.join(PRJ_PATH, "img", "edit-paste.png"),
    "redo": os.path.join(PRJ_PATH, "img", "edit-redo.png"),
    "undo": os.path.join(PRJ_PATH, "img", "edit-undo.png"),
    "exit": os.path.join(PRJ_PATH, "img", "exit.png"),
    "find": os.path.join(PRJ_PATH, "img", "find.png"),
    "findReplace": os.path.join(PRJ_PATH, "img", "find-replace.png"),
    "locator": os.path.join(PRJ_PATH, "img", "locator.png"),
    "play": os.path.join(PRJ_PATH, "img", "play.png"),
    "stop": os.path.join(PRJ_PATH, "img", "stop.png"),
    "file-run": os.path.join(PRJ_PATH, "img", "file-run.png"),
    "preview-web": os.path.join(PRJ_PATH, "img", "preview_web.png"),
    "debug": os.path.join(PRJ_PATH, "img", "debug.png"),
    "designer": os.path.join(PRJ_PATH, "img", "qtdesigner.png"),
    "bug": os.path.join(PRJ_PATH, "img", "bug.png"),
    "function": os.path.join(PRJ_PATH, "img", "function.png"),
    "module": os.path.join(PRJ_PATH, "img", "module.png"),
    "class": os.path.join(PRJ_PATH, "img", "class.png"),
    "attribute": os.path.join(PRJ_PATH, "img", "attribute.png"),
    "web": os.path.join(PRJ_PATH, "img", "web.png"),
    "fullscreen": os.path.join(PRJ_PATH, "img", "fullscreen.png"),
    "follow": os.path.join(PRJ_PATH, "img", "follow.png"),
    "splitH": os.path.join(PRJ_PATH, "img", "split-horizontal.png"),
    "splitV": os.path.join(PRJ_PATH, "img", "split-vertical.png"),
    "zoom-in": os.path.join(PRJ_PATH, "img", "zoom_in.png"),
    "zoom-out": os.path.join(PRJ_PATH, "img", "zoom_out.png"),
    "splitCPosition": os.path.join(PRJ_PATH, "img",
                                "panels-change-position.png"),
    "splitMPosition": os.path.join(PRJ_PATH, "img",
                                "panels-change-vertical-position.png"),
    "splitCRotate": os.path.join(PRJ_PATH, "img",
                                "panels-change-orientation.png"),
    "indent-less": os.path.join(PRJ_PATH, "img", "indent-less.png"),
    "indent-more": os.path.join(PRJ_PATH, "img", "indent-more.png"),
    "go-to-definition": os.path.join(PRJ_PATH, "img", "go_to_definition.png"),
    "insert-import": os.path.join(PRJ_PATH, "img", "insert_import.png"),
    "console": os.path.join(PRJ_PATH, "img", "console.png"),
    "pref": os.path.join(PRJ_PATH, "img", "preferences-system.png"),
    "tree-app": os.path.join(PRJ_PATH, "img", "tree-app.png"),
    "tree-code": os.path.join(PRJ_PATH, "img", "tree-code.png"),
    "tree-folder": os.path.join(PRJ_PATH, "img", "tree-folder.png"),
    "tree-html": os.path.join(PRJ_PATH, "img", "tree-html.png"),
    "tree-generic": os.path.join(PRJ_PATH, "img", "tree-generic.png"),
    "tree-css": os.path.join(PRJ_PATH, "img", "tree-CSS.png"),
    "tree-python": os.path.join(PRJ_PATH, "img", "tree-python.png"),
    "tree-image": os.path.join(PRJ_PATH, "img", "tree-image.png"),
    "comment-code": os.path.join(PRJ_PATH, "img", "comment-code.png"),
    "uncomment-code": os.path.join(PRJ_PATH, "img", "uncomment-code.png"),
    "reload-file": os.path.join(PRJ_PATH, "img", "reload-file.png"),
    "print": os.path.join(PRJ_PATH, "img", "document-print.png"),
    "book-left": os.path.join(PRJ_PATH, "img", "book-left.png"),
    "book-right": os.path.join(PRJ_PATH, "img", "book-right.png"),
    "break-left": os.path.join(PRJ_PATH, "img", "break-left.png"),
    "break-right": os.path.join(PRJ_PATH, "img", "break-right.png"),
    "nav-code-left": os.path.join(PRJ_PATH, "img", "nav-code-left.png"),
    "nav-code-right": os.path.join(PRJ_PATH, "img", "nav-code-right.png"),
    "locate-file": os.path.join(PRJ_PATH, "img", "locate-file.png"),
    "locate-class": os.path.join(PRJ_PATH, "img", "locate-class.png"),
    "locate-function": os.path.join(PRJ_PATH, "img", "locate-function.png"),
    "locate-attributes": os.path.join(PRJ_PATH, "img",
        "locate-attributes.png"),
    "locate-nonpython": os.path.join(PRJ_PATH, "img", "locate-nonpython.png"),
    "locate-on-this-file": os.path.join(PRJ_PATH, "img",
        "locate-on-this-file.png"),
    "locate-tab": os.path.join(PRJ_PATH, "img", "locate-tab.png"),
    "locate-line": os.path.join(PRJ_PATH, "img", "locate-line.png"),
    "add": os.path.join(PRJ_PATH, "img", "add.png"),
    "delete": os.path.join(PRJ_PATH, "img", "delete.png"),
    "loading": os.path.join(PRJ_PATH, "img", "loading.gif"),
    "separator": os.path.join(PRJ_PATH, "img", "separator.png")}


###############################################################################
# COLOR SCHEMES
###############################################################################

COLOR_SCHEME = {
    "keyword": "#6EC7D7",
    "operator": "#FFFFFF",
    "brace": "#FFFFFF",
    "definition": "#F6EC2A",
    "string": "#B369BF",
    "string2": "#86d986",
    "comment": "#80FF80",
    "properObject": "#6EC7D7",
    "numbers": "#F8A008",
    "spaces": "#7b7b7b",
    "extras": "#ee8859",
    "editor-background": "#1E1E1E",
    "editor-selection-color": "#FFFFFF",
    "editor-selection-background": "#437DCD",
    "editor-text": "#B3BFA7",
    "current-line": "#858585",
    "selected-word": "red",
    "pending": "red",
    "selected-word-background": "#009B00",
    "fold-area": "#FFFFFF",
    "fold-arrow": "#454545",
    "linkNavigate": "orange",
    "brace-background": "#5BC85B",
    "brace-foreground": "red",
    "error-underline": "red",
    "pep8-underline": "yellow",
    "sidebar-background": "#c4c4c4",
    "sidebar-foreground": "black",
    "locator-name": "white",
    "locator-name-selected": "black",
    "locator-path": "gray",
    "locator-path-selected": "white",
    "migration-underline": "blue",
    "current-line-opacity": 20,
    "error-background-opacity": 60,
}

CUSTOM_SCHEME = {}


###############################################################################
# SHORTCUTS
###############################################################################

#default shortcuts
SHORTCUTS = {
    "Duplicate": QKeySequence(Qt.CTRL + Qt.Key_R),  # Replicate
    "Remove-line": QKeySequence(Qt.CTRL + Qt.Key_E),  # Eliminate
    "Move-up": QKeySequence(Qt.ALT + Qt.Key_Up),
    "Move-down": QKeySequence(Qt.ALT + Qt.Key_Down),
    "Close-tab": QKeySequence(Qt.CTRL + Qt.Key_W),
    "New-file": QKeySequence(Qt.CTRL + Qt.Key_N),
    "New-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_N),
    "Open-file": QKeySequence(Qt.CTRL + Qt.Key_O),
    "Open-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_O),
    "Save-file": QKeySequence(Qt.CTRL + Qt.Key_S),
    "Save-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S),
    "Print-file": QKeySequence(Qt.CTRL + Qt.Key_P),
    "Redo": QKeySequence(Qt.CTRL + Qt.Key_Y),
    "Comment": QKeySequence(Qt.CTRL + Qt.Key_D),
    "Uncomment": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_D),
    "Horizontal-line": QKeySequence(),
    "Title-comment": QKeySequence(),
    "Indent-less": QKeySequence(Qt.SHIFT + Qt.Key_Tab),
    "Hide-misc": QKeySequence(Qt.Key_F4),
    "Hide-editor": QKeySequence(Qt.Key_F3),
    "Hide-explorer": QKeySequence(Qt.Key_F2),
    "Run-file": QKeySequence(Qt.CTRL + Qt.Key_F6),
    "Run-project": QKeySequence(Qt.Key_F6),
    "Debug": QKeySequence(Qt.Key_F7),
    "Switch-Focus": QKeySequence(Qt.CTRL + Qt.Key_QuoteLeft),
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
    "Split-vertical": QKeySequence(Qt.Key_F10),
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
    "Show-Code-Nav": QKeySequence(Qt.CTRL + Qt.Key_1),
    "Show-Paste-History": QKeySequence(Qt.CTRL + Qt.Key_4),
    "History-Copy": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_C),
    "History-Paste": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_V),
    "Add-Bookmark-or-Breakpoint": QKeySequence(Qt.CTRL + Qt.Key_B),
    "change-split-focus": QKeySequence(Qt.CTRL + Qt.Key_Tab),
    "move-tab-to-next-split": QKeySequence(Qt.SHIFT + Qt.Key_F10),
    "change-tab-visibility": QKeySequence(Qt.SHIFT + Qt.Key_F1),
    "Highlight-Word": QKeySequence(Qt.CTRL + Qt.Key_Down)}

CUSTOM_SHORTCUTS = {}

###############################################################################
# FUNCTIONS
###############################################################################


def load_shortcuts():
    """
    Loads the shortcuts from QSettings
    """
    global SHORTCUTS
    global CUSTOM_SHORTCUTS
    settings = QSettings()
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
    global SHORTCUTS
    global CUSTOM_SHORTCUTS
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
    for d in (HOME_NINJA_PATH, ADDINS, PLUGINS, EDITOR_SKINS,
              LANGS_DOWNLOAD, NINJA_THEME_DOWNLOAD):
        if not os.path.isdir(d):
            os.mkdir(d)
