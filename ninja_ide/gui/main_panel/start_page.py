# -*- coding: utf-8 -*-
import os
from urlparse import urlparse, urlunparse

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import QDir
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide import resources
from ninja_ide.gui.main_panel import itab_item


class StartPage(QWidget, itab_item.ITabItem):

    def __init__(self, parent=None):
        super(StartPage, self).__init__(parent)
        self._id = "Start Page"
        vbox = QVBoxLayout(self)
        self.view = QDeclarativeView()
        self.view.setMinimumWidth(400)
        self.view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        path_qml = QDir.fromNativeSeparators(
            os.path.join(resources.QML_FILES, "StartPage.qml"))
        path_qml = urlunparse(urlparse(path_qml)._replace(scheme='file'))
        self.view.setSource(QUrl(path_qml))
        self.root = self.view.rootObject()
        vbox.addWidget(self.view)

        self.load_items()

        self.connect(self.root, SIGNAL("openProject(QString)"),
            self._open_project)
        self.connect(self.root, SIGNAL("removeProject(QString)"),
            self._on_click_on_delete)
        self.connect(self.root, SIGNAL("markAsFavorite(QString, bool)"),
            self._on_click_on_favorite)
        self.connect(self.root, SIGNAL("openPreferences()"),
            lambda: self.emit(SIGNAL("openPreferences()")))

    def _open_project(self, path):
        self.emit(SIGNAL("openProject(QString)"), path)

    def _on_click_on_delete(self, path):
        settings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        recent_projects = settings.value("recentProjects")
        if path in recent_projects:
            del recent_projects[path]
            settings.setValue("recentProjects", recent_projects)

    def _on_click_on_favorite(self, path, value):
        settings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        recent_projects = settings.value("recentProjects")
        properties = recent_projects[path]
        properties["isFavorite"] = value
        recent_projects[path] = properties
        settings.setValue("recentProjects", recent_projects)

    def load_items(self):
        settings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        listByFavorites = []
        listNoneFavorites = []
        recent_projects_dict = dict(settings.value('recentProjects', {}))
        #Filter for favorites
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
            #sort by date last used
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