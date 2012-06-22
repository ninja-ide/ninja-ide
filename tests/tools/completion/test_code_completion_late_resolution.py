# -*- coding: utf-8 *-*
from __future__ import absolute_import

import _ast
import re
import unittest

from ninja_ide.tools.completion import analyzer
from ninja_ide.tools.completion import model
from ninja_ide.tools.completion import code_completion
from ninja_ide.tools.completion import completion_daemon
from tests.tools.completion import SOURCE_LATE_RESOLUTION


completion_daemon.shutdown_daemon()
completion_daemon.WAITING_BEFORE_START = 0


class AnalyzerLateResolutionTestCase(unittest.TestCase):

    def setUp(self):
        code_completion.settings.SYNTAX = {'python': {'keywords': []}}
        self.cc = code_completion.CodeCompletion()
        self.analyzer = analyzer.Analyzer()

    def tearDown(self):
        completion_daemon.shutdown_daemon()

    def get_source_data(self, code, word=""):
        clazzes = sorted(set(re.findall("class (\w+?)\(", code)))
        funcs = sorted(set(re.findall("(\w+?)\(", code)))
        attrs = sorted(set(re.split('\W+', code)))
        del attrs[0]
        filter_attrs = lambda x: (x not in funcs) and not x.isdigit()
        attrs = filter(filter_attrs, attrs)
        if word in attrs:
            attrs.remove(word)
        funcs = filter(lambda x: x not in clazzes, funcs)
        data = {'attributes': attrs,
            'functions': funcs,
            'classes': clazzes}
        return data

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
        self.assertIn('expanduser(path)', results['functions'])
        self.assertIn('sys', results['modules'])


if __name__ == '__main__':
    unittest.main()
