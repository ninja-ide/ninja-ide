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

from ninja_ide.gui.editor.extended_lexers.all_lexers import (
    PythonLexer, AVSLexer, BashLexer, BatchLexer, CMakeLexer,
    CPPLexer, CSSLexer, CSharpLexer, CoffeeScriptLexer, DLexer, DiffLexer,
    FortranLexer, Fortran77Lexer, HTMLLexer, IDLLexer, JavaLexer,
    JavaScriptLexer, LuaLexer, MakefileLexer, MatlabLexer, OctaveLexer, POLexer,
    POVLexer, PascalLexer, PerlLexer, PostScriptLexer, PropertiesLexer,
    RubyLexer, SQLLexer, SpiceLexer, TCLLexer, TeXLexer, VHDLLexer,
    VerilogLexer, XMLLexer, YAMLLexer)

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.gui.editor.highlighter')


LEXERS = {
    "python": PythonLexer,
    "avs": AVSLexer,
    "bash": BashLexer,
    "batch": BatchLexer,
    "cmake": CMakeLexer,
    "cpp": CPPLexer,
    "css": CSSLexer,
    "csharp": CSharpLexer,
    "coffeescript": CoffeeScriptLexer,
    "d": DLexer,
    "diff": DiffLexer,
    "fortran": FortranLexer,
    "fortran77": Fortran77Lexer,
    "html": HTMLLexer,
    "idl": IDLLexer,
    "java": JavaLexer,
    "javascript": JavaScriptLexer,
    "lua": LuaLexer,
    "makefile": MakefileLexer,
    "matlab": MatlabLexer,
    "octave": OctaveLexer,
    "po": POLexer,
    "pov": POVLexer,
    "pascal": PascalLexer,
    "perl": PerlLexer,
    "postscript": PostScriptLexer,
    "properties": PropertiesLexer,
    "ruby": RubyLexer,
    "sql": SQLLexer,
    "spice": SpiceLexer,
    "tcl": TCLLexer,
    "tex": TeXLexer,
    "vhdl": VHDLLexer,
    "verilog": VerilogLexer,
    "xml": XMLLexer,
    "yaml": YAMLLexer,
}

LEXER_MAP = {
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

BUILT_LEXERS = {
}


def get_lang(extension):
    if not extension:
        extension = "py"
    return LEXER_MAP.get(extension, "")


def get_lexer(extension="py"):
    return build_lexer(get_lang(extension))


def build_lexer(lang):
    global BUILT_LEXERS
    Lexer = BUILT_LEXERS.get(lang, None)

    if Lexer is None:
        Lexer = LEXERS.get(lang, None)
        if Lexer is not None:
            lex = Lexer()
            lex.initialize_color_scheme()
            BUILT_LEXERS[lang] = lex
            return lex
    return Lexer