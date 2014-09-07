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

from PyQt4.Qsci import QsciLexerPython


class PythonLexer(QsciLexerPython):

    def __init__(self, *args, **kwargs):
        super(PythonLexer, self).__init__(*args, **kwargs)
        self.setFoldComments(True)
        self.setFoldQuotes(True)

    def keywords(self, keyset):
        if keyset == 2:
            return (b'self super all any basestring bin bool bytearray callable '
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
