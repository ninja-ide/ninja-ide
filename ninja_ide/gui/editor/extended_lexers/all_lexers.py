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

from ninja_ide import resources
from ninja_ide.core import settings

from PyQt4.Qsci import (QsciLexerBash, QsciLexerBatch,
                        QsciLexerCMake, QsciLexerCPP, QsciLexerCSS,
                        QsciLexerCSharp,
                        QsciLexerD, QsciLexerDiff, QsciLexerFortran,
                        QsciLexerFortran77, QsciLexerHTML, QsciLexerIDL,
                        QsciLexerJava, QsciLexerJavaScript, QsciLexerLua,
                        QsciLexerMakefile, QsciLexerMatlab, QsciLexerOctave,
                        QsciLexerPOV, QsciLexerPascal,
                        QsciLexerPerl, QsciLexerPostScript, QsciLexerProperties,
                        QsciLexerPython, QsciLexerRuby, QsciLexerSQL,
                        QsciLexerSpice, QsciLexerTCL, QsciLexerTeX,
                        QsciLexerVHDL, QsciLexerVerilog, QsciLexerXML,
                        QsciLexerYAML)

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.gui.editor.extended_lexers.all_lexers')

pattern = re.compile(r'^([A-Z]).+$')


class BaseNinjaLexer(object):
    """WARNING: Only use this as the first part of a Lexer mixin"""

    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(BaseNinjaLexer, self).__init__(*args, **kwargs)

    def initialize_color_scheme(self):
        self.scheme = {}
        self.background_color = QColor(resources.COLOR_SCHEME["EditorBackground"])
        detected_values = []
        identifiers = [word for word in dir(self) if pattern.match(word)]
        logger.debug(identifiers)
        default_color = resources.COLOR_SCHEME["Default"]
        for key in identifiers:
            identifier = getattr(self, key)
            if identifier not in detected_values:
                color = resources.COLOR_SCHEME.get(key, default_color)

                if color != default_color:
                    detected_values.append(identifier)

                self.scheme[identifier] = QColor(color)

    def defaultColor(self, style):
        if self._settings_colored is not None:
            default_color = QColor(resources.COLOR_SCHEME["Default"])
            return self.scheme.get(style, default_color)

        parent_lexer = None
        not_lexers = [self.__class__.__name__, "BaseNinjaLexer"]
        for each_parent in self.__class__.__mro__:
            if each_parent.__name__ not in not_lexers:
                parent_lexer = each_parent
                break

        #FIXME This reverses colors while we find a way to do themes.
        c = parent_lexer.defaultColor(self, style).name()
        logger.debug(c)
        reverse_color = "#" + "".join((hex(255 - int(x, 16)))[2:].zfill(2) for x in (c[1:3], c[3:5], c[5:7]))
        return QColor(reverse_color)

    def defaultFont(self, style):
        return settings.FONT

    def defaultPaper(self, style):
        return self.background_color


class PythonLexer(BaseNinjaLexer, QsciLexerPython):

    def __init__(self, *args, **kwargs):
        super(PythonLexer, self).__init__(*args, **kwargs)
        self._settings_colored = 1
        self.setFoldComments(True)
        self.setFoldQuotes(True)

    def keywords(self, keyset):
        if keyset == 2:
            return ('self super all any basestring bin bool bytearray callable '
                    'chr abs classmethod cmp compile complex delattr dict dir '
                    'divmod enumerate eval execfile file filter float format '
                    'frozenset getattr globals hasattr hash help hex id input '
                    'int isinstance issubclass iter len list locals long map '
                    'max memoryview min next object oct open ord pow property '
                    'range raw_input reduce reload repr reversed round set '
                    'setattr slice sorted staticmethod str sum tuple type '
                    'unichr unicode vars xrange zip apply buffer coerce intern '
                    'True False')
        return super(PythonLexer, self).keywords(keyset)


try:
    from PyQt4.Qsci import QsciLexerAVS
    class AVSLexer(BaseNinjaLexer, QsciLexerAVS):
        def __init__(self, *args, **kwargs):
            self._settings_colored = None
            super(AVSLexer, self).__init__(*args, **kwargs)
except ImportError:
    AVSLexer = None

class BashLexer (BaseNinjaLexer, QsciLexerBash):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(BashLexer, self).__init__(*args, **kwargs)


class BatchLexer (BaseNinjaLexer, QsciLexerBatch):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(BatchLexer, self).__init__(*args, **kwargs)


class CMakeLexer (BaseNinjaLexer, QsciLexerCMake):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(CMakeLexer, self).__init__(*args, **kwargs)


class CPPLexer (BaseNinjaLexer, QsciLexerCPP):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(CPPLexer, self).__init__(*args, **kwargs)


class CSSLexer (BaseNinjaLexer, QsciLexerCSS):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(CSSLexer, self).__init__(*args, **kwargs)


class CSharpLexer (BaseNinjaLexer, QsciLexerCSharp):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(CSharpLexer, self).__init__(*args, **kwargs)

try:
    from PyQt4.Qsci import QsciLexerCoffeeScript
    class CoffeeScriptLexer (BaseNinjaLexer, QsciLexerCoffeeScript):
        def __init__(self, *args, **kwargs):
            self._settings_colored = None
            super(CoffeeScriptLexer, self).__init__(*args, **kwargs)
except ImportError:
    CoffeeScriptLexer = None

class DLexer (BaseNinjaLexer, QsciLexerD):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(DLexer, self).__init__(*args, **kwargs)


class DiffLexer (BaseNinjaLexer, QsciLexerDiff):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(DiffLexer, self).__init__(*args, **kwargs)


class FortranLexer (BaseNinjaLexer, QsciLexerFortran):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(FortranLexer, self).__init__(*args, **kwargs)


class Fortran77Lexer (BaseNinjaLexer, QsciLexerFortran77):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(Fortran77Lexer, self).__init__(*args, **kwargs)


class HTMLLexer (BaseNinjaLexer, QsciLexerHTML):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(HTMLLexer, self).__init__(*args, **kwargs)


class IDLLexer (BaseNinjaLexer, QsciLexerIDL):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(IDLLexer, self).__init__(*args, **kwargs)


class JavaLexer (BaseNinjaLexer, QsciLexerJava):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(JavaLexer, self).__init__(*args, **kwargs)


class JavaScriptLexer (BaseNinjaLexer, QsciLexerJavaScript):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(JavaScriptLexer, self).__init__(*args, **kwargs)


class LuaLexer (BaseNinjaLexer, QsciLexerLua):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(LuaLexer, self).__init__(*args, **kwargs)


class MakefileLexer (BaseNinjaLexer, QsciLexerMakefile):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(MakefileLexer, self).__init__(*args, **kwargs)


class MatlabLexer (BaseNinjaLexer, QsciLexerMatlab):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(MatlabLexer, self).__init__(*args, **kwargs)


class OctaveLexer (BaseNinjaLexer, QsciLexerOctave):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(OctaveLexer, self).__init__(*args, **kwargs)


try:
    from PyQt4.Qsci import QsciLexerPO
    class POLexer (BaseNinjaLexer, QsciLexerPO):
        def __init__(self, *args, **kwargs):
            self._settings_colored = None
            super(POLexer, self).__init__(*args, **kwargs)
except ImportError:
    POLexer = None

class POVLexer (BaseNinjaLexer, QsciLexerPOV):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(POVLexer, self).__init__(*args, **kwargs)


class PascalLexer (BaseNinjaLexer, QsciLexerPascal):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(PascalLexer, self).__init__(*args, **kwargs)


class PerlLexer (BaseNinjaLexer, QsciLexerPerl):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(PerlLexer, self).__init__(*args, **kwargs)


class PostScriptLexer (BaseNinjaLexer, QsciLexerPostScript):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(PostScriptLexer, self).__init__(*args, **kwargs)


class PropertiesLexer (BaseNinjaLexer, QsciLexerProperties):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(PropertiesLexer, self).__init__(*args, **kwargs)


class RubyLexer (BaseNinjaLexer, QsciLexerRuby):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(RubyLexer, self).__init__(*args, **kwargs)


class SQLLexer (BaseNinjaLexer, QsciLexerSQL):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(SQLLexer, self).__init__(*args, **kwargs)


class SpiceLexer (BaseNinjaLexer, QsciLexerSpice):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(SpiceLexer, self).__init__(*args, **kwargs)


class TCLLexer (BaseNinjaLexer, QsciLexerTCL):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(TCLLexer, self).__init__(*args, **kwargs)


class TeXLexer (BaseNinjaLexer, QsciLexerTeX):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(TeXLexer, self).__init__(*args, **kwargs)


class VHDLLexer (BaseNinjaLexer, QsciLexerVHDL):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(VHDLLexer, self).__init__(*args, **kwargs)


class VerilogLexer (BaseNinjaLexer, QsciLexerVerilog):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(VerilogLexer, self).__init__(*args, **kwargs)


class XMLLexer (BaseNinjaLexer, QsciLexerXML):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(XMLLexer, self).__init__(*args, **kwargs)


class YAMLLexer (BaseNinjaLexer, QsciLexerYAML):
    def __init__(self, *args, **kwargs):
        self._settings_colored = None
        super(YAMLLexer, self).__init__(*args, **kwargs)
