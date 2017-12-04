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

# DISCLAIMER ABOUT READING THIS CODE:
# We are not responsible for any kind of mental or emotional
# damage that may arise from reading this code.

import re
import token as tkn
from tokenize import generate_tokens, TokenError
try:
    from StringIO import StringIO
except:
    from io import StringIO  # lint:ok

from ninja_ide.core import settings
from ninja_ide.gui.editor import helpers
from ninja_ide.intellisensei.analyzer import model
from ninja_ide.intellisensei.analyzer import analyzer
from ninja_ide.intellisensei.analyzer import analyzer_daemon


#Because my python doesn't have it, and is not in the web docs either
#but trust me, it exists!
_TOKEN_NL = 54


class CodeCompletion(object):

    def __init__(self):
        self.analyzer = analyzer.Analyzer()
        self.cdaemon = analyzer_daemon.CompletionDaemon()
        # Set modules reference to model
        model.MODULES = self.cdaemon.modules
        self.module_id = None
        self.patIndent = re.compile('^\s+')
        self.patClass = re.compile("class (\w+?)\(")
        self.patFunction = re.compile("(\w+?)\(")
        self.patWords = re.compile('\W+')
        self._valid_op = (')', '}', ']')
        self._invalid_op = ('(', '{', '[')
        self._invalid_words = ('if', 'elif', 'for', 'while', 'in', 'return',
            'and', 'or', 'del', 'except', 'from', 'import', 'is', 'print',
            'super', 'yield')
        self.keywords = settings.SYNTAX['python']['keywords']

    def unload_module(self):
        self.cdaemon.unload_module(self.module_id)

    def analyze_file(self, path, source=None, indent=settings.INDENT,
        useTabs=settings.USE_TABS):
        if source is None:
            with open(path) as f:
                source = f.read()
        split_last_lines = source.rsplit('\n', 2)
        if len(split_last_lines) > 1 and \
           split_last_lines[-2].endswith(':') and split_last_lines[-1] == '':
            indent = helpers.get_indentation(split_last_lines[-2], indent,
                useTabs)
            source += '%spass;' % indent

        self.module_id = path
        if not self.cdaemon.daemon.is_alive():
            completion_daemon.shutdown_daemon()
            del self.cdaemon
            self.cdaemon = completion_daemon.CompletionDaemon()
            # Set modules reference to model
            model.MODULES = self.cdaemon.modules
        module = self.cdaemon.get_module(self.module_id)
        module = self.analyzer.analyze(source, module)
        self.cdaemon.inspect_module(self.module_id, module)

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
        except IndentationError:
            return []
        while token_code[-1][0] in (tkn.ENDMARKER, tkn.DEDENT, tkn.NEWLINE):
            token_code.pop()
        return token_code

    def _search_for_scope(self, token_code):
        if not token_code or not token_code[-1][3].startswith(' '):
            return None
        scopes = []
        indent = self.patIndent.match(token_code[-1][3])
        if indent is not None:
            indent = len(indent.group())
        else:
            indent = 0
        previous_line = ('', '')
        keep_exploring = True
        iterate = reversed(token_code)
        line = iterate.next()
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
                line = iterate.next()
            except StopIteration:
                keep_exploring = False
        return scopes

    def _search_for_completion_segment(self, token_code):
        tokens = []
        keep_iter = True
        iterate = reversed(token_code)
        while keep_iter:
            try:
                value = iterate.next()
                if value[0] in (tkn.NEWLINE, tkn.INDENT, tkn.DEDENT):
                    keep_iter = False
                tokens.append(value)
            except:
                keep_iter = False
        segment = ''
        brace_stack = 0
        first_element = True
        for t in tokens:
            token_str = t[1]
            if token_str in self._invalid_words and not first_element:
                break
            elif token_str in self._valid_op:
                if brace_stack == 0:
                    segment = token_str + segment
                brace_stack += 1
            elif token_str in self._invalid_op:
                brace_stack -= 1
                if brace_stack == 0:
                    segment = token_str + segment
                    continue
            first_element = False
            if brace_stack != 0:
                continue

            op = t[0]
            if (op == tkn.NAME) or token_str == '.':
                segment = token_str + segment
            elif op == tkn.OP:
                break
        return segment

    def get_prefix(self, code, offset):
        """Return the prefix of the word under the cursor and a boolean
        saying if it is a valid completion area."""
        token_code = self._tokenize_text(code[:offset])
        var_segment = self._search_for_completion_segment(token_code)
        words_final = var_segment.rsplit('.', 1)
        final_word = ''
        if not var_segment.endswith('.') and len(words_final) > 1:
            final_word = words_final[1].strip()
        elif (var_segment != "") and len(words_final) == 1:
            final_word = words_final[0].strip()
        return final_word, (var_segment != "")

    def get_completion(self, code, offset):
        token_code = self._tokenize_text(code[:offset])
        scopes = self._search_for_scope(token_code)
        # Find section to attempt for code completion (var_segment)
        var_segment = self._search_for_completion_segment(token_code)
        words = var_segment.split('.', 1)
        words_final = var_segment.rsplit('.', 1)
        # Main_attribute is the stem off of which to search for completions
        # i.e. in exec(ninja_ide.gui. ..., "ninja_ide.gui.main_panel"
        # would be main_attribute.
        main_attribute = words[0].strip().split('(', 1)
        attr_name = main_attribute[0]
        word = ''
        final_word = ''
        if var_segment.count(".") > 0:
            word = words[1].strip()
        if not var_segment.endswith('.') and len(words_final) > 1:
            final_word = words_final[1].strip()
            word = word.rsplit('.', 1)[0].strip()
            if final_word == word:
                word = ''
        self.cdaemon.lock.acquire()
        module = self.cdaemon.get_module(self.module_id)
        if module:
            imports = module.get_imports()
            result = module.get_type(attr_name, word, scopes)
        else:
            result = {'found': False, 'type': None}
        self.cdaemon.lock.release()
        if result['found'] and result['type'] is not None:
            prefix = attr_name
            if result['type'] != attr_name:
                prefix = result['type']
                word = final_word
            to_complete = "%s.%s" % (prefix, word)
            if result.get('main_attr_replace', False):
                to_complete = var_segment.replace(attr_name, result['type'], 1)
            imports = [imp.split('.')[0] for imp in imports]
            data = completer.get_all_completions(to_complete, imports)
            # Move system attributes beginning in '__' (built_in_attribs)
            # to the end of the list.
            built_in_attribs = [d for d in data.get('attributes', [])
                if d[:2] == '__']
            if built_in_attribs:
                for i in built_in_attribs:
                    data['attributes'].remove(i)
                data['attributes'] += built_in_attribs
            if data:
                return data
            else:
                result = {'found': None, 'type': None}

        if result['type'] is not None and len(result['type']) > 0:
            data = {'attributes': result['type']['attributes'],
                'functions': result['type']['functions']}
        else:
            clazzes = sorted(set(self.patClass.findall(code)))
            funcs = sorted(set(self.patFunction.findall(code)))
            attrs = sorted(set(self.patWords.split(code)))
            if final_word in attrs:
                attrs.remove(final_word)
            if attr_name in attrs:
                attrs.remove(attr_name)
            filter_attrs = lambda x: (x not in funcs) and \
                not x.isdigit() and (x not in self.keywords)
            attrs = list(filter(filter_attrs, attrs))
            funcs = [x for x in funcs if x not in clazzes]
            data = {'attributes': attrs,
                'functions': funcs,
                'classes': clazzes}
        return data
