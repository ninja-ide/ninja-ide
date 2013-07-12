# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject
from collections import defaultdict

from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE


SEC01 = 100
SEC02 = 200
SEC03 = 300
SEC04 = 400
SEC05 = 500
SEC06 = 600
SEC07 = 700
SEC08 = 800
SEC09 = 900
SEC10 = 1000


def menu_add_section(menu, section_parts):
    """
    each_part is expected to be a tuple of
    (QIcon, String, bool) containing respectively the icon, text and flag
    indicating if this is an action
    """
    for each_part, weight in section_parts:
        icon, text, action = each_part
        if action:
            add = menu.addAction
        else:
            add = menu.addMenu
        if icon:
            add(icon, text)
        else:
            add(text)
    #FIXME: This appends a separator at the end of each menu
    menu.addSeparator()


class _MenuBar(QObject):

    def __init__(self):
        super(_MenuBar, self).__init__()
        self._roots = {}
        self._children = {}
        self._menu_refs = {}
        self._toolbar_index = defaultdict(lambda: [])

        IDE.register_service('menu_bar', self)

        #TODO: Create recent file service
        #menu_file_connections = (
            #{'target': 'main_container',
            #'signal_name': 'recentTabsModified(QStringList)',
            #'slot': self._menuFile.update_recent_files},
        #)

    def add_root(self, root_name, root_weight=None):
        """
        Add a root menu with desired weight or at end of list
        """
        #If self._roots is empty this is going to explode
        if root_name not in self._roots:
            if root_weight is None:
                root_weight = sorted(self._roots.values())[-1] + 1
            self._roots[root_name] = root_weight

    def get_root(self):
        #Get the list of menu categories from ide: IDE.get_menu_categories
        #iter_items = self._roots.iteritems()
        #iter_items.sort(key=lambda x: x[1])
        #return iter_items
        pass

    def add_child(self, root_name, namespace, child_name, child, weight):
        #FIXME: We should also add plugin namespace for grouping per plugin
        child_path = (root_name, namespace, child_name)
        if child_path not in self._children:
            self.add_root(root_name)
            self._children[child_path] = (child, weight)

    def get_children_of(self, parent, namespace=None):
        children = defaultdict(lambda: [])
        for each_child in self._children:
            child_parent, child_namespace, child_name = each_child
            if (parent == child_parent) and ((namespace == child_namespace) or
                                             (not namespace)):
                child, weight = self._children[each_child]
                #Group by namespace and weight
                weight_index = "%d_%s" % (weight / 100, namespace)
                children[weight_index].append((child, weight))

        return children

    def add_toolbar_item(self, toolbar_item):
        section, item, weight = toolbar_item
        self._toolbar_sections[section] = (item, weight)

    def install(self):
        return
        ide = IDE.get_service('ide')
        menuitems = IDE.get_menuitems()
        #menuBar is the actual QMenuBar object from IDE which is a QMainWindow
        self.menubar = ide.menuBar()
        # EACH ITEM menu should be obtained from IDE.get_menuitems
        # which is going to return a dict with:
        # key: QAction or QMenu
        # value: (category[string], weight[int])
        # The menuitem shouldn't be created using text/icon as it is done in:
        # menu_add_section, we should already receive the proper
        # QAction/QMenu, and ask something like "instanceof" for those
        # objects to see if we should execute an addMenu or addAction to
        # the MenuBar.
        for each_menu in self.get_root():
            menu_object = self.menubar.addMenu(self.tr(each_menu))
            self._menu_refs[each_menu] = menu_object
            all_children = self.get_children_of(each_menu)
            for each_child_grp_key in sorted(all_children):
                each_child_grp = all_children[each_child_grp_key]
                menu_add_section(menu_object, sorted(each_child_grp,
                                                key=lambda x: x[1]))

    def load_toolbar(self, ide):
        #FIXME: Do the same as above to add items to toolbar
        toolbar = ide.toolbar
        toolbar.clear()
        toolbar_sections = sorted(self._toolbar_index.keys())
        for each_section in toolbar_sections:
            display = settings.TOOLBAR_ITEMS.get(each_section, None)
            items = self.get_toolbar_items_for_section(each_section)
            if display is None:
                for each_item in items:
                    #FIXME: Item should be a custom object with action being the actual addable
                    toolbar.addAction(each_item)
            else:
                #FIXME: How to make a map of items with names
                items_dict = {}
                for each_item in display:
                    pass
                    #
                #FIXME: Map items in order to get them in settings order
            toolbar.addSeparator()

        #toolbar_items = {}
        #toolbar_items.update(self._menuFile.toolbar_items)
        #toolbar_items.update(self._menuView.toolbar_items)
        #toolbar_items.update(self._menuEdit.toolbar_items)
        #toolbar_items.update(self._menuSource.toolbar_items)
        #toolbar_items.update(self._menuProject.toolbar_items)

        #for item in settings.TOOLBAR_ITEMS:
            #if item == 'separator':
                #toolbar.addSeparator()
            #else:
                #tool_item = toolbar_items.get(item, None)
                #if tool_item is not None:
                    #toolbar.addAction(tool_item)
        ##load action added by plugins, This is a special case when reload
        ##the toolbar after save the preferences widget
        #for toolbar_action in settings.get_toolbar_item_for_plugins():
            #toolbar.addAction(toolbar_action)


menu = _MenuBar()