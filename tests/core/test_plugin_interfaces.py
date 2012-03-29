# -*- coding: utf-8 *-*
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
