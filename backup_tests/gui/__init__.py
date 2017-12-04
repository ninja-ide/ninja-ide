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

# Import this before Qt to set the correct API
import ninja_ide  # lint:ok

from PyQt4.QtGui import QPlainTextEdit


class FakeExplorer(object):

    def get_project_given_filename(self, filename):
        return 'fake project for: %s' % filename


class FakeParent(object):

    def __init__(self):
        self.explorer = FakeExplorer()


class FakeEditor(QPlainTextEdit):

    def __init__(self, *args, **kwargs):
        super(FakeEditor, self).__init__()
        self.syntax = None
        self._id = None

    def register_syntax(self, syntax):
        self.syntax = syntax


class FakeQSettings(object):

    def __init__(self):
        self.names = []
        self.values = {}

    def beginGroup(self, name):
        self.names.append(name)

    def endGroup(self):
        self.names.pop()

    def setValue(self, key, val):
        self.values[key] = val

    def value(self, key, default_val=None):
        return self.values.get(key, default_val)


class FakeActions(object):

    def __init__(self):
        self.reset_editor_flags_executed = False
        self.func_name = ''

    def reset_editor_flags(self):
        self.reset_editor_flags_executed = True

    def call_editors_function(self, func_name):
        self.func_name = func_name
