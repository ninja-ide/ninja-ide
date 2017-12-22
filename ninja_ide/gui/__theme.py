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

# import yaml
import json
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import (
    QPalette,
    QColor
)
from PyQt5.QtCore import QObject, Qt
from ninja_ide.gui.ide import IDE
from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools.logger import NinjaLogger
# Logger
logger = NinjaLogger(__name__)

PALETTE = {}


class ThemeManager(object):

    __THEMES = {}

    @classmethod
    def discover_themes(cls):
        dirs = (
            resources.NINJA_THEMES,
            resources.NINJA_THEMES_DOWNLOAD
        )
        for dir_ in dirs:
            themes = file_manager.get_files_from_folder(dir_, '.ninjatheme')
            if themes:
                for theme_file in themes:

                    with open(os.path.join(dir_, theme_file)) as json_f:
                        theme_content = json.load(json_f)
                        theme_name = theme_content["name"]
                        ninja_theme = NTheme(theme_content)
                        cls.__THEMES[theme_name] = ninja_theme

    @classmethod
    def load(cls, theme_name):
        ninja_theme = cls.__THEMES.get(theme_name)
        ninja_theme.initialize_colors()
        palette = ninja_theme.get_palette()
        QApplication.setPalette(palette)


class _ThemeManager(QObject):

    def __init__(self):
        QObject.__init__(self)
        self._themes_dir = (
            resources.NINJA_THEMES,
            resources.NINJA_THEMES_DOWNLOAD
        )
        self.__themes = {}
        IDE.register_service("theme_manager", self)

    def discover_themes(self):
        for dir_ in self._themes_dir:
            themes = file_manager.get_files_from_folder(dir_, '.ninjatheme')
            if themes:
                for theme in sorted(themes):
                    theme_filename = os.path.join(dir_, theme)
                    with open(theme_filename) as json_f:
                        theme_content = json.load(json_f)
                        theme_name = theme_content['name']
                        ninja_theme = NTheme(theme_content)
                        self.__themes[theme_name] = ninja_theme

    def load(self, theme_name):
        theme = self.__themes[theme_name]
        pal = theme.get_palette()
        theme.initialize_colors()
        QApplication.setPalette(pal)


class NTheme(object):

    __COLORS = {}
    __FLAGS = {}

    def __init__(self, theme_content_dict):
        self.name = theme_content_dict['name']
        self.palette = theme_content_dict['palette']
        self.colors = theme_content_dict['colors']
        self._flags = theme_content_dict['flags']
        self._derive_palette_from_theme = self._flags['PaletteFromTheme']
        self.editor = theme_content_dict['editor-theme']

    def original_palette(self):
        """Return the original palette"""

        palette = QApplication.palette()
        return palette

    def initialize_colors(self):
        for role, color in self.colors.items():
            qcolor = QColor(color)
            if not qcolor.isValid():
                logger.warning(
                    "The color '%s' for '%s' is not valid" % (color, role))
                qcolor = QColor(Qt.white)
            self.__COLORS[role] = qcolor
        # initialize flags
        for flag_name, flag in self._flags.items():
            self.__FLAGS[flag_name] = flag

    @classmethod
    def get_color(cls, role):
        return cls.__COLORS.get(role)

    @classmethod
    def get_colors(cls):
        return cls.__COLORS

    @classmethod
    def flag(cls, name):
        return cls.__FLAGS[name]

    def get_palette(self):
        palette = self.original_palette()
        if not self._derive_palette_from_theme:
            return palette
        for role, color in self.palette.items():
            qcolor = QColor(color)
            color_group = QPalette.All
            if role.endswith('Disabled'):
                role = role.split('Disabled')[0]
                color_group = QPalette.Disabled
            color_role = getattr(palette, role, None)
            palette.setBrush(color_group, color_role, qcolor)
            PALETTE[role] = color
        return palette


# ThemeManager()
