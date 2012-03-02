# -*- coding: utf-8 *-*


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


class Module(Structure):

    def __init__(self):
        super(Module, self).__init__()
        self.imports = {}
        self.classes = {}

    def add_class(self, clazz):
        self.classes[clazz.name] = clazz

    def get_type(self, name):
        print self.attributes
        assign = self.attributes.get(name, None)
        print 'assign', assign
        if assign is not None:
            return assign.get_name_type()


class Clazz(Structure):

    def __init__(self, name):
        super(Clazz, self).__init__()
        self.name = name
        self.bases = []
        self.decorators = []


class _TypeData(object):

    def __init__(self, lineno, data_type, line_content, oper):
        self.lineno = lineno
        self.data_type = data_type
        self.line_content = line_content
        self.operation = oper


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

    def get_name_type(self):
        return self.data[0].data_type
