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


# Symbols handler per language
SYMBOLS_HANDLER = {}


def set_symbols_handler(language, symbols_handler):
    """
    Set a symbol handler for the given language
    """
    global SYMBOLS_HANDLER
    SYMBOLS_HANDLER[language] = symbols_handler


def get_symbols_handler(language):
    """
    Returns the symbol handler for the given language
    """
    global SYMBOLS_HANDLER
    return SYMBOLS_HANDLER.get(language, None)


def init_basic_handlers():
    # Import introspection here, it not needed in the namespace of
    # the rest of the file.
    from ninja_ide.tools import introspection
    # Set Default Symbol Handler
    set_symbols_handler('python', introspection)
