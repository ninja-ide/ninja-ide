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
from ninja_ide.tools.completion import code_completion
from ninja_ide.tools.completion import completion_daemon
from tests.tools.completion import get_source_data, SOURCE_LATE_RESOLUTION


completion_daemon.shutdown_daemon()
completion_daemon.WAITING_BEFORE_START = 0


class AnalyzerLateResolutionTestCase(unittest.TestCase):

    def setUp(self):
        code_completion.settings.SYNTAX = {'python': {'keywords': []}}
        self.cc = code_completion.CodeCompletion()
        self.analyzer = analyzer.Analyzer()

    def tearDown(self):
        completion_daemon.shutdown_daemon()

###############################################################################
# For Python Imports
###############################################################################

    def test_var_attribute_assign(self):
        module = self.analyzer.analyze(SOURCE_LATE_RESOLUTION)

        type1 = model._TypeData(None, 'os', 'import os', None)
        type2 = model.Assign('p')
        type2.add_data(4, model.late_resolution, 'p = os.path', _ast.Attribute)
        expected = {'os': type1}

        for imp in module.imports:
            data = expected[imp]
            impo = module.imports[imp]
            self.assertEqual(data.data_type, impo.data_type)
            self.assertEqual(data.line_content, impo.line_content)
            self.assertEqual(module.attributes['p'].data[0].lineno,
                type2.data[0].lineno)
            self.assertEqual(module.attributes['p'].data[0].data_type,
                type2.data[0].data_type)
            self.assertEqual(module.attributes['p'].data[0].operation,
                type2.data[0].operation)
            self.assertEqual(module.attributes['p'].data[0].line_content,
                type2.data[0].line_content)

    def test_simple_import_late_resolution(self):
        source_code = SOURCE_LATE_RESOLUTION + '\np.'
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        self.assertIn('pathsep', results['attributes'])
        self.assertIn('expanduser', results['functions'])
        self.assertIn('sys', results['modules'])

    def test_simple_import_late_resolution_func(self):
        new_code = ['def func():',
                    '    p.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        self.assertIn('pathsep', results['attributes'])
        self.assertIn('expanduser', results['functions'])
        self.assertIn('sys', results['modules'])

    def test_simple_import_late_resolution_chained_attr(self):
        new_code = ['import threading',
                    't = threading.Lock().']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        self.assertIn('acquire', results['attributes'])

    def test_simple_import_late_resolution_not_outside_func(self):
        new_code = ['def func():',
                    '    q = os.path',
                    'q.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        expected = get_source_data(source_code, 'q')
        self.assertEqual(results, expected)

    def test_simple_import_late_resolution_chained_func_1(self):
        new_code = ['import threading',
                    'import sys',
                    'def func():',
                    '    q = threading.Lock()',
                    '    def gfunc():',
                    '        a = sys',
                    '        a.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        self.assertIn('exit', results['attributes'])

    def test_simple_import_late_resolution_chained_func_2(self):
        new_code = ['import threading',
                    'import sys',
                    'def func():',
                    '    q = threading.Lock()',
                    '    def gfunc():',
                    '        a = sys',
                    '        q.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        self.assertIn('acquire', results['attributes'])

    def test_simple_import_late_resolution_chained_func_3(self):
        new_code = ['import threading',
                    'import sys',
                    'def func():',
                    '    q = threading.Lock()',
                    '    def gfunc():',
                    '        a = sys',
                    '        p.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        self.assertIn('expanduser', results['functions'])

    def test_simple_import_late_resolution_chained_func_4(self):
        new_code = ['import threading',
                    'import sys',
                    'def func():',
                    '    q = threading.Lock()',
                    '    def gfunc():',
                    '        a = sys',
                    '    a.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        expected = get_source_data(source_code, 'a')
        self.assertEqual(expected, results)

    def test_simple_import_late_resolution_chained_func_5(self):
        new_code = ['import threading',
                    'import sys',
                    'def func():',
                    '    q = threading.Lock()',
                    '    def gfunc():',
                    '        a = sys',
                    '    q.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        self.assertIn('acquire', results['attributes'])

    def test_simple_import_late_resolution_chained_func_6(self):
        new_code = ['import threading',
                    'import sys',
                    'def func():',
                    '    q = threading.Lock()',
                    '    def gfunc():',
                    '        a = sys',
                    'p.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        self.assertIn('expanduser', results['functions'])

    def test_simple_import_late_resolution_chained_func_7(self):
        new_code = ['import threading',
                    'import sys',
                    'def func():',
                    '    q = threading.Lock()',
                    '    def gfunc():',
                    '        a = sys',
                    'q.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        expected = get_source_data(source_code, 'q')
        self.assertEqual(expected, results)

    def test_simple_import_late_resolution_local_symbols(self):
        new_code = ['class MyClass(object):',
                    '    def __init__(self):',
                    '        self.value1 = True',
                    '    def func(self):',
                    '        self.q = os.path',
                    '    def gfunc(self):',
                    '        import sys',
                    '        self.a = sys',
                    'mc = MyClass()',
                    'mc.']
        source_code = SOURCE_LATE_RESOLUTION + '\n'.join(new_code)
        self.cc.analyze_file('', source_code)
        offset = len(source_code)
        import time
        time.sleep(1)
        results = self.cc.get_completion(source_code, offset)
        expected = {'attributes': ['a', 'q', 'value1'],
                    'functions': ['__init__', 'func', 'gfunc']}
        self.assertEqual(expected, results)


if __name__ == '__main__':
    unittest.main()
