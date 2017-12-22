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

<<<<<<< HEAD
# FIXME: Maybe we need to improve this module
=======
>>>>>>> 1e75c2f2... esto debo squash
import os
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import (
    QColor,
    QPalette
)
from PyQt5.QtCore import Qt
from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools.logger import NinjaLogger
# Logger
logger = NinjaLogger(__name__)


THEMES_DIRS = (
    resources.NINJA_THEMES,
    resources.NINJA_THEMES_DOWNLOAD
)
<<<<<<< HEAD
# All colors defined in the theme, included the palette
COLORS = {}
# Some flags
FLAGS = {}
# Editor scheme recomended by the theme
=======
COLORS = {}
FLAGS = {}
>>>>>>> 1e75c2f2... esto debo squash
DEFAULT_EDITOR_SCHEME = ""


def get_color(role):
    return COLORS.get(role)


<<<<<<< HEAD
def get_colors():
    return COLORS


=======
>>>>>>> 1e75c2f2... esto debo squash
def flag(name):
    return FLAGS.get(name)


def load_theme(name):
    theme_data = available_themes()[name]
    FLAGS = theme_data.get("flags")
<<<<<<< HEAD
    global DEFAULT_EDITOR_SCHEME
    DEFAULT_EDITOR_SCHEME = theme_data.get("editor-theme")
=======
    DEFUALT_EDITOR_SCHEME = theme_data.get("editor-theme")
>>>>>>> 1e75c2f2... esto debo squash
    colors = theme_data.get("colors")
    palette = theme_data.get("palette")
    # Create colors
    for role, color in colors.items():
        qcolor = QColor(color)
        if not qcolor.isValid():
            logger.warning(
                    "The color '%s' for '%s' is not valid" % (color, role))
            # If color is invalid, set white
            qcolor = QColor(Qt.white)
        COLORS[role] = qcolor
<<<<<<< HEAD
    qpalette = QApplication.palette()
=======
    palette = QApplication.palette()
>>>>>>> 1e75c2f2... esto debo squash
    if FLAGS["PaletteFromTheme"]:
        for role, color in palette.items():
            qcolor = QColor(color)
            color_group = QPalette.All
            if role.endswith("Disabled"):
                role = role.split("Disabled")[0]
                color_group = QPalette.Disabled
<<<<<<< HEAD
            color_role = getattr(qpalette, role)
            qpalette.setBrush(color_group, color_role, qcolor)
            COLORS[role] = qcolor
    QApplication.setPalette(qpalette)
=======
            color_role = get_color(palette, role)
            palette.setBrush(color_group, color_role, qcolor)
    QApplication.setPalette(palette)
>>>>>>> 1e75c2f2... esto debo squash


def available_themes():
    themes = {}
    for theme_dir in THEMES_DIRS:
        files = file_manager.get_files_from_folder(theme_dir, '.ninjatheme')
        if files:
            for theme_file in files:
                filename = os.path.join(theme_dir, theme_file)
                with open(filename) as json_f:
                    content = json.load(json_f)
                    theme_name = content["name"]
                    themes[theme_name] = content
    return themes


def available_theme_names():
    themes = available_themes()
    return themes.keys()
