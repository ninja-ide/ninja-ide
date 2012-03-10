# -*- coding: utf-8 *-*
from __future__ import absolute_import

import re
import unittest

from ninja_ide.tools.completion import code_completion
from tests.tools.completion import SOURCE_COMPLETION


class CodeCompletionTestCase(unittest.TestCase):

    def setUp(self):
        global SOURCE_COMPLETION
        self.cc = code_completion.CodeCompletion()

###############################################################################
# TESTS FOR BUILTIN COMPLETION
###############################################################################

    def test_import_completion_in_class(self):
        global SOURCE_COMPLETION
        self.cc.analyze_file('', SOURCE_COMPLETION)
        source_code = SOURCE_COMPLETION + '\n        os.p'
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        for r in results:
            self.assertTrue(r.startswith('p'))

    def test_builtin_list_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        self.cc.analyze_file('', SOURCE_COMPLETION)
        source_code = SOURCE_COMPLETION + '\n        l.'
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results)

    def test_builtin_dict_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        d = {}\n        d.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results)

    def test_builtin_int_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        i = 4\n        i.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_float_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        i = 4.3\n        i.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results)

    def test_builtin_tuple_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        t = ()\n        t.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_bool_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        b = True\n        b.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results)

    def test_builtin_str_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        s = "ninja"\n        s.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_unicode_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        s = u"ninja"\n        s.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(unicode)
        self.assertEqual(expected, results)

    def test_invalid_var_in_class_function(self):
        global SOURCE_COMPLETION
        new_lines = '\n        s.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = sorted(set(re.split('\W+', source_code)))
        del expected[0]
        self.assertEqual(expected, results)

    def test_builtin_int_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = 4\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_float_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = 4.3\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results)

    def test_builtin_list_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = []\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results)

    def test_builtin_dict_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = {}\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results)

    def test_builtin_tuple_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = ()\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_bool_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = False\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results)

    def test_builtin_str_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = "ninja"\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_unicode_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = u"ninja"\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(unicode)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_invalid_var_in_class_function_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.invalid.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = sorted(set(re.split('\W+', source_code)))
        del expected[0]
        self.assertEqual(expected, results)

    def test_builtin_dict_completion_in_class_attr_diff_func(self):
        """Test the completion of some attribute from another function."""
        global SOURCE_COMPLETION
        new_lines = '\n        self.s.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results)

    def test_builtin_int_completion_in_class_attr_diff_func(self):
        global SOURCE_COMPLETION
        new_lines = ('\n        self.var = 4'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_float_completion_in_class_attr_diff_func(self):
        global SOURCE_COMPLETION
        new_lines = ('\n        self.var = 4.3'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results)

    def test_builtin_list_completion_in_class_attr_diff_func(self):
        global SOURCE_COMPLETION
        new_lines = ('\n        self.var = []'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results)

    def test_builtin_tuple_completion_in_class_attr_diff_func(self):
        global SOURCE_COMPLETION
        new_lines = ('\n        self.var = ()'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_bool_completion_in_class_attr_diff_func(self):
        global SOURCE_COMPLETION
        new_lines = ('\n        self.var = True'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results)

    def test_builtin_str_completion_in_class_attr_diff_func(self):
        global SOURCE_COMPLETION
        new_lines = ('\n        self.var = "ninja"'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_unicode_completion_in_class_attr_diff_func(self):
        global SOURCE_COMPLETION
        new_lines = ('\n        self.var = u"ninja"'
                     '\n\n    def new_func(self):'
                     '\n        self.var.')
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(unicode)
        self.assertEqual(expected, results)

    def test_valid_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.attr.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)

    def test_import_completion(self):
        global SOURCE_COMPLETION
        self.cc.analyze_file('', SOURCE_COMPLETION)
        source_code = SOURCE_COMPLETION + '\n\nos.p'
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        for r in results:
            self.assertTrue(r.startswith('p'))

    def test_builtin_list_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\nlis = []\nlis.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results)

    def test_builtin_dict_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\nd = {}\nd.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results)

    def test_builtin_int_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ni = 4\ni.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_float_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ni = 4.3\ni.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results)

    def test_builtin_tuple_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\nt = ()\nt.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_bool_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\nb = True\nb.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results)

    def test_builtin_str_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ns = "ninja"\ns.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results)

    @unittest.skip("FIX LATER")
    def test_builtin_unicode_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ns = u"ninja"\ns.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(unicode)
        self.assertEqual(expected, results)

    def test_invalid_var(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ninvalid.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = sorted(set(re.split('\W+', source_code)))
        del expected[0]
        self.assertEqual(expected, results)


if __name__ == '__main__':
    unittest.main()
