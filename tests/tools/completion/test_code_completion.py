# -*- coding: utf-8 *-*
from __future__ import absolute_import

import re
import unittest

from ninja_ide.tools.completion import code_completion


SOURCE = """
a = "ninja-ide"
b = a.split()

import os

r = os.path.sep

from PyQt4 import QtGui

c = QtGui.Q

q = self.wrong_call("home",
        "cat")

mamamia = 2

class MyClass:

    attr = 'my_name'

    def __init__(self):
        self.s = {}
        self.m = 5

    def print_function(self):
        pass

    def another(self):
        l = []"""


class CodeCompletionTestCase(unittest.TestCase):

    def setUp(self):
        global SOURCE
        self.cc = code_completion.CodeCompletion()

    def test_import_completion_in_class(self):
        global SOURCE
        self.cc.analyze_file('', SOURCE)
        source_code = SOURCE + '\n        os.p'
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        for r in results:
            self.assertTrue(r.startswith('p'))

    def test_builtin_list_completion_in_class_not_attr(self):
        global SOURCE
        self.cc.analyze_file('', SOURCE)
        source_code = SOURCE + '\n        l.'
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results)

    def test_builtin_dict_completion_in_class_not_attr(self):
        global SOURCE
        new_lines = '\n        d = {}\n        d.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results)

    def test_builtin_int_completion_in_class_not_attr(self):
        global SOURCE
        new_lines = '\n        i = 4\n        i.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_float_completion_in_class_not_attr(self):
        global SOURCE
        new_lines = '\n        i = 4.3\n        i.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results)

    def test_builtin_tuple_completion_in_class_not_attr(self):
        global SOURCE
        new_lines = '\n        t = ()\n        t.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_bool_completion_in_class_not_attr(self):
        global SOURCE
        new_lines = '\n        b = True\n        b.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results)

    def test_builtin_str_completion_in_class_not_attr(self):
        global SOURCE
        new_lines = '\n        s = "ninja"\n        s.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_unicode_completion_in_class_not_attr(self):
        global SOURCE
        new_lines = '\n        s = u"ninja"\n        s.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(unicode)
        self.assertEqual(expected, results)

    def test_invalid_var_in_class_function(self):
        global SOURCE
        new_lines = '\n        s.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = sorted(set(re.split('\W+', source_code)))
        del expected[0]
        self.assertEqual(expected, results)

    def test_builtin_int_completion_in_class_attr(self):
        global SOURCE
        new_lines = '\n        self.var = 4\n        self.var.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_float_completion_in_class_attr(self):
        global SOURCE
        new_lines = '\n        self.var = 4.3\n        self.var.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results)

    def test_builtin_list_completion_in_class_attr(self):
        global SOURCE
        new_lines = '\n        self.var = []\n        self.var.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results)

    def test_builtin_dict_completion_in_class_attr(self):
        global SOURCE
        new_lines = '\n        self.var = {}\n        self.var.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results)

    def test_builtin_tuple_completion_in_class_attr(self):
        global SOURCE
        new_lines = '\n        self.var = ()\n        self.var.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_bool_completion_in_class_attr(self):
        global SOURCE
        new_lines = '\n        self.var = False\n        self.var.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results)

    def test_builtin_str_completion_in_class_attr(self):
        global SOURCE
        new_lines = '\n        self.var = "ninja"\n        self.var.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_unicode_completion_in_class_attr(self):
        global SOURCE
        new_lines = '\n        self.var = u"ninja"\n        self.var.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(unicode)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_invalid_var_in_class_function_attr(self):
        global SOURCE
        new_lines = '\n        self.invalid.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = sorted(set(re.split('\W+', source_code)))
        del expected[0]
        self.assertEqual(expected, results)

    def test_builtin_dict_completion_in_class_attr_diff_func(self):
        """Test the completion of some attribute from another function."""
        global SOURCE
        new_lines = '\n        self.s.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results)

    def test_builtin_int_completion_in_class_attr_diff_func(self):
        global SOURCE
        new_lines = ('\n        self.var = 4'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_float_completion_in_class_attr_diff_func(self):
        global SOURCE
        new_lines = ('\n        self.var = 4.3'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results)

    def test_builtin_list_completion_in_class_attr_diff_func(self):
        global SOURCE
        new_lines = ('\n        self.var = []'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results)

    def test_builtin_tuple_completion_in_class_attr_diff_func(self):
        global SOURCE
        new_lines = ('\n        self.var = ()'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_bool_completion_in_class_attr_diff_func(self):
        global SOURCE
        new_lines = ('\n        self.var = True'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results)

    def test_builtin_str_completion_in_class_attr_diff_func(self):
        global SOURCE
        new_lines = ('\n        self.var = "ninja"'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_unicode_completion_in_class_attr_diff_func(self):
        global SOURCE
        new_lines = ('\n        self.var = u"ninja"'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(unicode)
        self.assertEqual(expected, results)

    def test_valid_class_attr(self):
        global SOURCE
        new_lines = '\n        self.attr.'
        source_code = SOURCE + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)


if __name__ == '__main__':
    unittest.main()
