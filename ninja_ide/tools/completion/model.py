# -*- coding: utf-8 *-*


class _TypeData(object):

    def __init__(self, lineno, data_type, line_content, oper):
        self.lineno = lineno
        self.data_type = data_type
        self.line_content = line_content
        self.operation = oper

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
        result = (False, None)
        var_names = name.split('.')
        attr = self.attributes.get(var_names[0], None)
        if attr is not None:
            result = (True, attr.get_data_type())
        else:
            items = self.get_completion_items()
            result = (False, items)
        return result

    def recursive_search_type(self):
        return (False, None)


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
        elif main_attr == 'self' and scope is not None:
            clazz_name = scope[-1]
            clazz = self.classes.get(clazz_name, None)
            if clazz is not None:
                result = clazz.get_attribute_type(child_attrs)
        elif scope is not None:
            func_name = scope[-1]
            func = self.functions.get(func_name, None)
            if func is not None:
                result = func.get_attribute_type(child_attrs)
        return result

    def recursive_search_type(self):
        return (False, None)

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
        return attributes + functions


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
        return self.data[0].data_type
