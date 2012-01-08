#-*- coding: utf-8 -*-

from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import Qt

import os
import sys


###############################################################################
# PATHS
###############################################################################

try:
    # ...works on at least windows and linux.
    # In windows it points to the user"s folder
    #  (the one directly under Documents and Settings, not My Documents)

    # In windows, you can choose to care about local versus roaming profiles.
    # You can fetch the current user"s through PyWin32.
    #
    # For example, to ask for the roaming "Application Data" directory:
    # CSIDL_APPDATA asks for the roaming, CSIDL_LOCAL_APPDATA for the local one
    from win32com.shell import shellcon, shell
    HOME_PATH = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
except ImportError:
   # quick semi-nasty fallback for non-windows/win32com case
    HOME_PATH = os.path.expanduser("~")


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

LOG_FILE_PATH = os.path.join(HOME_NINJA_PATH, 'ninja_ide.log')

###############################################################################
# URLS
###############################################################################

BUGS_PAGE = "https://github.com/ninja-ide/ninja-ide/issues"

PLUGINS_DOC = "http://code.google.com/p/ninja-ide/wiki/New_Plugins_API"

UPDATES_URL = 'http://ninja-ide.org/updates'

SCHEMES_URL = 'http://ninja-ide.org/plugins/schemes'

LANGUAGES_URL = 'http://ninja-ide.org/plugins/languages'

PLUGINS_WEB = 'http://ninja-ide.org/plugins/official'

PLUGINS_COMMUNITY = 'http://ninja-ide.org/plugins/community'


###############################################################################
# IMAGES
###############################################################################

IMAGES = {
    "splash": os.path.join(PRJ_PATH, "img", "splash.jpg"),
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
    "tree-java": os.path.join(PRJ_PATH, "img", "tree-java.png"),
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
    "add": os.path.join(PRJ_PATH, "img", "add.png"),
    "delete": os.path.join(PRJ_PATH, "img", "delete.png"),
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
    "string2": "#80FF80",
    "comment": "#80FF80",
    "properObject": "#6EC7D7",
    "numbers": "#F8A008",
    "spaces": "#7b7b7b",
    "extras": "orange",
    "editor-background": "#1E1E1E",
    "editor-selection-color": "#FFFFFF",
    "editor-selection-background": "#437DCD",
    "editor-text": "#B3BFA7",
    "current-line": "#858585",
    "selected-word": "#009B00",
    "fold-area": "#FFFFFF",
    "fold-arrow": "#454545",
    "linkNavigate": "orange",
    "brace-background": "#5BC85B",
    "brace-foreground": "red",
    "error-underline": "red",
    "pep8-underline": "yellow"}

CUSTOM_SCHEME = {}


###############################################################################
# SHORTCUTS
###############################################################################

#default shortcuts
SHORTCUTS = {
    "Duplicate": QKeySequence(Qt.CTRL + Qt.Key_E),
    "Remove-line": QKeySequence(Qt.CTRL + Qt.Key_Q),
    "Move-up": QKeySequence(Qt.ALT + Qt.Key_Up),
    "Move-down": QKeySequence(Qt.ALT + Qt.Key_Down),
    "Close-tab": QKeySequence(Qt.CTRL + Qt.Key_W),
    "New-file": QKeySequence(Qt.CTRL + Qt.Key_N),
    "New-project": QKeySequence(Qt.CTRL + Qt.Key_M),
    "Open-file": QKeySequence(Qt.CTRL + Qt.Key_O),
    "Open-project": QKeySequence(Qt.CTRL + Qt.Key_P),
    "Save-file": QKeySequence(Qt.CTRL + Qt.Key_S),
    "Save-project": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S),
    "Print-file": QKeySequence(Qt.CTRL + Qt.Key_I),
    "Redo": QKeySequence(Qt.CTRL + Qt.Key_Y),
    "Comment": QKeySequence(Qt.CTRL + Qt.Key_D),
    "Horizontal-line": QKeySequence(Qt.CTRL + Qt.Key_R),
    "Title-comment": QKeySequence(Qt.CTRL + Qt.Key_T),
    "Indent-less": QKeySequence(Qt.SHIFT + Qt.Key_Tab),
    "Hide-misc": QKeySequence(Qt.Key_F4),
    "Hide-editor": QKeySequence(Qt.Key_F3),
    "Hide-explorer": QKeySequence(Qt.Key_F2),
    "Run-file": QKeySequence(Qt.CTRL + Qt.Key_F6),
    "Run-project": QKeySequence(Qt.Key_F6),
    "Debug": QKeySequence(Qt.Key_F7),
    "Stop-execution": QKeySequence(Qt.CTRL + Qt.Key_F5),
    "Hide-all": QKeySequence(Qt.Key_F11),
    "Full-screen": QKeySequence(Qt.CTRL + Qt.Key_F11),
    "Find": QKeySequence(Qt.CTRL + Qt.Key_F),
    "Find-replace": QKeySequence(Qt.CTRL + Qt.Key_H),
    "Find-with-word": QKeySequence(Qt.CTRL + Qt.Key_G),
    "Help": QKeySequence(Qt.Key_F1),
    "Split-horizontal": QKeySequence(Qt.Key_F10),
    "Split-vertical": QKeySequence(Qt.Key_F9),
    "Follow-mode": QKeySequence(Qt.CTRL + Qt.Key_F10),
    "Reload-file": QKeySequence(Qt.Key_F5),
    "Jump": QKeySequence(Qt.CTRL + Qt.Key_J),
    "Find-in-files": QKeySequence(Qt.CTRL + Qt.Key_L),
    "Import": QKeySequence(Qt.CTRL + Qt.Key_U),
    "Go-to-definition": QKeySequence(Qt.CTRL + Qt.Key_Return),
    "Code-locator": QKeySequence(Qt.CTRL + Qt.Key_K),
    "File-Opener": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_O),
    "Navigate-back": QKeySequence(Qt.ALT + Qt.Key_Left),
    "Navigate-forward": QKeySequence(Qt.ALT + Qt.Key_Right),
    "Open-recent-closed": QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_N),
    "Change-Tab": QKeySequence(Qt.CTRL + Qt.Key_Tab),
    "Change-Tab-Reverse": QKeySequence(Qt.CTRL + Qt.Key_Shift + Qt.Key_Tab),
    "Show-Code-Nav": QKeySequence(Qt.CTRL + Qt.Key_1),
    "Show-Bookmarks-Nav": QKeySequence(Qt.CTRL + Qt.Key_2),
    "Show-Breakpoints-Nav": QKeySequence(Qt.CTRL + Qt.Key_3),
    "Show-Paste-History": QKeySequence(Qt.CTRL + Qt.Key_4),
    "History-Copy": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_C),
    "History-Paste": QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_V),
    "Add-Bookmark-or-Breakpoint": QKeySequence(Qt.CTRL + Qt.Key_B)}

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
            default_action).toString()
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


def create_home_dir_structure():
    """
    Create the necesary directories structure for NINJA-IDE
    """
    for d in (HOME_NINJA_PATH, ADDINS, PLUGINS, EDITOR_SKINS, LANGS_DOWNLOAD):
        if not os.path.isdir(d):
            os.mkdir(d)
