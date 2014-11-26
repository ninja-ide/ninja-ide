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

import ast


MODULES = None
late_resolution = 0


def filter_data_type(data_types):
    occurrences = {}
    for type_ in data_types:
        if isinstance(type_, basestring):
            item = occurrences.get(type_, [0, type_])
            item[0] += 1
            occurrences[type_] = item
        else:
            item = occurrences.get(type_, [0, type_])
            item[0] += 1
            occurrences[type_.name] = item
    values = [occurrences[key][0] for key in occurrences]
    maximum = max(values)
    data_type = [occurrences[key][1] for key in occurrences
                if occurrences[key][0] == maximum]
    return data_type[0]


def remove_function_arguments(line):
    #TODO: improve line analysis using tokenizer to get the lines of the text
    while line.find('(') != -1:
        start = line.find('(')
        end = line.find(')') + 1
        if start == -1 or end == 0 or end <= start:
            break
        line = line[:start] + line[end:]
    return line


class TypeData(object):

    def __init__(self, lineno, data_type, line_content):
        self.lineno = lineno
        self.data_type = data_type
        self.line_content = line_content
        #if data_type != late_resolution:
            #oper = None
        #self.operation = oper
        #self.from_import = False
        if isinstance(data_type, str):
            self.is_native = True
        else:
            self.is_native = False
        #self.can_resolve = True

    def get_data_type(self):
        return self.data_type

    def __eq__(self, other):
        return other.line_content == self.line_content

    def __repr__(self):
        return repr(self.data_type)


class Structure(object):

    def __init__(self):
        self.attributes = {}
        self.functions = {}
        self.parent = None

    def add_function(self, function):
        function.parent = self
        self.functions[function.name] = function

    def add_attributes(self, attributes):
        #attributes = {name: [(lineno, type),...]}
        for attribute in attributes:
            if attribute[0] in self.attributes:
                assign = self.attributes[attribute[0]]
            else:
                assign = Assign(attribute[0])
            assign.add_data(*attribute[1:])
            assign.parent = self
            self.attributes[assign.name] = assign

    def update_attributes(self, attributes):
        for name in self.attributes:
            if name in attributes:
                assign = self.attributes[name]
                old_assign = attributes[name]
                for type_data in assign.data:
                    if type_data in old_assign.data:
                        old_type = old_assign.data[
                            old_assign.data.index(type_data)]
                        if old_type.data_type.__class__ is not Clazz:
                            type_data.data_type = old_type.data_type

    def update_functions(self, functions):
        for func_name in self.functions:
            if func_name in functions:
                old_func = functions[func_name]
                if old_func.__class__ is Assign:
                    continue
                function = self.functions[func_name]
                function.update_functions(old_func.functions)
                function.update_attributes(old_func.attributes)
                # Function Arguments
                for arg in function.args:
                    if arg in old_func.args:
                        argument_type = function.args[arg].data[0]
                        old_type = old_func.args[arg].data[0]
                        argument_type.data_type = old_type.data_type
                # Function Returns
                for type_data in function.return_type:
                    if type_data in old_func.return_type:
                        old_type = old_func.return_type[
                            old_func.return_type.index(type_data)]
                        type_data.data_type = old_type.data_type

    def get_attribute_type(self, name):
        """Return a tuple with:(Found, Type)"""
        result = {'found': False, 'type': None}
        var_names = name.split('.')
        attr = self.attributes.get(var_names[0], None)
        if attr is not None:
            result['found'], result['type'] = True, attr.get_data_type()
        elif self.parent.__class__ is Function:
            result = self.parent.get_attribute_type(name)
        return result

    def _get_scope_structure(self, structure, scope):
        struct = structure
        if len(scope) > 0:
            scope_name = scope[0]
            new_struct = structure.functions.get(scope_name, None)
            struct = self._get_scope_structure(new_struct, scope[1:])
        return struct

    def _resolve_attribute(self, type_data, attrs):
        object_type = type_data.get_data_type()
        return (True, object_type)

    def recursive_search_type(self, structure, attrs, scope):
        result = {'found': False, 'type': None}
        structure = self._get_scope_structure(structure, scope)
        if structure and structure.__class__ is not Assign:
            attr_name = attrs[0]
            data_type = structure.get_attribute_type(attr_name)
            result = data_type
        return result


class Module(Structure):

    def __init__(self):
        super(Module, self).__init__()
        self.imports = {}
        self.classes = {}

    def add_imports(self, imports):
        for imp in imports:
            line_content = "import %s" % imp[1]
            info = TypeData(None, imp[1], line_content, None)
            self.imports[imp[0]] = info

    def add_class(self, clazz):
        clazz.parent = self
        self.classes[clazz.name] = clazz

    def update_classes(self, classes):
        for clazz_name in self.classes:
            if clazz_name in classes:
                clazz = self.classes[clazz_name]
                clazz.update_functions(classes[clazz_name].functions)
                clazz.update_attributes(classes[clazz_name].attributes)

    def get_type(self, main_attr, child_attrs='', scope=None):
        result = {'found': False, 'type': None}
        canonical_attrs = remove_function_arguments(child_attrs)
        if not scope:
            value = self.imports.get(main_attr,
                self.attributes.get(main_attr,
                self.functions.get(main_attr,
                self.classes.get(main_attr, None))))
            if value is not None and value.__class__ is not Clazz:
                data_type = value.get_data_type()
                result['found'], result['type'] = True, data_type
                if child_attrs or (isinstance(data_type, basestring) and
                   data_type.endswith(main_attr)):
                    result['main_attr_replace'] = True
            elif value.__class__ is Clazz:
                result['found'], result['type'] = False, value
        elif main_attr == 'self':
            clazz_name = scope[0]
            clazz = self.classes.get(clazz_name, None)
            if clazz is not None:
                result = clazz.get_attribute_type(canonical_attrs)
            if canonical_attrs == '' and clazz is not None:
                items = clazz.get_completion_items()
                result['found'], result['type'] = False, items
        elif scope:
            scope_name = scope[0]
            structure = self.classes.get(scope_name,
                self.functions.get(scope_name, None))
            if structure is not None:
                attrs = [main_attr] + canonical_attrs.split('.')
                if len(attrs) > 1 and attrs[1] == '':
                    del attrs[1]
                result = self.recursive_search_type(
                    structure, attrs, scope[1:])
                if not result['found']:
                    value = self.imports.get(main_attr,
                        self.attributes.get(main_attr,
                        self.functions.get(main_attr, None)))
                    if value is not None:
                        data_type = value.get_data_type()
                        result['found'], result['type'] = True, data_type

        if result['type'].__class__ is Clazz:
            if canonical_attrs:
                attrs = canonical_attrs.split('.')
                if attrs[-1] == '':
                    attrs.pop(-1)
                result = self._search_type(result['type'], attrs)
            else:
                result = {'found': False,
                          'type': result['type'].get_completion_items(),
                          'object': result['type']}
        elif result['type'].__class__ is LinkedModule:
            if main_attr == 'self':
                attrs = canonical_attrs.split('.', 1)
                canonical_attrs = ''
                if len(attrs) > 1:
                    canonical_attrs = attrs[1]
            result = result['type'].get_type(canonical_attrs)

        return result

    def _search_type(self, structure, attrs):
        result = {'found': False, 'type': None}
        if not attrs:
            return result
        attr = attrs[0]
        value = structure.attributes.get(attr,
            structure.functions.get(attr, None))
        if value is None:
            return result
        data_type = value.get_data_type()
        if data_type.__class__ is Clazz and len(attrs) > 1:
            result = self._search_type(data_type, attrs[1:])
        elif data_type.__class__ is Clazz:
            items = data_type.get_completion_items()
            result['found'], result['type'] = False, items
            result['object'] = data_type
        elif isinstance(data_type, basestring):
            result['found'], result['type'] = True, data_type
            result['object'] = data_type
        return result

    def get_imports(self):
        module_imports = ['import __builtin__']
        for name in self.imports:
            module_imports.append(self.imports[name].line_content)
        return module_imports

    def need_resolution(self):
        if self._check_attr_func_resolution(self):
            return True
        for cla in self.classes:
            clazz = self.classes[cla]
            for parent in clazz.bases:
                if clazz.bases[parent] is None:
                    return True
            if self._check_attr_func_resolution(clazz):
                return True
        return False

    def _check_attr_func_resolution(self, structure):
        for attr in structure.attributes:
            attribute = structure.attributes[attr]
            for d in attribute.data:
                if d.data_type == late_resolution:
                    return True
        for func in structure.functions:
            function = structure.functions[func]
            for attr in function.attributes:
                attribute = function.attributes[attr]
                for d in attribute.data:
                    if d.data_type == late_resolution:
                        return True
            for ret in function.return_type:
                if ret.data_type == late_resolution:
                    return True
        return False


class Clazz(Structure):

    def __init__(self, name):
        super(Clazz, self).__init__()
        self.name = name
        self.bases = {}
        self._update_bases = []
#        self.decorators = []

    def add_parent(self, parent):
        self._update_bases.append(parent)
        value = self.bases.get(parent, None)
        if value is None:
            self.bases[parent] = None

    def update_bases(self):
        to_remove = []
        for parent in self.bases:
            if parent not in self._update_bases:
                to_remove.append(parent)
        for remove in to_remove:
            self.bases.pop(parent)

    def get_completion_items(self):
        attributes = [a for a in self.attributes]
        functions = [f for f in self.functions]
        if attributes or functions:
            attributes.sort()
            functions.sort()
            return {'attributes': attributes, 'functions': functions}
        return None

    def update_with_parent_data(self):
        for base in self.bases:
            parent = self.bases[base]
            if parent.__class__ is Clazz:
                self.attributes.update(parent.attributes)
                self.functions.update(parent.functions)
                self.bases[base] = None
            elif isinstance(parent, tuple):
                parent_name = parent[0]
                data = parent[1]
                attributes = {}
                functions = {}
                for attr in data.get('attributes', []):
                    if attr[:2] == '__' and attr[-2:] == '__':
                        continue
                    assign = Assign(attr)
                    assign.add_data(0, parent_name + attr, '',
                        parent_name + attr)
                    attributes[attr] = assign
                for func in data.get('functions', []):
                    if func[:2] == '__' and func[-2:] == '__':
                        continue
                    assign = Assign(func)
                    assign.add_data(0, parent_name + attr, '',
                        parent_name + attr)
                    functions[func] = assign
                self.attributes.update(attributes)
                self.functions.update(functions)


class Function(Structure):

    def __init__(self, name):
        super(Function, self).__init__()
        self.name = name
        self.args = {}
        self.decorators = []
        self.return_type = []

    def add_return(self, lineno, data_type, line_content, oper):
        info = TypeData(lineno, data_type, line_content, oper)
        if info not in self.return_type:
            self.return_type.append(info)

    def get_data_type(self):
        possible = [d.data_type for d in self.return_type
                    if d.data_type is not late_resolution and
                    d.data_type is not None]
        if possible:
            return filter_data_type(possible)
        else:
            return None


class Assign(object):

    def __init__(self, name):
        self.name = name
        self.data = []
        self.parent = None

    def add_data(self, lineno, data_type, line_content, oper):
        info = TypeData(lineno, data_type, line_content, oper)
        if info not in self.data:
            self.data.append(info)

    def get_data_type(self):
        possible = [d.data_type for d in self.data
                    if d.data_type is not late_resolution]
        if possible:
            return filter_data_type(possible)
        else:
            return None


class LinkedModule(object):

    def __init__(self, path, attrs):
        self.name = path
        self.resolve_attrs = remove_function_arguments(attrs)

    def get_type(self, resolve=''):
        result = {'found': False, 'type': None}
        global MODULES
        module = MODULES.get(self.name, None)
        if module:
            if resolve:
                to_resolve = "%s.%s" % (self.resolve_attrs, resolve)
            else:
                to_resolve = self.resolve_attrs
            to_resolve = to_resolve.split('.', 1)
            main_attr = to_resolve[0]
            child_attr = ''
            if len(to_resolve) == 2:
                child_attr = to_resolve[1]
            result = module.get_type(main_attr, child_attr)
        return result


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
        if attribute.func.__class__ is ast.Attribute:
            attribute_id = '%s.%s()' % (
                expand_attribute(attribute.func.value),
                attribute.func.attr)
        else:
            attribute_id = '%s()' % attribute.func.id
    name = attribute_id if name == '' else ("%s.%s" % (attribute_id, name))
    return name


#class Structure(object):

##   def __init__(self, parent=None):
        #super(Module, self).__init__()
        #self._parent = parent
        #self.attributes = {}
        #self.functions = {}

##   def create_function(self, symbol):
        #return Function(symbol, self)

##   def create_attribute(self, symbol):
        #pass

##class Module(Structure):

##   def __init__(self):
        #super(Module, self).__init__()
        #self.imports = {}
        #self.clazzes = {}

##   def create_class(self, symbol):
        #return Clazz(symbol, self)

##class Clazz(Structure):

##   def __init__(self, symbol, parent):
        #super(Clazz, self).__init__(parent)
        #self.bases = {}
        #for base in symbol.bases:
            #if base == 'object':
                #continue
            #name = expand_attribute(base)
            #value = self.bases.get(name, None)
            #if value is None:
                #self.bases[name] = value

##   def close_class(self):
        #return self._parent

##class Function(Structure):

##    def __init__(self, symbol, parent):
        #super(Function, self).__init__(parent)
        #self.name = symbol.name
        #self.args = {}
        #self.decorators = []
        #self.return_type = []

##        for decorator in symbol.decorator_list:
            ##Decorators can be: Name, Call, Attributes
            #self.decorators.append(decorator.id)

##        if symbol.args.vararg is not None:
            #assign = Assign(symbol.args.vararg)
            #assign.add_data(symbol.lineno, '__builtin__.list', None, None)
            #self.args[assign.name] = assign
        #if symbol.args.kwarg is not None:
            #assign = Assign(symbol.args.kwarg)
            #assign.add_data(symbol.lineno, '__builtin__.dict', None, None)
            #self.args[assign.name] = assign
        ##We store the arguments to compare with default backwards
        #defaults = []
        #for value in symbol.args.defaults:
            ##TODO: In some cases we can have something like: a=os.path
            #type_value = value.__class__
            #data_type = self.__mapping.get(type_value, None)
            #defaults.append((data_type, type_value))
        #for arg in reversed(symbol.args.args):
            #if isinstance(arg, ast.Tuple):
                #self._parse_tuple_in_func_arg(arg, symbol.lineno)
                #continue
            #elif arg.id == 'self':
                #continue
            #assign = Assign(arg.id)
            #data_type = (late_resolution, None)
            #if defaults:
                #data_type = defaults.pop()
            #assign.add_data(symbol.lineno, data_type[0], None, data_type[1])
            #self.args[assign.name] = assign

##    def _parse_tuple_in_func_arg(self, symbol_tuple, lineno=0):
        #"""Parse the tuple inside a function argument call."""
        #for item in symbol_tuple.elts:
            #assign = Assign(item.id)
            #data_type = (late_resolution, None)
            #assign.add_data(lineno, data_type[0], None, data_type[1])
            #self.args[assign.name] = assign

##    def close_function(self):
        #return self._parent

##class Assign(object):

##   def __init__(self, symbol, line_content=''):
        #super(Assign, self).__init__()
        #self.name = symbol.name
        #self.data = []
        #self.add_symbol(symbol, line_content)

##   def add_symbol(self, symbol, line_content=''):
        #for var in symbol.targets:
            #type_value = symbol.value.__class__
            #line_content = self.content[symbol.lineno - 1]
            #if type_value in (_ast.Num, _ast.Name):
                #type_value = self._assign_disambiguation(
                    #type_value, line_content)
                #if type_value is None:
                    #continue
            #data_type = self.__mapping.get(type_value, model.late_resolution)
            #if var.__class__ == ast.Attribute:
                #data = (var.attr, symbol.lineno, data_type, line_content,
                    #type_value)
                #attributes.append(data)
            #elif var.__class__ == ast.Name:
                #data = (var.id, symbol.lineno, data_type, line_content,
                    #type_value)
                #assigns.append(data)
##            if type_value is ast.Call:
##                self._process_expression(symbol.value)
        #return (assigns, attributes)
        ##info = TypeData(symbol.lineno, data_type, line_content)
        ##if info not in self.data:
            ##self.data.append(info)

##   def get_data_type(self):
        #possible = [d.data_type for d in self.data
                    #if d.data_type is not late_resolution]
        #if possible:
            #return filter_data_type(possible)
        #else:
            #return None