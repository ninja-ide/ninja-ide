# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject

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


#Register MenuBar
ide.IDE.register_service(MenuBar(), 'menu_bar')