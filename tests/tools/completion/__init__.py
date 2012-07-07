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

import re


def get_source_data(code, word=""):
    clazzes = sorted(set(re.findall("class (\w+?)\(", code)))
    funcs = sorted(set(re.findall("(\w+?)\(", code)))
    attrs = sorted(set(re.split('\W+', code)))
    del attrs[0]
    filter_attrs = lambda x: (x not in funcs) and not x.isdigit()
    attrs = filter(filter_attrs, attrs)
    if word in attrs:
        attrs.remove(word)
    funcs = filter(lambda x: x not in clazzes, funcs)
    data = {'attributes': attrs,
        'functions': funcs,
        'classes': clazzes}
    return data


SOURCE_COMPLETION = """
a = "ninja-ide"
b = a.split()

import os

r = os.path.sep

from PyQt4 import QtGui

c = QtGui.Q

q = self.wrong_call("home",
        "cat")

mamamia = 2

class MyClass:

    attr = 'my_name'

    def __init__(self):
        self.s = {}
        self.m = 5

    def print_function(self):
        pass

    def another(self):
        l = []"""


SOURCE_ANALYZER_NATIVE = """
import os
import sys
from sys import exit

a = 5
b = []


class Test(object):

    def __init__(self):
        self.x = {}

    def my_function(self):
        code = 'string'
        self.var = 4.5
        if code:
            my_var = 'inside if'

    def func_args(self, var, inte, num=5, li='ninja', *arggg, **kwarggg):
        nothing = False

def global_func():
    bo = True
    obj = os.path
    di = Test()
    another = obj


man = ()
"""


SOURCE_LATE_RESOLUTION = """
import os

p = os.path
"""


SOURCE_INHERITANCE = """
import decimal
from threading import Lock

class Parent:

    def __init__(self):
        self.value = 'string'

    def function(self):
        pass

"""
