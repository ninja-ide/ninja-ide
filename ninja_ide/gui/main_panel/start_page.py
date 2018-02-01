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

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout
)
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    QUrl
)

from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide import resources


class StartPage(QWidget):
    # Signals
    openPreferences = pyqtSignal()
    newFile = pyqtSignal()

    def __init__(self, parent=None):
        super(StartPage, self).__init__(parent)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.view = QQuickWidget()
        self.view.rootContext().setContextProperty(
            "theme", resources.QML_COLORS)
        self.view.rootContext().setContextProperty(
            "shortcuts", self.get_shortcuts())
        self.view.setMinimumWidth(400)
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("StartPage.qml"))
        self.root = self.view.rootObject()
        vbox.addWidget(self.view)

        # Connections
        self.root.onDrop.connect(self.__open_drop_files)
        self.root.openProject.connect(self._open_project)
        self.root.newFile.connect(lambda: self.newFile.emit())
        self.load_items()

    @pyqtSlot('QString')
    def _open_project(self, path):
        projects_explorer = IDE.get_service("projects_explorer")
        projects_explorer.open_project_folder(path)

    def get_shortcuts(self):
        shortcuts = {k: v.toString() for k, v in resources.SHORTCUTS.items()}
        return shortcuts

    def load_items(self):
        # dsettings = IDE.data_settings()
        # recent_projects_dict = dict(dsettings.value('recentProjects', {}))
        # for prj, values in recent_projects_dict.items():
        #    prj_name = values["name"]
        #    last_open = values["lastopen"]
        #    self.root.addProject(prj_name, prj, last_open)
        self.root.forceActiveFocus()
        """
        # Connections
        self.root.openProject['QString'].connect(self._open_project)
        self.root.removeProject['QString'].connect(self._on_click_on_delete)
        self.root.markAsFavorite['QString',
                                 bool].connect(self._on_click_on_favorite)
        self.root.openPreferences.connect(
            lambda: self.openPreferences.emit())
        self.root.newFile.connect(lambda: self.newFile.emit())

    def _open_project(self, path):
        projects_explorer = IDE.get_service('projects_explorer')
        if projects_explorer:
            projects_explorer.open_project_folder(path)

    def _on_click_on_delete(self, path):
        settings = IDE.data_settings()
        recent_projects = settings.value("recentProjects")
        if path in recent_projects:
            del recent_projects[path]
            settings.setValue("recentProjects", recent_projects)

    def _on_click_on_favorite(self, path, value):
        settings = IDE.data_settings()
        recent_projects = settings.value("recentProjects")
        properties = recent_projects[path]
        properties["isFavorite"] = value
        recent_projects[path] = properties
        settings.setValue("recentProjects", recent_projects)

    def load_items(self):
        settings = IDE.data_settings()
        listByFavorites = []
        listNoneFavorites = []
        recent_projects_dict = dict(settings.value('recentProjects', {}))
        # Filter for favorites
        for recent_project_path, content in list(recent_projects_dict.items()):
            if bool(dict(content)["isFavorite"]):
                listByFavorites.append((recent_project_path,
                                        content["lastopen"]))
            else:
                listNoneFavorites.append((recent_project_path,
                                          content["lastopen"]))
        if len(listByFavorites) > 1:
            # sort by date favorites
            listByFavorites = sorted(listByFavorites,
                                     key=lambda date: listByFavorites[1])

        if len(listNoneFavorites) > 1:
            # sort by date last used
            listNoneFavorites = sorted(listNoneFavorites,
                                       key=lambda date: listNoneFavorites[1])

        for recent_project_path in listByFavorites:
            path = recent_project_path[0]
            name = recent_projects_dict[path]['name']
            self.root.add_project(name, path, True)

        for recent_project_path in listNoneFavorites:
            path = recent_project_path[0]
            name = recent_projects_dict[path]['name']
            self.root.add_project(name, path, False)
        self.root.forceActiveFocus()
    """

    def __open_drop_files(self, files: str):

        """Open dragged files to Start Page"""
        files = files.split(',')  # FIXME: it's ok?
        main_container = IDE.get_service("main_container")
        for f in files:
            main_container.open_file(QUrl(f).toLocalFile())
