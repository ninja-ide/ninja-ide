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
import unittest

from ninja_ide.core.plugin_interfaces import implements
from ninja_ide.core.plugin_interfaces import MethodNotImplemented


class A(object):
    def _a_private_method(self):
        pass

    def one(self):
        pass

    def two(self):
        pass


class B(object):
    pass


class C(object):
    def one(self):
        pass

    def two(self):
        pass


class PluginInterfacesTestCase(unittest.TestCase):

    def test_implements_decorator(self):
        a_implement = implements(A)
        self.assertRaises(MethodNotImplemented, a_implement, B)
        self.assertEqual(a_implement(C), C)

if __name__ == '__main__':
    unittest.main()
