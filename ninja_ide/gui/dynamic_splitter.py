# -*- coding: utf-8 -*-

from PyQt4.QtGui import QSplitter


class DynamicSplitter(QSplitter):

    def __init__(self, orientation):
        super(DynamicSplitter, self).__init__(orientation)

    def add_widget(self, widget, top=False):
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