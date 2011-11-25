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
from ninja_ide.core import settings
from ninja_ide.tools import introspection


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

        #Set self as symbols handler for python
        settings.set_symbols_handler('py', self)

        self.connect(self, SIGNAL("itemClicked(QTreeWidgetItem *, int)"),
            self._go_to_definition)

    def obtain_symbols(self, source):
        """
        Returns the symbols for Python Language
        """
        return introspection.obtain_symbols(source)

    def update_symbols_tree(self, symbols, filename='', parent=None):
        if not parent:
            if filename == self.actualSymbols[0] and \
                self.actualSymbols[1] and not symbols:
                    return
            self.clear()
            self.actualSymbols = (filename, symbols)
            parent = self
        if 'imports' in symbols:
            impItem = ItemTree(parent,
                QStringList(self.tr("Imports")))
            impItem.isClickable = False
            for imp in sorted(symbols['imports']):
                name = imp
                if symbols['imports'][imp]['asname'] is not None:
                    name += ' as %s' % \
                        symbols['imports'][imp]['asname']
                importItem = ItemTree(impItem,
                    QStringList(name),
                    lineno=symbols['imports'][imp]['lineno'])
                importItem.setIcon(0, QIcon(resources.IMAGES['import']))
        if 'fromImports' in symbols:
            fromImpItem = ItemTree(parent,
                QStringList(self.tr("From ... Imports")))
            fromImpItem.isClickable = False
            for imp in sorted(symbols['fromImports']):
                name = imp
                if symbols['fromImports'][imp]['asname'] is not None:
                    name += ' as %s' % \
                        symbols['fromImports'][imp]['asname']
                importItem = ItemTree(fromImpItem,
                    QStringList(name),
                    lineno=symbols['fromImports'][imp]['lineno'])
                importItem.setIcon(0, QIcon(resources.IMAGES['import']))
        if 'attributes' in symbols:
            globalAttribute = ItemTree(parent,
                QStringList(self.tr("Attributes")))
            globalAttribute.isClickable = False
            for glob in sorted(symbols['attributes']):
                globItem = ItemTree(globalAttribute,
                    QStringList(glob), lineno=symbols['attributes'][glob])
                globItem.isAttribute = True
                globItem.setIcon(0, QIcon(resources.IMAGES['attribute']))
            self.expand(self.indexFromItem(globalAttribute, 0))
        if 'functions' in symbols:
            functionsItem = ItemTree(parent, QStringList(self.tr("Functions")))
            functionsItem.isClickable = False
            for func in sorted(symbols['functions']):
                item = ItemTree(functionsItem, QStringList(func),
                    lineno=symbols['functions'][func])
                item.setIcon(0, QIcon(resources.IMAGES['function']))
            self.expand(self.indexFromItem(functionsItem, 0))
        if 'classes' in symbols:
            classItem = ItemTree(self, QStringList(self.tr("Classes")))
            classItem.isClickable = False
            for claz in sorted(symbols['classes']):
                item = ItemTree(classItem, QStringList(claz),
                    lineno=symbols['classes'][claz][0])
                item.setIcon(0, QIcon(resources.IMAGES['class']))
                self.update_symbols_tree(symbols['classes'][claz][1],
                    parent=item)
            self.expand(self.indexFromItem(classItem, 0))

    def _go_to_definition(self, item):
        if item.isClickable:
            self.emit(SIGNAL("goToDefinition(int)"), item.lineno - 1)


class ItemTree(QTreeWidgetItem):

    def __init__(self, parent, name, lineno=None):
        QTreeWidgetItem.__init__(self, parent, name)
        self.lineno = lineno
        self.isClickable = True
        self.isAttribute = False
