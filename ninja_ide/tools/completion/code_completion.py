# -*- coding: utf-8 *-*

# DISCLAIMER ABOUT READING THIS CODE:
# We are not responsible for any kind of mental or emotional
# damage that may arise from reading this code.

import re
import token as tkn
from tokenize import generate_tokens, TokenError
from StringIO import StringIO

from ninja_ide.core import settings
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
        self.keywords = settings.SYNTAX['python']['keywords']

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
        # TODO Optimization, only iterate until the previous line of a class??
        token_code = []
        try:
            for tkn_type, tkn_str, pos, _, line, \
                in generate_tokens(StringIO(code).readline):
                token_code.append((tkn_type, tkn_str, pos, line))
        except TokenError:
            #This is an expected situation, where i don't want to do anything
            #possible an unbalanced brace like: func(os.p| (| = cursor-end)
            pass
        while token_code[-1][0] in (tkn.ENDMARKER, tkn.DEDENT, tkn.NEWLINE):
            token_code.pop()
        return token_code

    def _search_for_scope(self, token_code):
        if not token_code[-1][3].startswith(' '):
            return None
        scopes = []
        indent = self.patIndent.match(token_code[-1][3])
        if indent is not None:
            indent = len(indent.group())
        else:
            indent = 0
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
                    #We need the "previous_line" because we are exploring
                    #the tokens backwards, and when we reach to def or class
                    #the actual name was in the line before.
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
            try:
                value = iter.next()
            except:
                keep_iter = False
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

    def get_prefix(self, code, offset):
        token_code = self._tokenize_text(code[:offset])
        var_segment = self._search_for_completion_segment(token_code)
        words_final = var_segment.rsplit('.', 1)
        final_word = ''
        if not var_segment.endswith('.') and len(words_final) > 1:
            final_word = words_final[1].strip()
        return final_word

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
            prefix = attr_name
            if result[1] != attr_name:
                prefix = result[1]
                word = final_word
            to_complete = "%s.%s" % (prefix, word)
            items = completer.get_all_completions(to_complete, imports)
            data = {'attributes': [], 'functions': items}
        else:
            if result[1] is not None and len(result[1]) > 0:
                data = {'attributes': result[1][0],
                    'functions': result[1][1]}
            else:
                clazzes = sorted(set(re.findall("class (\w+?)\(", code)))
                funcs = sorted(set(re.findall("(\w+?)\(", code)))
                attrs = sorted(set(re.split('\W+', code)))
                if final_word in attrs:
                    attrs.remove(final_word)
                filter_attrs = lambda x: (x not in funcs) and \
                    not x.isdigit() and (x not in self.keywords)
                attrs = filter(filter_attrs, attrs)
                funcs = filter(lambda x: x not in clazzes, funcs)
                data = {'attributes': attrs,
                    'functions': funcs,
                    'classes': clazzes}
        return data
