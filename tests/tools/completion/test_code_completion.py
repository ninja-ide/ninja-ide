# -*- coding: utf-8 *-*
from __future__ import absolute_import

import re
import unittest

from ninja_ide.tools.completion import code_completion
from tests.tools.completion import SOURCE_COMPLETION


class CodeCompletionTestCase(unittest.TestCase):

    def setUp(self):
        self.cc = code_completion.CodeCompletion()

    def get_source_data(self, code):
        clazzes = re.findall("class (\w+?)\(", code)
        funcs = re.findall("(\w+?)\(", code)
        attrs = sorted(set(re.split('\W+', code)))
        del attrs[0]
        attrs = filter(lambda x: x not in funcs, attrs)
        funcs = filter(lambda x: x not in clazzes, funcs)
        data = {'attributes': attrs,
            'functions': funcs,
            'classes': clazzes}
        return data

###############################################################################
# TESTS FOR BUILTIN COMPLETION
###############################################################################

    def test_import_completion_in_class(self):
        global SOURCE_COMPLETION
        self.cc.analyze_file('', SOURCE_COMPLETION)
        source_code = SOURCE_COMPLETION + '\n        os.p'
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        for r in results['functions']:
            self.assertTrue(r.startswith('p'))

    def test_global_attr_in_class(self):
        global SOURCE_COMPLETION
        source_code = SOURCE_COMPLETION + '\n        mamamia.'
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results['functions'])

    def test_global_attr_not_recognized_in_class(self):
        global SOURCE_COMPLETION
        source_code = SOURCE_COMPLETION + '\n        cat.'
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = self.get_source_data(SOURCE_COMPLETION)
        self.assertEqual(expected, results)

    def test_builtin_list_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        self.cc.analyze_file('', SOURCE_COMPLETION)
        source_code = SOURCE_COMPLETION + '\n        l.'
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results['functions'])

    def test_builtin_dict_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        d = {}\n        d.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results['functions'])

    def test_builtin_int_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        i = 4\n        i.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results['functions'])

    def test_builtin_float_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        i = 4.3\n        i.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results['functions'])

    def test_builtin_tuple_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        t = ()\n        t.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results['functions'])

    def test_builtin_bool_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        b = True\n        b.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results['functions'])

    def test_builtin_str_completion_in_class_not_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        s = "ninja"\n        s.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results['functions'])

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
        expected = self.get_source_data(SOURCE_COMPLETION)
        self.assertEqual(expected, results)

    def test_builtin_int_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = 4\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results['functions'])

    def test_builtin_float_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = 4.3\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results['functions'])

    def test_builtin_list_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = []\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results['functions'])

    def test_builtin_dict_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = {}\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results['functions'])

    def test_builtin_tuple_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = ()\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results['functions'])

    def test_builtin_bool_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = False\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results['functions'])

    def test_builtin_str_completion_in_class_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.var = "ninja"\n        self.var.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results['functions'])

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

    def test_invalid_var_in_class_function_attr(self):
        global SOURCE_COMPLETION
        new_lines = '\n        self.invalid.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = self.get_source_data(source_code)
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
        self.assertEqual(expected, results['functions'])

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
        self.assertEqual(expected, results['functions'])

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
        self.assertEqual(expected, results['functions'])

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
        self.assertEqual(expected, results['functions'])

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
        self.assertEqual(expected, results['functions'])

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
        self.assertEqual(expected, results['functions'])

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
        self.assertEqual(expected, results['functions'])

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
        self.assertEqual(expected, results['functions'])

    def test_import_completion(self):
        global SOURCE_COMPLETION
        self.cc.analyze_file('', SOURCE_COMPLETION)
        source_code = SOURCE_COMPLETION + '\n\nos.p'
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        for r in results['functions']:
            self.assertTrue(r.startswith('p'))

    def test_builtin_list_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\nlis = []\nlis.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(list)
        self.assertEqual(expected, results['functions'])

    def test_builtin_dict_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\nd = {}\nd.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(dict)
        self.assertEqual(expected, results['functions'])

    def test_builtin_int_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ni = 4\ni.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(int)
        self.assertEqual(expected, results['functions'])

    def test_builtin_float_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ni = 4.3\ni.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(float)
        self.assertEqual(expected, results['functions'])

    def test_builtin_tuple_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\nt = ()\nt.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(tuple)
        self.assertEqual(expected, results['functions'])

    def test_builtin_bool_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\nbo = True\nbo.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(bool)
        self.assertEqual(expected, results['functions'])

    def test_builtin_str_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ns = "ninja"\ns.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(str)
        self.assertEqual(expected, results['functions'])

    @unittest.skip("FIX LATER")
    def test_builtin_unicode_completion(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ns = u"ninja"\ns.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = dir(unicode)
        self.assertEqual(expected, results['functions'])

    def test_invalid_var(self):
        global SOURCE_COMPLETION
        new_lines = '\n\ninvalid.'
        source_code = SOURCE_COMPLETION + new_lines
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        results = self.cc.get_completion(source_code, offset)
        expected = self.get_source_data(source_code)
        self.assertEqual(expected, results)

###############################################################################
# TESTS FOR COMPLETION SEGMENT
###############################################################################

    def test_completion_segment1(self):
        source = """var."""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.'
        self.assertEqual(expected, segment)

    def test_completion_segment2(self):
        source = """var.attr"""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.attr'
        self.assertEqual(expected, segment)

    def test_completion_segment3(self):
        source = """var.attr."""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.attr.'
        self.assertEqual(expected, segment)

    def test_completion_segment4(self):
        source = """var.func()"""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.func()'
        self.assertEqual(expected, segment)

    def test_completion_segment5(self):
        source = """var.func()."""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.func().'
        self.assertEqual(expected, segment)

    def test_completion_segment6(self):
        source = """var.func('name')."""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.func().'
        self.assertEqual(expected, segment)

    def test_completion_segment7(self):
        source = """q = var.func('name')."""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.func().'
        self.assertEqual(expected, segment)

    def test_completion_segment8(self):
        source = """
            f = ase.port("diego", [], {},
                "gato")"""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'ase.port()'
        self.assertEqual(expected, segment)

    def test_completion_segment9(self):
        source = """
            f = ase.port("diego", [], {},
                "gato")."""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'ase.port().'
        self.assertEqual(expected, segment)

    def test_completion_segment10(self):
        source = """
            f = ase.port("diego", [], {},
                "gato").attr"""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'ase.port().attr'
        self.assertEqual(expected, segment)

    def test_completion_segment11(self):
        source = """
            f = ase.port("diego", [], {},
                "gato").attr."""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'ase.port().attr.'
        self.assertEqual(expected, segment)

    def test_completion_segment12(self):
        source = """
            ase.port(var.)"""
        token_code = self.cc._tokenize_text(source[:len(source) - 1])
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.'
        self.assertEqual(expected, segment)

    def test_completion_segment13(self):
        source = """
            ase.port(var.func('name', 3, [yep], (6, 7)).attr)"""
        token_code = self.cc._tokenize_text(source[:len(source) - 1])
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.func().attr'
        self.assertEqual(expected, segment)

    def test_completion_segment14(self):
        #doesn't have much sense, but i wanted to test it
        source = """
            ase.port{var.func('name', 3, [yep], (6, 7)).attr}"""
        token_code = self.cc._tokenize_text(source[:len(source) - 1])
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.func().attr'
        self.assertEqual(expected, segment)

    def test_completion_segment15(self):
        #doesn't have much sense, but i wanted to test it
        source = """
            f = ase.port[var.func('name', 3, [yep], (6, 7)).attr]"""
        token_code = self.cc._tokenize_text(source[:len(source) - 1])
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'var.func().attr'
        self.assertEqual(expected, segment)

    def test_completion_segment16(self):
        #doesn't have much sense, but i wanted to test it
        source = """asd.\
            ase.port(var.func('name', 3, [yep], (6, 7)).attr)."""
        token_code = self.cc._tokenize_text(source)
        segment = self.cc._search_for_completion_segment(token_code)
        expected = 'asd.ase.port().'
        self.assertEqual(expected, segment)

###############################################################################
# TESTS FOR SCOPE SEARCH
###############################################################################

    def test_search_for_scope1(self):
        global SOURCE_COMPLETION
        new_lines = '\n        l.'
        source_code = SOURCE_COMPLETION + new_lines
        token_code = self.cc._tokenize_text(source_code)
        scope = self.cc._search_for_scope(token_code)
        expected = ['MyClass', 'another']
        self.assertEqual(expected, scope)

    def test_search_for_scope2(self):
        global SOURCE_COMPLETION
        new_lines = '\n    l.'
        source_code = SOURCE_COMPLETION + new_lines
        token_code = self.cc._tokenize_text(source_code)
        scope = self.cc._search_for_scope(token_code)
        expected = ['MyClass']
        self.assertEqual(expected, scope)

    def test_search_for_scope3(self):
        global SOURCE_COMPLETION
        new_lines = ('\n        def new_func():'
                     '\n            self.var.')
        source_code = SOURCE_COMPLETION + new_lines
        token_code = self.cc._tokenize_text(source_code)
        scope = self.cc._search_for_scope(token_code)
        expected = ['MyClass', 'another', 'new_func']
        self.assertEqual(expected, scope)

    def test_search_for_scope(self):
        global SOURCE_COMPLETION
        new_lines = ('\nvar.')
        source_code = SOURCE_COMPLETION + new_lines
        token_code = self.cc._tokenize_text(source_code)
        scope = self.cc._search_for_scope(token_code)
        self.assertEqual(None, scope)


if __name__ == '__main__':
    unittest.main()
