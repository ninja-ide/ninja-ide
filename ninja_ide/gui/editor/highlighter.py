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
# based on Python Syntax highlighting from:
# http://diotavelli.net/PyQtWiki/Python%20syntax%20highlighting
from __future__ import absolute_import

import re

from PyQt4.QtGui import QColor
#from PyQt4.Qsci import QsciLexerPython

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.editor.extended_lexers.python_lexer import PythonLexer


pattern = re.compile(r'^([A-Z]).+$')

LEXERS = {
    "python": PythonLexer,
}


def __initialize_color_scheme(self):
    self.scheme = {}
    self.background_color = QColor(resources.COLOR_SCHEME["EditorBackground"])
    detected_values = []
    identifiers = [word for word in dir(self) if pattern.match(word)]
    for key in identifiers:
        identifier = getattr(self, key)
        if identifier not in detected_values:
            color = resources.COLOR_SCHEME.get(
                key, resources.COLOR_SCHEME["Default"])
            if color != resources.COLOR_SCHEME["Default"]:
                detected_values.append(identifier)
            self.scheme[identifier] = QColor(color)


def __custom_default_color(self, style):
    return self.scheme.get(style, QColor(resources.COLOR_SCHEME["Default"]))


def __custom_default_font(self, style):
    return settings.FONT


def __custom_default_paper(self, style):
    return self.background_color


def build_lexer(lang):
    BaseLexer = LEXERS.get(lang, None)
    Lexer = None
    if BaseLexer is not None:
        Lexer = type('Lexer', (BaseLexer,),
                     {'defaultColor': __custom_default_color,
                      'initialize_color_scheme': __initialize_color_scheme,
                      'defaultFont': __custom_default_font,
                      'defaultPaper': __custom_default_paper})
    if Lexer is not None:
        lex = Lexer()
        lex.initialize_color_scheme()
        return lex
    return None