# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject

from ninja_ide.core import settings
from ninja_ide.core.pattern import singleton
from ninja_ide.gui import ide

#NINJA-IDE Menus
from ninja_ide.gui.menus import menu_about
from ninja_ide.gui.menus import menu_file
from ninja_ide.gui.menus import menu_edit
from ninja_ide.gui.menus import menu_view
from ninja_ide.gui.menus import menu_plugins
from ninja_ide.gui.menus import menu_project
from ninja_ide.gui.menus import menu_source


@singleton
class MenuBar(QObject):

    def __init__(self):
        super(MenuBar, self).__init__()

    def install(self, ide):
        #Menu
        menubar = ide.menuBar()
        file_ = menubar.addMenu(self.tr("&File"))
        edit = menubar.addMenu(self.tr("&Edit"))
        view = menubar.addMenu(self.tr("&View"))
        source = menubar.addMenu(self.tr("&Source"))
        project = menubar.addMenu(self.tr("&Project"))
        self.pluginsMenu = menubar.addMenu(self.tr("&Addins"))
        about = menubar.addMenu(self.tr("Abou&t"))

        #The order of the icons in the toolbar is defined by this calls
        self._menuFile = menu_file.MenuFile(file_, ide.toolbar, ide)
        self._menuView = menu_view.MenuView(view, ide.toolbar, ide)
        self._menuEdit = menu_edit.MenuEdit(edit, ide.toolbar)
        self._menuSource = menu_source.MenuSource(source)
        self._menuProject = menu_project.MenuProject(project, ide.toolbar)
        self._menuPlugins = menu_plugins.MenuPlugins(ide.pluginsMenu)
        self._menuAbout = menu_about.MenuAbout(about)

    def load_toolbar(self, ide):
        toolbar = ide.toolbar
        toolbar.clear()
        toolbar_items = {}
        toolbar_items.update(self._menuFile.toolbar_items)
        toolbar_items.update(self._menuView.toolbar_items)
        toolbar_items.update(self._menuEdit.toolbar_items)
        toolbar_items.update(self._menuSource.toolbar_items)
        toolbar_items.update(self._menuProject.toolbar_items)

        for item in settings.TOOLBAR_ITEMS:
            if item == 'separator':
                toolbar.addSeparator()
            else:
                tool_item = toolbar_items.get(item, None)
                if tool_item is not None:
                    toolbar.addAction(tool_item)
        #load action added by plugins, This is a special case when reload
        #the toolbar after save the preferences widget
        for toolbar_action in settings.get_toolbar_item_for_plugins():
            toolbar.addAction(toolbar_action)


#Register StatusBar
def register_status_bar():
    menu = MenuBar()
    ide.IDE.register_service(menu, 'menu_bar')


register_status_bar()