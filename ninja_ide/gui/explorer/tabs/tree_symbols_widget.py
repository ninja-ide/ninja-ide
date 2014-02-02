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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QMenu

from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer


class TreeSymbolsWidget(QDialog):

    def __init__(self, parent=None):
        super(TreeSymbolsWidget, self).__init__(parent,
            Qt.WindowStaysOnTopHint)
        self.setWindowTitle(translations.TR_TAB_SYMBOLS)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.tree = QTreeWidget()
        vbox.addWidget(self.tree)
        self.tree.header().setHidden(True)
        self.tree.setSelectionMode(self.tree.SingleSelection)
        self.tree.setAnimated(True)
        self.tree.header().setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self.tree.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(False)
        self.actualSymbols = ('', {})
        self.docstrings = {}
        self.collapsedItems = {}

        self.connect(self, SIGNAL("itemClicked(QTreeWidgetItem *, int)"),
            self._go_to_definition)
        self.connect(self, SIGNAL("itemActivated(QTreeWidgetItem *, int)"),
            self._go_to_definition)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self,
            SIGNAL("customContextMenuRequested(const QPoint &)"),
            self._menu_context_tree)
        self.connect(self, SIGNAL("itemCollapsed(QTreeWidgetItem *)"),
            self._item_collapsed)
        self.connect(self, SIGNAL("itemExpanded(QTreeWidgetItem *)"),
            self._item_expanded)

        IDE.register_service('symbols_explorer', self)
        ExplorerContainer.register_tab(translations.TR_TAB_SYMBOLS, self)

    def install_tab(self):
        ide = IDE.get_service('ide')
        self.connect(ide, SIGNAL("goingDown()"), self.close)

    def _menu_context_tree(self, point):
        index = self.tree.indexAt(point)
        if not index.isValid():
            return

        menu = QMenu(self)
        f_all = menu.addAction(self.tr("Fold all"))
        u_all = menu.addAction(self.tr("Unfold all"))
        menu.addSeparator()
        u_class = menu.addAction(self.tr("Unfold classes"))
        u_class_method = menu.addAction(self.tr("Unfold classes and methods"))
        u_class_attr = menu.addAction(self.tr("Unfold classes and attributes"))
        menu.addSeparator()
        #save_state = menu.addAction(self.tr("Save State"))

        self.connect(f_all, SIGNAL("triggered()"),
            lambda: self.tree.collapseAll())
        self.connect(u_all, SIGNAL("triggered()"),
            lambda: self.tree.expandAll())
        self.connect(u_class, SIGNAL("triggered()"), self._unfold_class)
        self.connect(u_class_method, SIGNAL("triggered()"),
            self._unfold_class_method)
        self.connect(u_class_attr, SIGNAL("triggered()"),
            self._unfold_class_attribute)
        #self.connect(save_state, SIGNAL("triggered()"),
            #self._save_symbols_state)

        menu.exec_(QCursor.pos())

    def _get_classes_root(self):
        class_root = None
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.isClass and not item.isClickable:
                class_root = item
                break
        return class_root

    def _unfold_class(self):
        self.tree.collapseAll()
        classes_root = self._get_classes_root()
        if not classes_root:
            return

        classes_root.setExpanded(True)

    def _unfold_class_method(self):
        self.tree.expandAll()
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
        self.tree.expandAll()
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

    def _save_symbols_state(self):
        #filename = self.actualSymbols[0]
        #TODO: persist self.collapsedItems[filename] in QSettings
        pass

    def _get_expand(self, item):
        """
        Returns True or False to be used as setExpanded() with the items
        It method is based on the click that the user made in the tree
        """
        name = self._get_unique_name(item)
        filename = self.actualSymbols[0]
        collapsed_items = self.collapsedItems.get(filename, [])
        can_check = (not item.isClickable) or item.isClass or item.isMethod
        if can_check and name in collapsed_items:
            return False
        return True

    @staticmethod
    def _get_unique_name(item):
        """
        Returns a string used as unique name
        """
        # className_Attributes/className_Functions
        parent = item.parent()
        if parent:
            return "%s_%s" % (parent.text(0), item.text(0))
        return "_%s" % item.text(0)

    def update_symbols_tree(self, symbols, filename='', parent=None):
        if not parent:
            if filename == self.actualSymbols[0] and \
                self.actualSymbols[1] and not symbols:
                    return

            if symbols == self.actualSymbols[1]:
                # Nothing new then return
                return

            # we have new symbols refresh it
            self.tree.clear()
            self.actualSymbols = (filename, symbols)
            self.docstrings = symbols.get('docstrings', {})
            parent = self.tree
        if 'attributes' in symbols:
            globalAttribute = ItemTree(parent, [self.tr("Attributes")])
            globalAttribute.isClickable = False
            globalAttribute.isAttribute = True
            globalAttribute.setExpanded(self._get_expand(globalAttribute))
            for glob in sorted(symbols['attributes']):
                globItem = ItemTree(globalAttribute, [glob],
                    lineno=symbols['attributes'][glob])
                globItem.isAttribute = True
                globItem.setIcon(0, QIcon(":img/attribute"))
                globItem.setExpanded(self._get_expand(globItem))

        if 'functions' in symbols and symbols['functions']:
            functionsItem = ItemTree(parent, [self.tr("Functions")])
            functionsItem.isClickable = False
            functionsItem.isMethod = True
            functionsItem.setExpanded(self._get_expand(functionsItem))
            for func in sorted(symbols['functions']):
                item = ItemTree(functionsItem, [func],
                    lineno=symbols['functions'][func]['lineno'])
                tooltip = self.create_tooltip(
                    func, symbols['functions'][func]['lineno'])
                item.isMethod = True
                item.setIcon(0, QIcon(":img/function"))
                item.setToolTip(0, tooltip)
                item.setExpanded(self._get_expand(item))
                self.update_symbols_tree(
                    symbols['functions'][func]['functions'], parent=item)
        if 'classes' in symbols and symbols['classes']:
            classItem = ItemTree(parent, [self.tr("Classes")])
            classItem.isClickable = False
            classItem.isClass = True
            classItem.setExpanded(self._get_expand(classItem))
            for claz in sorted(symbols['classes']):
                line_number = symbols['classes'][claz]['lineno']
                item = ItemTree(classItem, [claz], lineno=line_number)
                item.isClass = True
                tooltip = self.create_tooltip(claz, line_number)
                item.setToolTip(0, tooltip)
                item.setIcon(0, QIcon(":img/class"))
                item.setExpanded(self._get_expand(item))
                self.update_symbols_tree(symbols['classes'][claz]['members'],
                    parent=item)

    def _go_to_definition(self, item):
        main_container = IDE.get_service('main_container')
        if item.isClickable and main_container:
            main_container.editor_go_to_line(item.lineno - 1)

    def create_tooltip(self, name, lineno):
        doc = self.docstrings.get(lineno, None)
        if doc is None:
            doc = ''
        else:
            doc = '\n' + doc
        tooltip = name + doc
        return tooltip

    def _item_collapsed(self, item):
        super(TreeSymbolsWidget, self).collapseItem(item)

        can_check = (not item.isClickable) or item.isClass or item.isMethod
        if can_check:
            n = self._get_unique_name(item)
            filename = self.actualSymbols[0]
            self.collapsedItems.setdefault(filename, [])
            if not n in self.collapsedItems[filename]:
                self.collapsedItems[filename].append(n)

    def _item_expanded(self, item):
        super(TreeSymbolsWidget, self).expandItem(item)

        n = self._get_unique_name(item)
        filename = self.actualSymbols[0]
        if n in self.collapsedItems.get(filename, []):
            self.collapsedItems[filename].remove(n)
            if not len(self.collapsedItems[filename]):
                # no more items, free space
                del self.collapsedItems[filename]

    def clean(self):
        """
        Reset the tree and reset attributes
        """
        self.tree.clear()
        self.collapsedItems = {}

    def closeEvent(self, event):
        self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)
        event.ignore()


class ItemTree(QTreeWidgetItem):

    def __init__(self, parent, name, lineno=None):
        super(ItemTree, self).__init__(parent, name)
        self.lineno = lineno
        self.isClickable = True
        self.isAttribute = False
        self.isClass = False
        self.isMethod = False


if settings.SHOW_SYMBOLS_LIST:
    treeSymbols = TreeSymbolsWidget()
else:
    treeSymbols = None