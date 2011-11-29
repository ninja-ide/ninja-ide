# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView

from PyQt4.QtCore import QStringList
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources


class TreeSymbolsWidget(QTreeWidget):

###############################################################################
# TreeSymbolsWidget SIGNALS
###############################################################################

    """
    goToDefinition(int)
    """

###############################################################################

    def __init__(self):
        QTreeWidget.__init__(self)
        self.header().setHidden(True)
        self.setSelectionMode(self.SingleSelection)
        self.setAnimated(True)
        self.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.actualSymbols = ('', {})

        self.connect(self, SIGNAL("itemClicked(QTreeWidgetItem *, int)"),
            self._go_to_definition)

    def update_symbols_tree(self, symbols, filename='', parent=None):
        if not parent:
            if filename == self.actualSymbols[0] and \
                self.actualSymbols[1] and not symbols:
                    return
            self.clear()
            self.actualSymbols = (filename, symbols)
            parent = self
        if 'attributes' in symbols:
            globalAttribute = ItemTree(parent,
                QStringList(self.tr("Attributes")))
            globalAttribute.isClickable = False
            for glob in sorted(symbols['attributes']):
                globItem = ItemTree(globalAttribute,
                    QStringList(glob), lineno=symbols['attributes'][glob])
                globItem.isAttribute = True
                globItem.setIcon(0, QIcon(resources.IMAGES['attribute']))
        if 'functions' in symbols:
            functionsItem = ItemTree(parent, QStringList(self.tr("Functions")))
            functionsItem.isClickable = False
            for func in sorted(symbols['functions']):
                item = ItemTree(functionsItem, QStringList(func),
                    lineno=symbols['functions'][func])
                item.setIcon(0, QIcon(resources.IMAGES['function']))
        if 'classes' in symbols:
            classItem = ItemTree(self, QStringList(self.tr("Classes")))
            classItem.isClickable = False
            for claz in sorted(symbols['classes']):
                item = ItemTree(classItem, QStringList(claz),
                    lineno=symbols['classes'][claz][0])
                item.setIcon(0, QIcon(resources.IMAGES['class']))
                self.update_symbols_tree(symbols['classes'][claz][1],
                    parent=item)
        self.expandAll()

    def _go_to_definition(self, item):
        if item.isClickable:
            self.emit(SIGNAL("goToDefinition(int)"), item.lineno - 1)


class ItemTree(QTreeWidgetItem):

    def __init__(self, parent, name, lineno=None):
        QTreeWidgetItem.__init__(self, parent, name)
        self.lineno = lineno
        self.isClickable = True
        self.isAttribute = False
