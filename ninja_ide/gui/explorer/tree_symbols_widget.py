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
from __future__ import absolute_import

from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QMenu

from PyQt4.QtCore import Qt
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
        self.docstrings = {}

        self.connect(self, SIGNAL("itemClicked(QTreeWidgetItem *, int)"),
            self._go_to_definition)
        self.connect(self, SIGNAL("itemActivated(QTreeWidgetItem *, int)"),
            self._go_to_definition)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self,
            SIGNAL("customContextMenuRequested(const QPoint &)"),
            self._menu_context_tree)

    def select_current_item(self, line, col):
        #TODO
        #print line, col
        pass

    def _menu_context_tree(self, point):
        index = self.indexAt(point)
        if not index.isValid():
            return

        menu = QMenu(self)
        f_all = menu.addAction(self.tr("Fold all"))
        u_all = menu.addAction(self.tr("Unfold all"))
        menu.addSeparator()
        u_class = menu.addAction(self.tr("Unfold classes"))
        u_class_method = menu.addAction(self.tr("Unfold classes and methods"))
        u_class_attr = menu.addAction(self.tr("Unfold classes and attributes"))

        self.connect(f_all, SIGNAL("triggered()"),
            lambda: self.collapseAll())
        self.connect(u_all, SIGNAL("triggered()"),
            lambda: self.expandAll())
        self.connect(u_class, SIGNAL("triggered()"), self._unfold_class)
        self.connect(u_class_method, SIGNAL("triggered()"),
            self._unfold_class_method)
        self.connect(u_class_attr, SIGNAL("triggered()"),
            self._unfold_class_attribute)

        menu.exec_(QCursor.pos())

    def _get_classes_root(self):
        class_root = None
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.isClass and not item.isClickable:
                class_root = item
                break
        return class_root

    def _unfold_class(self):
        self.collapseAll()
        classes_root = self._get_classes_root()
        if not classes_root:
            return

        classes_root.setExpanded(True)

    def _unfold_class_method(self):
        self.expandAll()
        classes_root = self._get_classes_root()
        if not classes_root:
            return
        #for each class!
        for i in range(classes_root.childCount()):
            class_item = classes_root.child(i)
            #for each attribute or functions
            for j in range(class_item.childCount()):
                item = class_item.child(j)
                #METHODS ROOT!!
                if not item.isMethod and not item.isClickable:
                    item.setExpanded(False)
                    break

    def _unfold_class_attribute(self):
        self.expandAll()
        classes_root = self._get_classes_root()
        if not classes_root:
            return
        #for each class!
        for i in range(classes_root.childCount()):
            class_item = classes_root.child(i)
            #for each attribute or functions
            for j in range(class_item.childCount()):
                item = class_item.child(j)
                #ATTRIBUTES ROOT!!
                if not item.isAttribute and not item.isClickable:
                    item.setExpanded(False)
                    break

    def update_symbols_tree(self, symbols, filename='', parent=None):
        if not parent:
            if filename == self.actualSymbols[0] and \
                self.actualSymbols[1] and not symbols:
                    return
            self.clear()
            self.actualSymbols = (filename, symbols)
            self.docstrings = symbols.get('docstrings', {})
            parent = self
        if 'attributes' in symbols:
            globalAttribute = ItemTree(parent, [self.tr("Attributes")])
            globalAttribute.isClickable = False
            globalAttribute.isAttribute = True
            for glob in sorted(symbols['attributes']):
                globItem = ItemTree(globalAttribute, [glob],
                    lineno=symbols['attributes'][glob])
                globItem.isAttribute = True
                globItem.setIcon(0, QIcon(resources.IMAGES['attribute']))
        if 'functions' in symbols and symbols['functions']:
            functionsItem = ItemTree(parent, [self.tr("Functions")])
            functionsItem.isClickable = False
            functionsItem.isMethod = True
            for func in sorted(symbols['functions']):
                item = ItemTree(functionsItem, [func],
                    lineno=symbols['functions'][func][0])
                tooltip = self.create_tooltip(
                    func, symbols['functions'][func][0])
                item.isMethod = True
                item.setIcon(0, QIcon(resources.IMAGES['function']))
                item.setToolTip(0, tooltip)
                self.update_symbols_tree(symbols['functions'][func][1],
                    parent=item)
        if 'classes' in symbols and symbols['classes']:
            classItem = ItemTree(parent, [self.tr("Classes")])
            classItem.isClickable = False
            classItem.isClass = True
            for claz in sorted(symbols['classes']):
                line_number = symbols['classes'][claz][0]
                item = ItemTree(classItem, [claz], lineno=line_number)
                item.isClass = True
                tooltip = self.create_tooltip(claz, line_number)
                item.setToolTip(0, tooltip)
                item.setIcon(0, QIcon(resources.IMAGES['class']))
                self.update_symbols_tree(symbols['classes'][claz][1],
                    parent=item)

        self.expandAll()

    def _go_to_definition(self, item):
        if item.isClickable:
            self.emit(SIGNAL("goToDefinition(int)"), item.lineno - 1)

    def create_tooltip(self, name, lineno):
        doc = self.docstrings.get(lineno, None)
        if doc is None:
            doc = ''
        else:
            doc = '\n' + doc
        tooltip = name + doc
        return tooltip


class ItemTree(QTreeWidgetItem):

    def __init__(self, parent, name, lineno=None):
        QTreeWidgetItem.__init__(self, parent, name)
        self.lineno = lineno
        self.isClickable = True
        self.isAttribute = False
        self.isClass = False
        self.isMethod = False
