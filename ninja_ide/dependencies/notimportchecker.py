#!/usr/bin/env python3
__author__ = "Emmanuel Arias <eamanu@eamanu.com>"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "0.0.2b1"
__maintainer__ = "Emmanuel Arias"
__email__ = "eamanu@eamanu.com"
__status__ = "Beta"

import ast
import os
import sys


class SearchImport(ast.NodeVisitor):
    def __init__(self):
        self._imports = {}

    def get_imports(self):
        """Return a dict of imports on the file

        Parameters
        ----------
        None

        Return
        ------
        self._imports: dict -> dict of imports
        """
        return self._imports

    def visit_ImportFrom(self, stmt):
        """Visit Import from
        This is the visit from of ast module
        """
        module_name = stmt.module
        names = stmt.names
        names_dict = {}

        for al in names:
            if al.name == '*':
                continue
            names_dict[al.name] = al.name

        self._imports.setdefault(module_name, {'mod_name': names_dict,
                                               'lineno': stmt.lineno})
        for child in ast.iter_child_nodes(stmt):
            self.generic_visit(child)

    def visit_Import(self, stmt):
        """Visit Import
        This is the visit of ast module
        """
        for al in stmt.names:
            self._imports.setdefault(al.name, {'mod_name':
                                               {al.name: al.name},
                                               'lineno': stmt.lineno})
        for child in ast.iter_child_nodes(stmt):
            self.generic_visit(child)


class Checker(object):
    def __init__(self, path):
        """Checker object
        Parameters
        ----------
        path: string -> path file

        """
        self._path = path
        self._imports = dict()
        self._import_error_list = dict()

    def parse_file(self, path):
        """Parse the file

        Params
        ------
        path: string -- path of the file

        Return
        ------
        stmt: string -- the parse file

        Error:

        -10 -> if there are some problem while try to open the file
        -11 -> syntax error on parse file
        """
        stmt = ''
        try:
            with open(path, 'r') as f:
                stmt = ast.parse(f.read())
            return stmt
        except IOError as ioerror:
            print('{}: Error while try to open the file'.format(str(ioerror)))
            return (-10)
        except SyntaxError as syntaxerror:
            print('{}: Wrong Syntax'.format(str(syntaxerror)))
            return (-11)

    def get_imports(self, path_file=None):
        """Return Imports on file given on path

        Params
        ------
        path: string -- path of the file

        Return
        ------
        self_imports: dict -- dict of imports and importFrom

        Error
        -----
        -1 -> if there are some problems
        """
        if path_file is None:
            path = self._path
        else:
            path = path_file

        stmt = self.parse_file(path)
        if stmt != -10 and stmt != -11:
            searcher = SearchImport()
            searcher.visit(stmt)
            self._imports = searcher.get_imports()
            return self._imports
        return (-1)

    def get_not_imports_on_file(self, stmt, path=None):
        """Get imports that dont exist on the file

        Parameters
        ----------
        stmt: dict -> dict of not imports in the file
            {'sys':{'lineno': 1, 'mod_name': 'sys'}}

        if stmt == -1 (see parse_file) return None

        path: string -> default None. path is the basename
        of the file.
        """
        if (stmt == -1):
            self._import_error_list = {}
            return None

        if path is None:
            path = self._path
        workspace = os.getcwd()
        dn = os.path.dirname(path)
        if dn == '':  # if path file is in the current folder
            os.chdir(workspace)
        else:
            os.chdir(dn)  # if path is complete
        for key, value in stmt.items():
            for mod_name in value['mod_name']:
                try:
                    if key == mod_name:
                        exec('import {}'.format(key))
                    else:
                        exec('from {} import {}'.format(key, mod_name))
                except RuntimeError as e:
                    pass
                except ImportError as e:
                    self._import_error_list.setdefault(key,
                                                       {'mod_name': mod_name,
                                                        'lineno':
                                                        value['lineno']})
        os.chdir(workspace)
        if len(self._import_error_list) == 0:
            return None
        else:
            return self._import_error_list


def print_report(dict_not_imports):
    """Print the report of not imports on the file"""
    if dict_not_imports is None:
        print('There are not not imports')
    else:
        for key, values in dict_not_imports.items():
            if values is None:
                print('{}: OK'.format(key))
            else:
                print('{} module have {} Not Imports'.format(key, len(values)))
                if isinstance(values['mod_name'], dict):
                    for v in values['mod_name']:
                        print('{} on line: {}'.format(v, values['lineno']))
                else:
                    print('{} on line: {}'.format(values['mod_name'],
                                                  values['lineno']))


if __name__ == "__main__":
    files = sys.argv[1:]
    checker_list = dict()
    for f in files:
        if os.path.dirname(f) == '':
            c = Checker(os.path.join(
                os.getcwd(), f)
                        )
            checker_list[f] = c.get_not_imports_on_file(c.get_imports())
        else:
            c = Checker(f)
            checker_list[f] = c.get_not_imports_on_file(c.get_imports())
    print_report(checker_list)
