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

import _ast
import unittest

from ninja_ide.tools.completion import analyzer
from ninja_ide.tools.completion import model
from ninja_tests.tools.completion import SOURCE_ANALYZER_NATIVE


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
        self.assertEqual(clazz.bases, {'object': None})

    def test_simple_class_attrs(self):
        module = self.analyzer.analyze(SOURCE_ANALYZER_NATIVE)

        clazz = module.classes['Test']
        attr_x = clazz.attributes['x']
        attr_var = clazz.attributes['var']
        type_x = attr_x.data[0]
        type_var = attr_var.data[0]

        self.assertEqual(type_x.data_type, '__builtin__.dict')
        self.assertEqual(type_x.line_content, '        self.x = {}')
        self.assertEqual(type_x.operation, None)
        self.assertEqual(type_x.from_import, False)
        self.assertEqual(type_x.is_native, True)
        self.assertEqual(type_var.data_type, '__builtin__.float')
        self.assertEqual(type_var.line_content, '        self.var = 4.5')
        self.assertEqual(type_var.operation, None)
        self.assertEqual(type_var.from_import, False)
        self.assertEqual(type_var.is_native, True)

    def test_attrs_in_class_func(self):
        module = self.analyzer.analyze(SOURCE_ANALYZER_NATIVE)

        clazz = module.classes['Test']
        func = clazz.functions['my_function']

        self.assertEqual(func.args, {})
        self.assertEqual(func.decorators, [])
        self.assertEqual(func.return_type, [])
        self.assertEqual(func.name, 'my_function')
        self.assertEqual(func.functions, {})
        #Assign
        result_a = func.attributes.keys()
        result_a.sort()
        expected = ['code', 'my_var']
        self.assertEqual(result_a, expected)
        #Assing: code
        assign = func.attributes['code']
        self.assertEqual(assign.name, 'code')
        assign_test1 = model.Assign('code')
        assign_test1.add_data(0, '__builtin__.str', "        code = 'string'",
            None)
        expected_data = assign_test1.data[0]
        result_data = assign.data[0]
        self.assertEqual(result_data.data_type, expected_data.data_type)
        self.assertEqual(result_data.line_content, expected_data.line_content)
        self.assertEqual(result_data.operation, expected_data.operation)
        self.assertTrue(result_data.is_native)
        self.assertFalse(result_data.from_import)
        #Assing: my_var
        assign = func.attributes['my_var']
        self.assertEqual(assign.name, 'my_var')
        assign_test1 = model.Assign('my_var')
        assign_test1.add_data(0, '__builtin__.str',
        "            my_var = 'inside if'", None)
        expected_data = assign_test1.data[0]
        result_data = assign.data[0]
        self.assertEqual(result_data.data_type, expected_data.data_type)
        self.assertEqual(result_data.line_content, expected_data.line_content)
        self.assertEqual(result_data.operation, expected_data.operation)
        self.assertTrue(result_data.is_native)
        self.assertFalse(result_data.from_import)

    def test_attrs_in_class_func_extended(self):
        module = self.analyzer.analyze(SOURCE_ANALYZER_NATIVE)

        clazz = module.classes['Test']
        func = clazz.functions['func_args']

        #Args
        args_names = ['var', 'inte', 'num', 'li', 'arggg', 'kwarggg']
        args_names.sort()
        func_args = func.args.keys()
        func_args.sort()
        self.assertEqual(func_args, args_names)
        #For: var
        type_var = model._TypeData(0, model.late_resolution, None, None)
        func_arg_obj = func.args['var']
        type_arg_func = func_arg_obj.data[0]
        self.assertEqual(func_arg_obj.name, 'var')
        self.assertEqual(type_arg_func.data_type, type_var.data_type)
        self.assertEqual(type_arg_func.line_content, type_var.line_content)
        self.assertEqual(type_arg_func.operation, type_var.operation)
        self.assertFalse(type_arg_func.is_native)
        #For: inte
        type_var = model._TypeData(0, model.late_resolution, None, None)
        func_arg_obj = func.args['inte']
        type_arg_func = func_arg_obj.data[0]
        self.assertEqual(func_arg_obj.name, 'inte')
        self.assertEqual(type_arg_func.data_type, type_var.data_type)
        self.assertEqual(type_arg_func.line_content, type_var.line_content)
        self.assertEqual(type_arg_func.operation, type_var.operation)
        self.assertFalse(type_arg_func.is_native)
        #For: num
        type_var = model._TypeData(0, '__builtin__.int', None, None)
        func_arg_obj = func.args['num']
        type_arg_func = func_arg_obj.data[0]
        self.assertEqual(func_arg_obj.name, 'num')
        self.assertEqual(type_arg_func.data_type, type_var.data_type)
        self.assertEqual(type_arg_func.line_content, type_var.line_content)
        self.assertEqual(type_arg_func.operation, type_var.operation)
        self.assertTrue(type_arg_func.is_native)
        #For: li
        type_var = model._TypeData(0, '__builtin__.str', None, None)
        func_arg_obj = func.args['li']
        type_arg_func = func_arg_obj.data[0]
        self.assertEqual(func_arg_obj.name, 'li')
        self.assertEqual(type_arg_func.data_type, type_var.data_type)
        self.assertEqual(type_arg_func.line_content, type_var.line_content)
        self.assertEqual(type_arg_func.operation, type_var.operation)
        self.assertTrue(type_arg_func.is_native)
        #For: arggg
        type_var = model._TypeData(0, '__builtin__.list', None, None)
        func_arg_obj = func.args['arggg']
        type_arg_func = func_arg_obj.data[0]
        self.assertEqual(func_arg_obj.name, 'arggg')
        self.assertEqual(type_arg_func.data_type, type_var.data_type)
        self.assertEqual(type_arg_func.line_content, type_var.line_content)
        self.assertEqual(type_arg_func.operation, type_var.operation)
        self.assertTrue(type_arg_func.is_native)
        #For: kwarggg
        type_var = model._TypeData(0, '__builtin__.dict', None, None)
        func_arg_obj = func.args['kwarggg']
        type_arg_func = func_arg_obj.data[0]
        self.assertEqual(func_arg_obj.name, 'kwarggg')
        self.assertEqual(type_arg_func.data_type, type_var.data_type)
        self.assertEqual(type_arg_func.line_content, type_var.line_content)
        self.assertEqual(type_arg_func.operation, type_var.operation)
        self.assertTrue(type_arg_func.is_native)

        #Decorators
        self.assertEqual(func.decorators, [])
        #Return Type
        self.assertEqual(func.return_type, [])
        #Attributes
        self.assertEqual(func.name, 'func_args')
        self.assertEqual(func.functions, {})
        #Assign
        result_a = func.attributes.keys()
        expected = ['nothing']
        self.assertEqual(result_a, expected)
        assign = func.attributes['nothing']
        self.assertEqual(assign.name, 'nothing')
        assign_test1 = model.Assign('nothing')
        assign_test1.add_data(0, '__builtin__.bool', "        nothing = False",
            None)
        expected_data = assign_test1.data[0]
        result_data = assign.data[0]
        self.assertEqual(result_data.data_type, expected_data.data_type)
        self.assertEqual(result_data.line_content, expected_data.line_content)
        self.assertEqual(result_data.operation, expected_data.operation)
        self.assertTrue(result_data.is_native)
        self.assertFalse(result_data.from_import)


if __name__ == '__main__':
    unittest.main()
