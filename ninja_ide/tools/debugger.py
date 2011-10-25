# -*- coding: utf-8 -*-
from __future__ import absolute_import

import bdb


class Debugger(bdb.Bdb):

    def __init__(self, breakpoints):
        bdb.Bdb.__init__(self)

        #Apply breakpoints
        for bp in breakpoints:
            self.set_break(bp[0], bp[1])

    def run(self, code):
        bdb.Bdb.run(self, code)
