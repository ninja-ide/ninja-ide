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
from ninja_ide.gui.ide import IDE


class _SyntaxRegistry(object):

    def __init__(self):
        self.__syntaxes = {}
        super(_SyntaxRegistry, self).__init__()
        IDE.register_service('syntax_registry', self)

    def register_syntax(self, name, syntax):
        self.__syntaxes[name] = syntax

    def get_syntax_for(self, name):
        return self.__syntaxes.get(name, None)


syntax_registry = _SyntaxRegistry()
