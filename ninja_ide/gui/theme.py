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
from PyQt5.QtCore import QObject
from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager

PALETTE = {}


class ThemeManager(QObject):

    def __init__(self):
        QObject.__init__(self)
        self._themes_dir = (
            resources.NINJA_THEMES,
            resources.NINJA_THEMES_DOWNLOAD
        )
        self.__themes = {}

    def discover_themes(self):
        for dir_ in self._themes_dir:
            themes = file_manager.get_files_from_folder(dir_, '.ninjatheme')
            if themes:
                for theme in themes:
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

    def __init__(self, theme_content_dict):
        self.name = theme_content_dict['name']
        self.palette = theme_content_dict['palette']
        self.colors = theme_content_dict['colors']
        self._flags = theme_content_dict['flags']
        self._derive_palette_from_theme = self._flags['PaletteFromTheme']

    def initialize_colors(self):
        for role, color in self.colors.items():
            self.__COLORS[role] = QColor(color)

    @classmethod
    def get_color(cls, role):
        return cls.__COLORS.get(role)

    @classmethod
    def get_colors(cls):
        return cls.__COLORS

    def get_palette(self):
        if not self._derive_palette_from_theme:
            return QApplication.palette()
        palette = QPalette()
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
