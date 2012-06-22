# -*- coding: utf-8 *-*

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
