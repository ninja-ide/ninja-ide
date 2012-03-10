# -*- coding: utf-8 *-*

import re
import token as tkn
from tokenize import generate_tokens, TokenError
from StringIO import StringIO

from ninja_ide.tools.completion import analyzer
from ninja_ide.tools.completion import completer


#Because my python doesn't have it, and is not in the web docs either
#but trust me, it exists!
_TOKEN_NL = 54


class CodeCompletion(object):

    def __init__(self):
        self.analyzer = analyzer.Analyzer()
        self.current_module = None
        self.patIndent = re.compile('^\s+')
        self._valid_op = (')', '}', ']')
        self._invalid_op = ('(', '{', '[')

    def analyze_project(self, path):
        pass

    def analyze_file(self, path, source=None):
        if source is None:
            with open(path) as f:
                source = f.read()
        self.current_module = self.analyzer.analyze(source)

    def update_file(self, path):
        pass

    def _tokenize_text(self, code):
        # Optimization, only iterate until the previous line of a class??
        token_code = []
        try:
            for t in generate_tokens(StringIO(code).readline):
                token_code.append((t[0], t[1], t[2], t[4]))
        except TokenError:
            #This is an expected situation, where i don't want to do anything
            #possible an unbalanced brace like: func(os.p| (| = cursor-end)
            pass
        while token_code[-1][0] in (tkn.ENDMARKER, tkn.DEDENT, tkn.NEWLINE):
            token_code.pop()
        return token_code

    def _search_for_scope(self, token_code):
        global _TOKEN_NL
        if not token_code[-1][3].startswith(' '):
            return None
        scopes = []
        indent = len(token_code[-1][3])
        previous_line = ('', '')
        keep_exploring = True
        iter = reversed(token_code)
        line = iter.next()
        while keep_exploring:
            is_indented = line[3].startswith(' ')
            is_definition = line[1] in ('def', 'class')
            #Skip lines that are not def or class
            if is_indented and is_definition:
                new_indent = self.patIndent.match(line[3])
                if new_indent is not None:
                    new_indent = len(new_indent.group())
                #We only care about the function where we are
                if new_indent < indent:
                    indent = new_indent
                    scopes.insert(0, previous_line)
            elif not is_indented and is_definition:
                scopes.insert(0, previous_line)
                keep_exploring = False
            previous_line = line[1]
            try:
                line = iter.next()
            except StopIteration:
                keep_exploring = False
        return scopes

    def _search_for_completion_segment(self, token_code):
        tokens = []
        keep_iter = True
        iter = reversed(token_code)
        value = iter.next()
        while keep_iter:
            if value[0] in (tkn.NEWLINE, tkn.INDENT, tkn.DEDENT):
                keep_iter = False
            tokens.append(value)
            value = iter.next()
        segment = ''
        brace_stack = 0
        for t in tokens:
            token_str = t[1]
            if token_str in self._valid_op:
                if brace_stack == 0:
                    segment = token_str + segment
                brace_stack += 1
            elif token_str in self._invalid_op:
                brace_stack -= 1
                if brace_stack == 0:
                    segment = token_str + segment
                    continue
            if brace_stack != 0:
                continue

            op = t[0]
            if (op == tkn.NAME) or token_str == '.':
                segment = token_str + segment
            elif op == tkn.OP:
                break
        return segment

    def get_completion(self, code, offset):
        token_code = self._tokenize_text(code[:offset])
        scopes = self._search_for_scope(token_code)
        var_segment = self._search_for_completion_segment(token_code)
        words = var_segment.split('.', 1)
        words_final = var_segment.rsplit('.', 1)
        attr_name = words[0].strip()
        word = ''
        final_word = ''
        if var_segment.count(".") > 0:
            word = words[1].strip()
        if not var_segment.endswith('.') and len(words_final) > 1:
            final_word = words_final[1].strip()
            word = word.rsplit('.', 1)[0].strip()
            if final_word == word:
                word = ''
        result = self.current_module.get_type(attr_name, word, scopes)
        if result[0] and result[1] is not None:
            imports = self.current_module.get_imports()
            to_complete = "%s.%s" % (result[1], final_word)
            data = completer.get_all_completions(to_complete, imports)
        else:
            if result[1] is not None and len(result[1]) > 0:
                data = result[1]
            else:
                #Based in Kai Plugin: https://github.com/matiasb/kai
                data = sorted(set(re.split('\W+', code)))
                if final_word in data:
                    data.remove(final_word)
        return data


text = """
a = "diego"
b = a.split()

import os

r = os.p

from PyQt4 import QtGui

c = QtGui.Q

q = self.diego("casa",
    "diego")

mamamia = 2

class Diego:

    def __init__(self):
        self.s = {}
        self.m = 5
        self.w = QtGui.QWidget()

    def imprimir(self):
        pass

    def otra(self):
        l = []
        if algo:
            self.w."""

#offset = 21
#offset = 47
#offset = 85
#print len(text)
#print text[:offset]

#cc = CodeCompletion()
#cc.analyze_file('path', text)
#offset = len(text)
#print cc.get_completion(text, offset)
