# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (
    QAction,
    QMenu
)
from PyQt5.QtCore import QObject
from collections import defaultdict

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import utils


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


# WE WILL PROBABLY NEED TO SAVE THE WEIGHT WITH THE ACTIONS SO WE CAN
# DETERMINE TO LOCATE A PLUGIN LOADED AFTER INITIALIZATION AT THE PROPER PLACE


def menu_add_section(menu, section_parts):
    menus = []
    for each_part in section_parts:
        action, weight = each_part
        add = None
        if isinstance(action, QAction):
            add = menu.addAction
        elif isinstance(action, QMenu):
            add = menu.addMenu
            menus.append(action)
        if add:
            add(action)
    # FIXME: This appends a separator at the end of each menu
    # FIXME: add separator between sections
    menu.addSeparator()
    return menus


class _MenuBar(QObject):

    def __init__(self):
        super(_MenuBar, self).__init__()
        self._roots = {}
        self._children = {}
        self._submenu = {}
        self._menu_refs = {}
        self._toolbar_index = {}

        IDE.register_service('menu_bar', self)

    def add_root(self, root_name, root_weight=None):
        """
        Add a root menu with desired weight or at end of list
        """
        # If self._roots is empty this is going to explode
        if root_name not in self._roots:
            if root_weight is None:
                root_weight = sorted(self._roots.values())[-1] + 1
            self._roots[root_name] = root_weight

    def get_root(self):
        """Get the list of menu categories from ide: IDE.get_menu_categories"""

        iter_items = list(self._roots.items())
        iter_items.sort(key=lambda x: x[1])
        return [item[0] for item in iter_items]

    def add_child(self, root_name, sub_name, child, weight,
                  namespace="ninjaide"):
        child_path = (root_name, sub_name, namespace, child)
        oname = child.objectName()
        if oname:
            self._toolbar_index[oname] = child
        if child_path not in self._children:
            self.add_root(root_name)
            self._children[child_path] = (child, weight)

    def get_children_of(self, parent, sub_name=None, namespace=None):
        children = defaultdict(lambda: [])
        for each_child in self._children:
            child_parent, sub_parent, child_namespace, child_name = each_child
            if (parent == child_parent) and (sub_parent == sub_name) \
                    and ((namespace == child_namespace) or (not namespace)):
                child, weight = self._children[each_child]
                # Group by namespace and weight
                weight_index = "%d_%s" % (int(weight / 100.0), namespace)
                children[weight_index].append((child, weight))

        return children

    def add_toolbar_item(self, toolbar_item):
        section, item, weight = toolbar_item
        self._toolbar_sections[section] = (item, weight)

    def load_menu(self, ide):
        # menuBar is the actual QMenuBar object from IDE which is a QMainWindow
        self.menubar = ide.menuBar()
        # Create Root
        categories = ide.get_bar_categories()
        for category in categories.keys():
            self.add_root(category, root_weight=categories[category])
        # EACH ITEM menu should be obtained from ide.get_menuitems()
        # which is going to return a dict with:
        # key: QAction or QMenu
        # value: (category[string], weight[int])
        # QAction/QMenu, and ask something like "instanceof" for those
        # objects to see if we should execute an addMenu or addAction to
        # the MenuBar.
        menuitems = ide.get_menuitems()
        for action in menuitems.keys():
            category, weight = menuitems[action]
            category, subcategory = category
            # FIXME: Need category and sub, which should be none
            self.add_child(category, subcategory, action, weight)

        # FIXME: This should add to the given methods and they to the actual
        # adding on menu upon add
        # FIXME: To support this we should have a way to add these in order
        # after menu creation
        for each_menu in self.get_root():
            menu_object = self.menubar.addMenu(each_menu)
            self._menu_refs[each_menu] = menu_object
            all_children = self.get_children_of(each_menu)
            for each_child_grp_key in sorted(all_children):
                each_child_grp = all_children[each_child_grp_key]
                menus = menu_add_section(
                    menu_object, sorted(each_child_grp, key=lambda x: x[1]))
                # FIXME: Prettify the following
                for menu in menus:
                    self._submenu[(each_menu, menu.title())] = menu

        for each_parent, each_submenu in list(self._submenu.keys()):
            menu = self._submenu[(each_parent, each_submenu)]
            all_children = self.get_children_of(each_parent, each_submenu)
            for each_child_grp_key in sorted(all_children):
                each_child_grp = all_children[each_child_grp_key]
                menu_add_section(
                    menu, sorted(each_child_grp, key=lambda x: x[1]))
                # ADD A LATER CALLBACK

        # Recent files service
        filemenu = self._menu_refs[translations.TR_MENU_FILE]
        filemenu.aboutToShow.connect(self._update_recent_files_and_projects)

    def _update_recent_files_and_projects(self):
        recent_fmenu = self._submenu[(translations.TR_MENU_FILE,
                                      translations.TR_RECENT_FILES)]
        recent_fmenu.clear()
        main_container = IDE.get_service("main_container")
        recent_files = main_container.last_opened_files
        for e, file_path in enumerate(recent_files):
            _file_path = utils.path_with_tilde_homepath(file_path)
            action_text = "&{} | {}".format(e + 1, _file_path)
            action = recent_fmenu.addAction(action_text)
            action.setData(file_path)
            action.triggered.connect(self._open_recent)

        recent_fmenu.setEnabled(bool(recent_files))
        if recent_files:
            recent_fmenu.addSeparator()
            clear_action = recent_fmenu.addAction(translations.TR_CLEAR_THIS_LIST)
            clear_action.triggered.connect(
                main_container.clear_last_opened_files)

    def _open_recent(self):
        qaction = self.sender()
        main_container = IDE.get_service("main_container")
        main_container.open_file(qaction.data())

    def load_toolbar(self, ide):
        toolbar = ide.get_service("toolbar")
        toolbar_items = ide.get_toolbaritems()
        categories = list(ide.get_bar_categories().items())
        categories = sorted(categories, key=lambda x: x[1])
        for category, _ in categories:
            items_in_category = sorted(
                [(key, toolbar_items[key][0], toolbar_items[key][1])
                 for key in toolbar_items
                 if toolbar_items[key][0][0] == category],
                key=lambda x: x[2])
            for item in items_in_category:
                action = item[0]
                if action.objectName() in settings.TOOLBAR_ITEMS:
                    toolbar.add_action(action)
                if action.objectName() in settings.ACTIONBAR_ITEMS:
                    toolbar.add_actionbar_item(action)


menu = _MenuBar()
