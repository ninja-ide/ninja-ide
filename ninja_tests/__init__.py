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

import unittest


class BaseTest(unittest.TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        self._original_values = []

    def patch(self, obj, attr, new_value):
        self._original_values.append((obj, attr, getattr(obj, attr)))
        setattr(obj, attr, new_value)

    def tearDown(self):
        for values in self._original_values:
            obj, attr, old_value = values
            setattr(obj, attr, old_value)