# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject

from ninja_ide.core import settings
from ninja_ide.gui import ide

#NINJA-IDE Menus
from ninja_ide.gui.menus import menu_about
from ninja_ide.gui.menus import menu_file
from ninja_ide.gui.menus import menu_edit
from ninja_ide.gui.menus import menu_view
from ninja_ide.gui.menus import menu_plugins
from ninja_ide.gui.menus import menu_project
from ninja_ide.gui.menus import menu_source


class _MenuBar(QObject):

    def __init__(self):
        super(_MenuBar, self).__init__()

        self._menuFile = menu_file.MenuFile()
        self._menuView = menu_view.MenuView()
        self._menuEdit = menu_edit.MenuEdit()
        self._menuSource = menu_source.MenuSource()
        self._menuProject = menu_project.MenuProject()
        self._menuPlugins = menu_plugins.MenuPlugins()
        self._menuAbout = menu_about.MenuAbout()

        ide.IDE.register_service('menu_bar', self)
        ide.IDE.register_service('menu_file', self._menuFile)
        ide.IDE.register_service('menu_view', self._menuView)

        menu_file_connections = (
            {'target': 'main_container',
            'signal_name': 'recentTabsModified(QStringList)',
            'slot': self._menuFile.update_recent_files},
        )
        ide.IDE.register_signals('menu_file', menu_file_connections)

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
        self._menuFile.install_menu(file_, ide.toolbar, ide)
        self._menuView.install_menu(view, ide.toolbar, ide)
        self._menuEdit.install_menu(edit, ide.toolbar)
        self._menuSource.install_menu(source)
        self._menuProject.install_menu(project, ide.toolbar)
        self._menuPlugins.install_menu(ide.pluginsMenu)
        self._menuAbout.install_menu(about)

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


menu = _MenuBar()