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

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer


class TreeSymbolsWidget(QDialog):
    """Class of Dialog for Tree Symbols"""
    dockedWidget = pyqtSignal("QObject*")
    undockedWidget = pyqtSignal()
    changeTitle = pyqtSignal(str)
    def __init__(self, parent=None):
        super(TreeSymbolsWidget, self).__init__(parent,
                                                Qt.WindowStaysOnTopHint)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.tree = QTreeWidget()
        vbox.addWidget(self.tree)
        self.tree.header().setHidden(True)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.setAnimated(True)
        self.tree.header().setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(False)
        self.actualSymbols = ('', {})
        self.docstrings = {}
        self.collapsedItems = {}

        self.tree.itemClicked['QTreeWidgetItem*', int].connect(self._go_to_definition)
        # self.tree.itemActivated['QTreeWidgetItem*', int].connect(self._go_to_definition)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested['const QPoint &'].connect(self._menu_context_tree)
        self.tree.itemCollapsed['QTreeWidgetItem*'].connect(self._item_collapsed)
        self.tree.itemExpanded['QTreeWidgetItem*'].connect(self._item_expanded)

        IDE.register_service('symbols_explorer', self)
        ExplorerContainer.register_tab(translations.TR_TAB_SYMBOLS, self)

    def install_tab(self):
        """Connect signals for goingdown"""
        ide = IDE.getInstance()
        ide.goingDown.connect(self.close)

    def _menu_context_tree(self, point):
        """Context menu"""
        index = self.tree.indexAt(point)
        if not index.isValid():
            return

        menu = QMenu(self)
        f_all = menu.addAction(translations.TR_FOLD_ALL)
        u_all = menu.addAction(translations.TR_UNFOLD_ALL)
        menu.addSeparator()
        u_class = menu.addAction(translations.TR_UNFOLD_CLASSES)
        u_class_method = menu.addAction(
            translations.TR_UNFOLD_CLASSES_AND_METHODS)
        u_class_attr = menu.addAction(
            translations.TR_UNFOLD_CLASSES_AND_ATTRIBUTES)
        menu.addSeparator()
        #save_state = menu.addAction(self.tr("Save State"))

        f_all.triggered['bool'].connect(lambda s: self.tree.collapseAll())
        u_all.triggered['bool'].connect(lambda s: self.tree.expandAll())
        u_class.triggered['bool'].connect(self._unfold_class)
        u_class_method.triggered['bool'].connect(self._unfold_class_method)
        u_class_attr.triggered['bool'].connect(self._unfold_class_attribute)
        #self.connect(save_state, SIGNAL("triggered()"),
            #self._save_symbols_state)

        menu.exec_(QCursor.pos())

    def _get_classes_root(self):
        """Return the root of classes"""
        class_root = None
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.isClass and not item.isClickable:
                class_root = item
                break
        return class_root

    def _unfold_class(self):
        """Method to Unfold Classes"""
        self.tree.collapseAll()
        classes_root = self._get_classes_root()
        if not classes_root:
            return

        classes_root.setExpanded(True)

    def _unfold_class_method(self):
        """Method to Unfold Methods"""
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
        """Method to Unfold Attributes"""
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
        """Method to Save a persistent Symbols state"""
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
        """Method to Update the symbols on the Tree"""
        TIP = "{} {}"
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
            # print("\nsymbols['attributes']", symbols['attributes'])
            globalAttribute = ItemTree(parent, [translations.TR_ATTRIBUTES])
            globalAttribute.isClickable = False
            globalAttribute.isAttribute = True
            globalAttribute.setExpanded(self._get_expand(globalAttribute))
            globalAttribute.setToolTip(
                0, TIP.format(len(symbols['attributes']),
                              translations.TR_ATTRIBUTES))
            for glob in sorted(symbols['attributes']):
                globItem = ItemTree(globalAttribute, [glob],
                                    lineno=symbols['attributes'][glob])
                globItem.isAttribute = True
                globItem.setIcon(0, QIcon(":img/attribute"))
                globItem.setExpanded(self._get_expand(globItem))

        if 'functions' in symbols and symbols['functions']:
            functionsItem = ItemTree(parent, [translations.TR_FUNCTIONS])
            functionsItem.isClickable = False
            functionsItem.isMethod = True
            functionsItem.setExpanded(self._get_expand(functionsItem))
            functionsItem.setToolTip(0, TIP.format(len(symbols['functions']),
                                                   translations.TR_FUNCTIONS))
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
            classItem = ItemTree(parent, [translations.TR_CLASSES])
            classItem.isClickable = False
            classItem.isClass = True
            classItem.setExpanded(self._get_expand(classItem))
            classItem.setToolTip(0, TIP.format(len(symbols['classes']),
                                               translations.TR_CLASSES))
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
        """Takes and item object and goes to definition on the editor"""
        main_container = IDE.get_service('main_container')
        print("\nprimero al clickear pas por aca!!", item.text(0))
        if item.isClickable and main_container:
            # main_container.editor_go_to_line(item.lineno - 1, True)
            main_container.editor_go_to_symbol_line(item.lineno - 1, item.text(0), True)

    def create_tooltip(self, name, lineno):
        """Takes a name and line number and returns a tooltip"""
        doc = self.docstrings.get(lineno, None)
        if doc is None:
            doc = ''
        else:
            doc = '\n' + doc
        tooltip = name + doc
        return tooltip

    def _item_collapsed(self, item):
        """When item collapsed"""
        self.tree.collapseItem(item)

        can_check = (not item.isClickable) or item.isClass or item.isMethod
        if can_check:
            n = self._get_unique_name(item)
            filename = self.actualSymbols[0]
            self.collapsedItems.setdefault(filename, [])
            if not n in self.collapsedItems[filename]:
                self.collapsedItems[filename].append(n)

    def _item_expanded(self, item):
        """When item expanded"""
        self.tree.expandItem(item)

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

    def reject(self):
        if self.parent() is None:
            self.dockedWidget.emit(self)

    def closeEvent(self, event):
        """On Close event handling"""
        self.dockedWidget.emit(self)
        event.ignore()


class ItemTree(QTreeWidgetItem):
    """Item Tree widget items"""

    def __init__(self, parent, name, lineno=None, pos= None):
        super(ItemTree, self).__init__(parent, name)
        self.lineno = lineno
        self.pos = pos
        self.isClickable = True
        self.isAttribute = False
        self.isClass = False
        self.isMethod = False


if settings.SHOW_SYMBOLS_LIST:
    treeSymbols = TreeSymbolsWidget()
else:
    treeSymbols = None