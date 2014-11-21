# -*- coding: utf-8 -*-


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


"""PEP8 Mod Settings for Ninja-IDE."""


# imports
from ninja_ide.dependencies import pep8mod


###############################################################################
# Utility functions to update (patch at runtime) pep8mod.py
###############################################################################


def pep8mod_refresh_checks():
    """Force to reload all checks in pep8mod.py."""
    # pep8mod.refresh_checks()
    pass


def pep8mod_add_ignore(ignore_code):
    """Patch pep8mod.py to ignore a given check by code
    EXAMPLE:
        pep8mod_add_ignore('W191')
        'W1919': 'indentation contains tabs'."""
    pep8mod.options.ignore.append(ignore_code)


def pep8mod_remove_ignore(ignore_code):
    """Patch pep8mod.py to remove the ignore of a give check
    EXAMPLE:
        pep8mod_remove_ignore('W191')
        'W1919': 'indentation contains tabs'."""
    if ignore_code in pep8mod.options.ignore:
        pep8mod.options.ignore.remove(ignore_code)


def pep8mod_update_margin_line_length(new_margin_line):
    """Patch pep8mod.py to update the margin line length with a new value."""
    pep8mod.MAX_LINE_LENGTH = new_margin_line
    pep8mod.options.max_line_length = new_margin_line
