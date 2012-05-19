# -*- coding: utf-8 *-*


late_resolution = object()


class _TypeData(object):

    def __init__(self, lineno, data_type, line_content, oper):
        self.lineno = lineno
        self.data_type = data_type
        self.line_content = line_content
        if data_type != late_resolution:
            oper = None
        self.operation = oper
        self.from_import = False
        if isinstance(data_type, str):
            self.is_native = True
        else:
            self.is_native = False

    def get_data_type(self):
        return self.data_type


class Structure(object):

    def __init__(self):
        self.attributes = {}
        self.functions = {}

    def add_function(self, function):
        self.functions[function.name] = function

    def add_attributes(self, attributes):
        #attributes = {name: [(lineno, type),...]}
        for attribute in attributes:
            if attribute[0] in self.attributes:
                assign = self.attributes[attribute[0]]
            else:
                assign = Assign(attribute[0])
            assign.add_data(*attribute[1:])
            self.attributes[assign.name] = assign

    def get_attribute_type(self, name):
        """Return a tuple with:(Found, Type)"""
        result = (False, None)
        var_names = name.split('.')
        attr = self.attributes.get(var_names[0], None)
        if attr is not None:
            result = (True, attr.get_data_type())
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
        result = (False, None)
        structure = self._get_scope_structure(structure, scope)
        if structure:
            attr_name = attrs[0]
            data_type = structure.get_attribute_type(attr_name)
            result = data_type
#            print 'assign', assign
#            if assign is not None:
#                result = self._resolve_attribute(assign, attrs[1:])
        return result


class Module(Structure):

    def __init__(self):
        super(Module, self).__init__()
        self.imports = {}
        self.classes = {}

    def add_imports(self, imports):
        for imp in imports:
            line_content = "import %s" % imp[1]
            info = _TypeData(None, imp[1], line_content, None)
            self.imports[imp[0]] = info

    def add_class(self, clazz):
        self.classes[clazz.name] = clazz

    def get_type(self, main_attr, child_attrs='', scope=None):
        result = (False, None)
        if scope is None:
            value = self.imports.get(main_attr,
                self.attributes.get(main_attr, None))
            if value is not None:
                result = (True, value.get_data_type())
        elif main_attr == 'self':
            clazz_name = scope[0]
            clazz = self.classes.get(clazz_name, None)
            if clazz is not None:
                result = clazz.get_attribute_type(child_attrs)
            if child_attrs == '' and clazz is not None:
                items = clazz.get_completion_items()
                result = (False, items)
        else:
            scope_name = scope[0]
            structure = self.classes.get(scope_name,
                self.functions.get(scope_name, None))
            if structure is not None:
                attrs = [main_attr] + child_attrs.split('.')
                if len(attrs) > 1 and attrs[1] == '':
                    del attrs[1]
                result = self.recursive_search_type(
                    structure, attrs, scope[1:])
                if not result[0]:
                    value = self.imports.get(main_attr,
                        self.attributes.get(main_attr, None))
                    if value is not None:
                        result = (True, value.get_data_type())
        return result

    def get_imports(self):
        module_imports = ['import __builtin__']
        for name in self.imports:
            module_imports.append(self.imports[name].line_content)
        return module_imports


class Clazz(Structure):

    def __init__(self, name):
        super(Clazz, self).__init__()
        self.name = name
        self.bases = []
        self.decorators = []

    def get_completion_items(self):
        attributes = [a for a in self.attributes]
        functions = [f for f in self.functions]
        if attributes or functions:
            attributes.sort()
            functions.sort()
            return (attributes, functions)
        return None


class Function(Structure):

    def __init__(self, name):
        super(Function, self).__init__()
        self.name = name
        self.args = {}
        self.decorators = []
        self.return_type = []

    def add_return(self, lineno, data_type, line_content, oper):
        info = _TypeData(lineno, data_type, line_content, oper)
        self.return_type.append(info)


class Assign(object):

    def __init__(self, name):
        self.name = name
        self.data = []

    def add_data(self, lineno, data_type, line_content, oper):
        info = _TypeData(lineno, data_type, line_content, oper)
        self.data.append(info)

    def get_data_type(self):
        if self.data[0].is_native:
            return self.data[0].data_type
        else:
            return None
