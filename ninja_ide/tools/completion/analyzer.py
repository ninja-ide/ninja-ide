# -*- coding: utf-8 *-*

# DISCLAIMER ABOUT READING THIS CODE:
# We are not responsible for any kind of mental or emotional
# damage that may arise from reading this code.

import ast
import _ast
import logging

from ninja_ide.tools.completion import model


logger = logging.getLogger('ninja_ide.tools.completion.analyzer')

MODULES = {}


def expand_attribute(attribute):
    parent_name = []
    while attribute.__class__ is ast.Attribute:
        parent_name.append(attribute.attr)
        attribute = attribute.value
    name = '.'.join(reversed(parent_name))
    attribute_id = ''
    if attribute.__class__ is ast.Name:
        attribute_id = attribute.id
    elif attribute.__class__ is ast.Call:
        attribute_id = attribute.func.id
    name = attribute_id if name == '' else ("%s.%s" % (attribute_id, name))
    return name


class Analyzer(object):

    __mapping = {
        _ast.Tuple: '__builtin__.tuple',
        _ast.List: '__builtin__.list',
        _ast.Str: '__builtin__.str',
        _ast.Dict: '__builtin__.dict',
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

    def collect_metadata(self, project_path):
        """Collect metadata from a project."""
        #TODO

    def _get_valid_module(self, source, retry=True):
        """Try to parse the module and fix some errors if it has some."""
        astModule = None
        try:
            astModule = ast.parse(source)
        except SyntaxError, reason:
            line = reason.lineno - 1
            if line != self._fixed_line:
                self._fixed_line = line
                new_line = ''
                #This is failing sometimes, it should remaing commented
                #until we find the proper fix.
#                indent = re.match('^\s+', reason.text)
#                if indent is not None:
#                    new_line = indent.group() + 'pass'
                split_source = source.splitlines()
                split_source[line] = new_line
                source = '\n'.join(split_source)
                if retry:
                    astModule = self._get_valid_module(source, False)
        return astModule

    def _resolve_late(self, module):
        """Resolve the late_resolution objects inside the module."""

    def analyze(self, source):
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
#        self.resolve_late(module)

        self.content = None
        return module

    def _assign_disambiguation(self, type_name, line_content):
        """Provide a specific builtin for the cases were ast doesn't work."""
        line = line_content.split('=')
        value = line[1].strip()
        # TODO: We have to analyze when the assign is: x,y = 1, 2
        if type_name is _ast.Num and '.' in value:
            type_name = '_ast.Float'
        elif value in ('True', 'False'):
            type_name = '_ast.Bool'
        return type_name

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
            data_type = self.__mapping.get(type_value, None)
            if var.__class__ == ast.Attribute:
                data = (var.attr, symbol.lineno, data_type, line_content,
                    type_value)
                attributes.append(data)
            elif var.__class__ == ast.Name:
                data = (var.id, symbol.lineno, data_type, line_content,
                    type_value)
                assigns.append(data)
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
            name = expand_attribute(base)
            clazz.bases.append(name)
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
            try:
                if arg.id == 'self':
                    continue
            except Exception, reason:
                logger.error('_process_function, error: %r' % reason)
                logger.error('line number: %d' % symbol.lineno)
                logger.error('line: %s' % self.content[symbol.lineno])
                logger.error('source: \n%s' % ''.join(self.content))
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
