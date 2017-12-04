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

NOTIFICATIONS_CHECKERS = {}


def register_checker(lang='python', checker=None, color=None, priority=1):
    """Register a Checker (Like PEP8, Lint, etc) for some language.
    @lang: language that the checker apply.
    @checker: Class to be instantiated.
    @color: the color that this checker will use.
    @priority: the priority of this checker (1=LOW, >1 = HIGH...)"""
    global NOTIFICATIONS_CHECKERS
    checkers = NOTIFICATIONS_CHECKERS.get(lang, [])
    checkers.append((checker, color, priority))
    NOTIFICATIONS_CHECKERS[lang] = checkers


def remove_checker(checker):
    global NOTIFICATIONS_CHECKERS
    checkers = NOTIFICATIONS_CHECKERS.get('python', [])
    if checker in checkers:
        checkers.remove(checker)
        NOTIFICATIONS_CHECKERS['python'] = checkers


def get_checkers_for(lang='python'):
    """Get a registered checker for some language."""
    global NOTIFICATIONS_CHECKERS
    return NOTIFICATIONS_CHECKERS.get(lang, [])
