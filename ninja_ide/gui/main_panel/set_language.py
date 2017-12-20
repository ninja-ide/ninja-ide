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

from ninja_ide.gui.ide import IDE


class SetLanguageFile(object):
    def __init__(self):
        self.dict_language = {
            0: None,  # This is the default value, maybe need some work
            1: 'python',
            # 2: 'HTML',
            # 3: 'js',
            # 4: 'qml'
        }
        self.LEXER_MAP = {
            "asm": "assembler",
            "json": "json",
            "cs": "csharp",
            "rb": "ruby_on_rails",
            "cpp": "cpp",
            "coffee": "coffeescript",
            "tex": "bibtex",
            "js": "javascript",
            "qml": "javascript",
            "mo": "gettext",
            "po": "gettext",
            "pot": "gettext",
            "v": "verilog",
            "sh": "shell",
            "shell": "shell",
            "bash": "shell",
            "ksh": "shell",
            "pas": "pascal",
            "html": "html",
            "list": "sourceslist",
            "lol": "lolcode",
            "h": "header",
            "conf": "apache",
            "php": "php",
            "php4": "php",
            "php5": "php",
            "css": "css",
            "qss": "css",
            "scss": "css",
            "sass": "css",
            "tex": "latex",
            "py": "python",
            "pyw": "python",
            "rpy": "python",
            "tac": "python",
            "pyx": "cython",
            "pxd": "cython",
            "pxi": "cython",
            "go": "go",
            "asp": "asp",
            "rst": "rst",
            "c": "c",
            "java": "java",
        }

    def set_language_to_editor(self, lang):
        self.mc = IDE.get_service("main_container")
        self._current_editor_widget = self.mc.get_current_editor()
        self._current_editor_widget.register_syntax_for(lang)
        # self._current_editor_widget.register_syntax_for(
        #    self.dict_language[index])

    def get_list_of_language(self):
        return self.dict_language.values()

    def get_lang(self, extension):
        if not extension:
            extension = "py"
        return self.LEXER_MAP.get(extension, "")

    def set_language_from_extension(self, ext):
        self.mc = IDE.get_service("main_container")
        self._current_editor_widget = self.mc.get_current_editor()
        self._current_editor_widget.register_syntax_for(
            self.get_lang(ext))
