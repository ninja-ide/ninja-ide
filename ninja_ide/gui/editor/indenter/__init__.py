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

from ninja_ide.gui.editor.indenter import (
    python_indenter,
    html_indenter,
    base
)

INDENTER_MAP = {
    'python': python_indenter.PythonIndenter,
    'html': html_indenter.HtmlIndenter
}


def load_indenter(editor, lang=None):
    indenter_obj = INDENTER_MAP.get(lang, base.BasicIndenter)
    return indenter_obj(editor)
