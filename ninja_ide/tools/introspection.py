# -*- coding: utf-8 -*-
import ast

import logging

from ninja_ide.tools.completion import analyzer


logger_imports = logging.getLogger(
    'ninja_ide.tools.introspection.obtaining_imports')
logger_symbols = logging.getLogger(
    'ninja_ide.tools.introspection.obtainint_symbols')


_FILE_CONTENT = None


def _parse_assign(symbol):
    assigns = {}
    attributes = {}
    for var in symbol.targets:
        if var.__class__ == ast.Attribute:
            attributes[var.attr] = var.lineno
        elif var.__class__ == ast.Name:
            assigns[var.id] = var.lineno
    return (assigns, attributes)


def _parse_class(symbol, with_docstrings):
    docstring = ''
    attr = {}
    func = {}
    name = symbol.name + '('
    name += ', '.join([
        analyzer.expand_attribute(base) for base in symbol.bases])
    name += ')'
    for sym in symbol.body:
        if sym.__class__ is ast.Assign:
            result = _parse_assign(sym)
            attr.update(result[0])
            attr.update(result[1])
        elif sym.__class__ is ast.FunctionDef:
            result = _parse_function(sym, with_docstrings)
            attr.update(result['attrs'])
            if with_docstrings:
                func[result['name']] = (result['lineno'], result['docstring'])
            else:
                func[result['name']] = result['lineno']
    if with_docstrings:
        docstring = ast.get_docstring(symbol, clean=True)
    return {'name': name, 'attributes': attr, 'functions': func,
        'lineno': symbol.lineno, 'docstring': docstring}


def _parse_function(symbol, with_docstrings):
    docstring = ''
    attrs = {}
    global _FILE_CONTENT
    line_pos = symbol.lineno - 1
    line = _FILE_CONTENT[line_pos]
    index = line.find('def')
    if index != -1:
        func_name = line[index + 3:].strip()
        line_pos += 1
        while not func_name.endswith(':') and (len(_FILE_CONTENT) > line_pos):
            func_name += ' ' + _FILE_CONTENT[line_pos].strip()
            line_pos += 1
        func_name = func_name[:-1]
        func_name = func_name.replace('\\', '')
    else:
        func_name = symbol.name + '()'

    for sym in symbol.body:
        if sym.__class__ is ast.Assign:
            result = _parse_assign(sym)
            attrs.update(result[1])

    if with_docstrings:
        docstring = ast.get_docstring(symbol, clean=True)

    return {'name': func_name, 'lineno': symbol.lineno,
        'attrs': attrs, 'docstring': docstring}


def obtain_symbols(source, with_docstrings=False):
    """Parse a module source code to obtain: Classes, Functions and Assigns."""
    try:
        module = ast.parse(source)
        global _FILE_CONTENT
        _FILE_CONTENT = source.splitlines()
    except:
        logger_symbols.debug("A file contains syntax errors.")
        return {}
    symbols = {}
    globalAttributes = {}
    globalFunctions = {}
    classes = {}
    docstrings = {}

    for symbol in module.body:
        if symbol.__class__ is ast.Assign:
            result = _parse_assign(symbol)
            globalAttributes.update(result[0])
            globalAttributes.update(result[1])
        elif symbol.__class__ is ast.FunctionDef:
            result = _parse_function(symbol, with_docstrings)
            if with_docstrings:
                globalFunctions[result['name']] = result['lineno']
                docstrings[result['lineno']] = result['docstring']
            else:
                globalFunctions[result['name']] = result['lineno']
        elif symbol.__class__ is ast.ClassDef:
            result = _parse_class(symbol, with_docstrings)
            classes[result['name']] = (result['lineno'],
                {'attributes': result['attributes'],
                'functions': result['functions']})
            docstrings[result['lineno']] = result['docstring']
    if globalAttributes:
        symbols['attributes'] = globalAttributes
    if globalFunctions:
        symbols['functions'] = globalFunctions
    if classes:
        symbols['classes'] = classes
    if docstrings and with_docstrings:
        symbols['docstrings'] = docstrings

    _FILE_CONTENT = None

    return symbols


def obtain_imports(source='', body=None):
    if source:
        try:
            module = ast.parse(source)
            body = module.body
        except:
            logger_imports.debug("A file contains syntax errors.")
    #Imports{} = {name: asname}, for example = {sys: sysAlias}
    imports = {}
    #From Imports{} = {name: {module: fromPart, asname: nameAlias}}
    fromImports = {}
    for sym in body:
        if type(sym) is ast.Import:
            for item in sym.names:
                imports[item.name] = {'asname': item.asname,
                    'lineno': sym.lineno}
        if type(sym) is ast.ImportFrom:
            for item in sym.names:
                fromImports[item.name] = {'module': sym.module,
                    'asname': item.asname, 'lineno': sym.lineno}
    return {'imports': imports, 'fromImports': fromImports}
