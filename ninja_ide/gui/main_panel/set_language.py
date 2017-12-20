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
from ninja_ide.gui.editor import syntaxhighlighter as SH


class SetLanguageFile(object):
    def set_language_to_editor(self, lang):
        self.mc = IDE.get_service("main_container")
        self._current_editor_widget = self.mc.get_current_editor()
        self._current_editor_widget.register_syntax_for(lang)
        # self._current_editor_widget.register_syntax_for(
        #    self.dict_language[index])

    def get_list_of_language(self):
        return SH.SYNTAXES.keys()

    def get_lang(self, extension):
        if not extension:
            extension = "py"
        return SH.LANGUAGE_MAP.get(extension, "")

    def set_language_from_extension(self, ext):
        self.mc = IDE.get_service("main_container")
        self._current_editor_widget = self.mc.get_current_editor()
        self._current_editor_widget.register_syntax_for(
            self.get_lang(ext))
