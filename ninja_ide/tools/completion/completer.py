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
#Based in pycomplete emacs module.

from __future__ import absolute_import

import sys
import types
#import inspect
try:
    import StringIO
except:
    import io as StringIO  # lint:ok
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.tools.completion.completer')

_HELPOUT = StringIO.StringIO
_STDOUT = sys.stdout


def get_completions_per_type(object_dir):
    '''Return info about function parameters'''

    if not object_dir:
        return {}
    result = {'attributes': [], 'modules': [], 'functions': [], 'classes': []}
    type_assign = {types.ClassType: 'classes',
                   types.FunctionType: 'functions',
                   types.MethodType: 'functions',
                   types.ModuleType: 'modules',
                   types.LambdaType: 'functions'}

    for attr in object_dir:
        obj = None
        sig = ""
        try:
            obj = _load_symbol(attr, globals(), locals())
        except Exception as ex:
            logger.error('Could not load symbol: %r', ex)
            return {}

        if type(obj) in (types.ClassType, types.TypeType):
            # Look for the highest __init__ in the class chain.
            obj = _find_constructor(obj)
        elif isinstance(obj, types.MethodType):
            # bit of a hack for methods - turn it into a function
            # but we drop the "self" param.
            obj = obj.im_func

        # Not Show functions args, but we will use this for showing doc
#        if type(obj) in [types.FunctionType, types.LambdaType]:
#            (args, varargs, varkw, defaults) = inspect.getargspec(obj)
#            sig = ('%s%s' % (obj.__name__,
#                               inspect.formatargspec(args, varargs, varkw,
#                                                     defaults)))
        if not sig:
            sig = attr[attr.rfind('.') + 1:]
        result[type_assign.get(type(obj), 'attributes')].append(sig)
    return result


def _load_symbol(s, dglobals, dlocals):
    sym = None
    dots = s.split('.')
    if not s or len(dots) == 1:
        sym = eval(s, dglobals, dlocals)
    else:
        for i in range(1, len(dots) + 1):
            s = '.'.join(dots[:i])
            if not s:
                continue
            try:
                sym = eval(s, dglobals, dlocals)
            except NameError:
                try:
                    sym = __import__(s, dglobals, dlocals, [])
                    dglobals[s] = sym
                except ImportError:
                    pass
            except AttributeError:
                try:
                    sym = __import__(s, dglobals, dlocals, [])
                except ImportError:
                    pass
    return sym


def _import_modules(imports, dglobals):
    '''If given, execute import statements'''
    if imports is not None:
        for stmt in imports:
            try:
                exec(stmt, dglobals)
            except TypeError:
                raise TypeError('invalid type: %s' % stmt)
            except Exception:
                continue


def get_all_completions(s, imports=None):
    '''Return contextual completion of s (string of >= zero chars)'''
    dlocals = {}
    #FIXXXXXXXXXXXXXXXX
    #return {}

    _import_modules(imports, globals())

    dots = s.rsplit('.', 1)

    sym = None
    for i in range(1, len(dots)):
        s = '.'.join(dots[:i])
        if not s:
            continue
        try:
            try:
                if s.startswith('PyQt4.') and s.endswith(')'):
                    s = s[:s.rindex('(')]
                sym = eval(s, globals(), dlocals)
            except NameError:
                try:
                    sym = __import__(s, globals(), dlocals, [])
                except ImportError:
                    if s.find('(') != -1 and s[-1] == ')':
                        s = s[:s.index('(')]
                    sym = eval(s, globals(), dlocals)
                except AttributeError:
                    try:
                        sym = __import__(s, globals(), dlocals, [])
                    except ImportError:
                        pass
        except (AttributeError, NameError, TypeError, SyntaxError):
            return {}
    if sym is not None:
        var = s
        s = dots[-1]
        return get_completions_per_type(["%s.%s" % (var, k) for k in
                                         dir(sym) if k.startswith(s)])
    return {}


def _find_constructor(class_ob):
    # Given a class object, return a function object used for the
    # constructor (ie, __init__() ) or None if we can't find one.
    try:
        return class_ob.__init__.im_func
    except AttributeError:
        for base in class_ob.__bases__:
            rc = _find_constructor(base)
            if rc is not None:
                return rc
    return None
