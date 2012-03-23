# -*- coding: utf-8 *-*
from __future__ import absolute_import

import _ast
import unittest

from ninja_ide.tools.completion import analyzer
from ninja_ide.tools.completion import model
from tests.tools.completion import SOURCE_ANALYZER_NATIVE


class AnalyzerTestCase(unittest.TestCase):

    def setUp(self):
        self.analyzer = analyzer.Analyzer()

###############################################################################
# SIMPLE NATIVE TYPES
###############################################################################

    def test_content_value(self):
        self.assertTrue(self.analyzer.content is None)
        self.analyzer.analyze(SOURCE_ANALYZER_NATIVE)
        self.assertTrue(self.analyzer.content is None)

    def test_imports(self):
        module = self.analyzer.analyze(SOURCE_ANALYZER_NATIVE)

        type1 = model._TypeData(None, 'sys', 'import sys', None)
        type2 = model._TypeData(None, 'os', 'import os', None)
        type3 = model._TypeData(None, 'sys.exit', 'import sys.exit', None)
        expected = {'sys': type1, 'os': type2, 'exit': type3}

        for imp in module.imports:
            data = expected[imp]
            impo = module.imports[imp]
            self.assertEqual(data.data_type, impo.data_type)
            self.assertEqual(data.line_content, impo.line_content)

    def test_module_class_func_attrs(self):
        module = self.analyzer.analyze(SOURCE_ANALYZER_NATIVE)

        result_f = module.functions.keys()
        result_f.sort()
        result_a = module.attributes.keys()
        result_a.sort()
        result_c = module.classes.keys()
        functions = ['global_func']
        attrs = ['a', 'b', 'man']
        classes = ['Test']
        functions.sort()
        attrs.sort()
        self.assertEqual(result_f, functions)
        self.assertEqual(result_a, attrs)
        self.assertEqual(result_c, classes)

    def test_attrs_in_module_func(self):
        module = self.analyzer.analyze(SOURCE_ANALYZER_NATIVE)

        func = module.functions['global_func']

        self.assertEqual(func.args, {})
        self.assertEqual(func.decorators, [])
        self.assertEqual(func.return_type, [])
        self.assertEqual(func.name, 'global_func')
        self.assertEqual(func.functions, {})
        #Assign: 1
        result_a = func.attributes.keys()
        result_a.sort()
        expected = ['another', 'bo', 'di', 'obj']
        self.assertEqual(result_a, expected)
        assign = func.attributes['bo']
        self.assertEqual(assign.name, 'bo')
        assign_test1 = model.Assign('bo')
        assign_test1.add_data(0, '__builtin__.bool', '    bo = True', None)
        expected_data = assign_test1.data[0]
        result_data = assign.data[0]
        self.assertEqual(result_data.data_type, expected_data.data_type)
        self.assertEqual(result_data.line_content, expected_data.line_content)
        self.assertEqual(result_data.operation, expected_data.operation)
        self.assertTrue(result_data.is_native)
        self.assertFalse(result_data.from_import)
        #Assign: 2
        assign = func.attributes['obj']
        self.assertEqual(assign.name, 'obj')
        assign_test2 = model.Assign('obj')
        assign_test2.add_data(0, model.late_resolution,
            '    obj = os.path', _ast.Attribute)
        expected_data = assign_test2.data[0]
        result_data = assign.data[0]
        self.assertEqual(result_data.data_type, expected_data.data_type)
        self.assertEqual(result_data.line_content, expected_data.line_content)
        self.assertEqual(result_data.operation, expected_data.operation)
        self.assertFalse(result_data.is_native)
#        self.assertTrue(result_data.from_import)
        #Assign: 3
        assign = func.attributes['di']
        self.assertEqual(assign.name, 'di')
        assign_test2 = model.Assign('di')
        assign_test2.add_data(0, model.late_resolution,
            '    di = Test()', _ast.Call)
        expected_data = assign_test2.data[0]
        result_data = assign.data[0]
        self.assertEqual(result_data.data_type, expected_data.data_type)
        self.assertEqual(result_data.line_content, expected_data.line_content)
        self.assertEqual(result_data.operation, expected_data.operation)
        self.assertFalse(result_data.is_native)
        self.assertFalse(result_data.from_import)
        #Assign: 4
        assign = func.attributes['another']
        self.assertEqual(assign.name, 'another')
        assign_test2 = model.Assign('another')
        assign_test2.add_data(0, model.late_resolution,
            '    another = obj', _ast.Name)
        expected_data = assign_test2.data[0]
        result_data = assign.data[0]
        self.assertEqual(result_data.data_type, expected_data.data_type)
        self.assertEqual(result_data.line_content, expected_data.line_content)
        self.assertEqual(result_data.operation, expected_data.operation)
        self.assertFalse(result_data.is_native)
#        self.assertFalse(result_data.from_import)

    def test_simple_class_data(self):
        module = self.analyzer.analyze(SOURCE_ANALYZER_NATIVE)

        clazz = module.classes['Test']
        result_f = clazz.functions.keys()
        result_f.sort()
        result_a = clazz.attributes.keys()
        result_a.sort()
        functions = ['__init__', 'my_function', 'func_args']
        attrs = ['x', 'var']
        functions.sort()
        attrs.sort()
        self.assertEqual(result_f, functions)
        self.assertEqual(result_a, attrs)


if __name__ == '__main__':
    unittest.main()
