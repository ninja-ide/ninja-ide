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

from PyQt4.QtGui import QSplitter
from PyQt4.QtCore import Qt


class DynamicSplitter(QSplitter):

    def __init__(self, orientation=Qt.Horizontal):
        super(DynamicSplitter, self).__init__(orientation)

    def add_widget(self, widget, top=False):
        #self.splitter.setSizes([1, 1])
        if top:
            self.insertWidget(0, widget)
        else:
            self.addWidget(widget)

    #def insertWidget(self, index, widget):
        #current = self.widget(index)
        #super(DynamicSplitter, self).addWidget(widget)
        ##if not current:
            ##super(DynamicSplitter, self).insertWidget(index, widget)
        ##elif self.count() == 1:
            ##super(DynamicSplitter, self).insertWidget(index, widget)
        ##elif isinstance(current, DynamicSplitter):
            ##current.insertWidget(index, widget)
        ##else:
            ##splitter = DynamicSplitter(Qt.Vertical)
            ##splitter.addWidget(current)
            ##splitter.addWidget(widget)
            ##super(DynamicSplitter, self).insertWidget(index, splitter)

    #def addWidget(self, widget):
        #self.insertWidget(1, widget)