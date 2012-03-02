# -*- coding: utf-8 *-*

import analyzer
import completer


class CodeCompletion(object):

    def __init__(self):
        self.analyzer = analyzer.Analyzer()
        self.current_module = None

    def analyze_project(self, path):
        pass

    def analyze_file(self, path, source=None):
        if source is None:
            with open(path) as f:
                source = f.read()
        self.current_module = self.analyzer.analyze(source)

    def update_file(self, path):
        pass

    def get_completion(self, code, offset, file_path):
        begin = code[:offset].rfind(' ') + 1
        var = code[begin:offset - 1]
        print var
        data_type = self.current_module.get_type(var) + '.'
        print data_type
        data = completer.get_all_completions(data_type,
            ['import __builtin__'])
        print data


text = """
a = "diego"
b = a.split()
"""

offset = 19

cc = CodeCompletion()
cc.analyze_file('path', text)
cc.get_completion(text, offset, 'path')
