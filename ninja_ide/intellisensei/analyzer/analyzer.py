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
import ast
import _ast

from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.intellisensei.analyzer import model


logger = NinjaLogger('ninja_ide.tools.completion.analyzer')

MAX_THRESHOLD = 3


class Analyzer(object):

    __mapping = {
        _ast.Tuple: '__builtin__.tuple',
        _ast.List: '__builtin__.list',
        _ast.ListComp: '__builtin__.list',
        _ast.Set: '__builtin__.set',
        _ast.SetComp: '__builtin__.set',
        _ast.Str: '__builtin__.str',
        _ast.Dict: '__builtin__.dict',
        _ast.DictComp: '__builtin__.dict',
        _ast.Num: '__builtin__.int',
        '_ast.Float': '__builtin__.float',
        '_ast.Bool': '__builtin__.bool',
        _ast.Call: model.late_resolution,
        _ast.Name: model.late_resolution,
        _ast.Attribute: model.late_resolution,
    }

    def __init__(self):
        self._fixed_line = -1
        self.content = None
#        self._functions = {}

    def _get_valid_module(self, source, retry=0):
        """Try to parse the module and fix some errors if it has some."""
        astModule = None
        try:
            astModule = ast.parse(source)
            self._fixed_line = -1
        except SyntaxError as reason:
            line = reason.lineno - 1
            if line != self._fixed_line and reason.text is not None:
                self._fixed_line = line
                new_line = ''
                split_source = source.splitlines()
                indent = re.match('^\s+', str(split_source[line]))
                if indent is not None:
                    new_line = "%s%s" % (indent.group(), 'pass')
                split_source[line] = new_line
                source = '\n'.join(split_source)
                if retry < MAX_THRESHOLD:
                    astModule = self._get_valid_module(source, retry + 1)
        return astModule

    def analyze(self, source, old_module=None):
        """Analyze the source provided and create the proper structure."""
        astModule = self._get_valid_module(source)
        if astModule is None:
            return model.Module()
        self.content = source.split('\n')

        module = model.Module()
        for symbol in astModule.body:
            if symbol.__class__ is ast.Assign:
                assigns = self._process_assign(symbol)[0]
                module.add_attributes(assigns)
            elif symbol.__class__ in (ast.Import, ast.ImportFrom):
                module.add_imports(self._process_import(symbol))
            elif symbol.__class__ is ast.ClassDef:
                module.add_class(self._process_class(symbol))
            elif symbol.__class__ is ast.FunctionDef:
                module.add_function(self._process_function(symbol))
#            elif symbol.__class__ is ast.Expr:
#                self._process_expression(symbol.value)
        if old_module is not None:
            self._resolve_module(module, old_module)

        self.content = None
#        self._functions = {}
        return module

    def _resolve_module(self, module, old_module):
        module.update_classes(old_module.classes)
        module.update_functions(old_module.functions)
        module.update_attributes(old_module.attributes)

    def _assign_disambiguation(self, type_name, line_content):
        """Provide a specific builtin for the cases were ast doesn't work."""
        line = line_content.split('=')
        if len(line) < 2:
            logger.error('_assign_disambiguation, line not valid: %r' %
                line_content)
            return type_name
        value = line[1].strip()
        # TODO: We have to analyze when the assign is: x,y = 1, 2
        if type_name is _ast.Num and '.' in value:
            type_name = '_ast.Float'
        elif value in ('True', 'False'):
            type_name = '_ast.Bool'
        elif value == 'None':
            type_name = None
        return type_name

#    def _process_expression(self, expr):
#        """Process expression, not assignment."""
#        if expr.__class__ is not ast.Call:
#            return
#        args = expr.args
#        keywords = expr.keywords
#        ar = []
#        kw = {}
#        for arg in args:
#            type_value = arg.__class__
#            arg_name = ''
#            if type_value is ast.Call:
#                arg_name = expand_attribute(arg.func)
#            elif type_value is ast.Attribute:
#                arg_name = expand_attribute(arg.attr)
#            data_type = self.__mapping.get(type_value, model.late_resolution)
#            ar.append((arg_name, data_type))
#        for key in keywords:
#            type_value = key.value.__class__
#            data_type = self.__mapping.get(type_value, model.late_resolution)
#            kw[key.arg] = data_type
#        if expr.func.__class__ is ast.Attribute:
#            name = expand_attribute(expr.func)
#        else:
#            name = expr.func.id
#        self._functions[name] = (ar, kw)

    def _process_assign(self, symbol):
        """Process an ast.Assign object to extract the proper info."""
        assigns = []
        attributes = []
        for var in symbol.targets:
            type_value = symbol.value.__class__
            line_content = self.content[symbol.lineno - 1]
            if type_value in (_ast.Num, _ast.Name):
                type_value = self._assign_disambiguation(
                    type_value, line_content)
                if type_value is None:
                    continue
            data_type = self.__mapping.get(type_value, model.late_resolution)
            if var.__class__ == ast.Attribute:
                data = (var.attr, symbol.lineno, data_type, line_content,
                    type_value)
                attributes.append(data)
            elif var.__class__ == ast.Name:
                data = (var.id, symbol.lineno, data_type, line_content,
                    type_value)
                assigns.append(data)
#            if type_value is ast.Call:
#                self._process_expression(symbol.value)
        return (assigns, attributes)

    def _process_import(self, symbol):
        """Process an ast.Import and ast.ImportFrom object to extract data."""
        imports = []
        for imp in symbol.names:
            if symbol.__class__ is ast.ImportFrom:
                module_name = "%s.%s" % (symbol.module, imp.name)
            else:
                module_name = imp.name
            name = imp.asname
            if name is None:
                name = imp.name
            imports.append((name, module_name))
        return imports

    def _process_class(self, symbol):
        """Process an ast.ClassDef object to extract data."""
        clazz = model.Clazz(symbol.name)
        for base in symbol.bases:
            if base == 'object':
                continue
            name = expand_attribute(base)
            clazz.add_parent(name)
        #TODO: Decotator
#        for decorator in symbol.decorator_list:
#            clazz.decorators.append(decorator.id)
        # PARSE FUNCTIONS AND ATTRIBUTES
        for sym in symbol.body:
            if sym.__class__ is ast.Assign:
                assigns = self._process_assign(sym)[0]
                clazz.add_attributes(assigns)
            elif sym.__class__ is ast.FunctionDef:
                clazz.add_function(self._process_function(sym, clazz))
        clazz.update_bases()
        clazz.update_with_parent_data()
        return clazz

    def _process_function(self, symbol, parent=None):
        """Process an ast.FunctionDef object to extract data."""
        function = model.Function(symbol.name)
        #TODO: Decorators
        #We are not going to collect data from decorators yet.
#        for decorator in symbol.decorator_list:
            #Decorators can be: Name, Call, Attributes
#            function.decorators.append(decorator.id)
        if symbol.args.vararg is not None:
            assign = model.Assign(symbol.args.vararg)
            assign.add_data(symbol.lineno, '__builtin__.list', None, None)
            function.args[assign.name] = assign
        if symbol.args.kwarg is not None:
            assign = model.Assign(symbol.args.kwarg)
            assign.add_data(symbol.lineno, '__builtin__.dict', None, None)
            function.args[assign.name] = assign
        #We store the arguments to compare with default backwards
        defaults = []
        for value in symbol.args.defaults:
            #TODO: In some cases we can have something like: a=os.path
            type_value = value.__class__
            data_type = self.__mapping.get(type_value, None)
            defaults.append((data_type, type_value))
        for arg in reversed(symbol.args.args):
            if isinstance(arg, ast.Tuple):
                self._parse_tuple_in_func_arg(arg, function, symbol.lineno)
                continue
            elif arg.id == 'self':
                continue
            assign = model.Assign(arg.id)
            data_type = (model.late_resolution, None)
            if defaults:
                data_type = defaults.pop()
            assign.add_data(symbol.lineno, data_type[0], None, data_type[1])
            function.args[assign.name] = assign
        for sym in symbol.body:
            if sym.__class__ is ast.Assign:
                result = self._process_assign(sym)
                function.add_attributes(result[0])
                if parent is not None:
                    parent.add_attributes(result[1])
            elif sym.__class__ is ast.FunctionDef:
                function.add_function(self._process_function(sym))

            if sym.__class__ is not ast.Assign:
                self._search_recursive_for_types(function, sym, parent)

        return function

    def _parse_tuple_in_func_arg(self, symbol_tuple, function, lineno=0):
        """Parse the tuple inside a function argument call."""
        for item in symbol_tuple.elts:
            assign = model.Assign(item.id)
            data_type = (model.late_resolution, None)
            assign.add_data(lineno, data_type[0], None, data_type[1])
            function.args[assign.name] = assign

    def _search_recursive_for_types(self, function, symbol, parent=None):
        """Search for return recursively inside the function."""
        if symbol.__class__ is ast.Assign:
            result = self._process_assign(symbol)
            function.add_attributes(result[0])
            if parent is not None:
                parent.add_attributes(result[1])
        elif symbol.__class__ is ast.Return:
            type_value = symbol.value.__class__
            lineno = symbol.lineno
            data_type = self.__mapping.get(type_value, None)
            line_content = self.content[lineno - 1]
            if data_type != model.late_resolution:
                type_value = None
            function.add_return(lineno, data_type, line_content, type_value)
        elif symbol.__class__ in (ast.If, ast.For, ast.TryExcept):
            for sym in symbol.body:
                self._search_recursive_for_types(function, sym, parent)
            for else_item in symbol.orelse:
                self._search_recursive_for_types(function, else_item, parent)
        elif symbol.__class__ is ast.TryFinally:
            for sym in symbol.body:
                self._search_recursive_for_types(function, sym, parent)
            for else_item in symbol.finalbody:
                self._search_recursive_for_types(function, else_item, parent)
#        elif symbol.__class__ is ast.Expr:
#            self._process_expression(symbol.value)


class CodeParser(ast.NodeVisitor):

    def analyze(self, astmodule):
        self.module = model.Module()
        self.visit(astmodule)

    def visit_ClassDef(self, node):
        self.module = self.module.create_class(node)
        for item in node.body:
            self.visit(item)
        self.module = self.module.close_class()
        return node

    def visit_FunctionDef(self, node):
        self.module.create_function(node)
        for item in node.body:
            self.visit(item)
        self.module = self.module.close_function()
        return node

    def visit_Name(self, node):
        if node.id not in self.code_names:
            self.code_names.append(node.id)
        return node

    def visit_Attribute(self, node):
        if node.attr not in self.code_names:
            self.code_names.append(node.attr)
        return node