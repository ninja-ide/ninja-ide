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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QCursor
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QString
from PyQt4.QtCore import Qt

from ninja_ide import resources


class RecentProjectItem(QWidget):

###############################################################################
# RecentProjectItem SIGNALS
###############################################################################
    """
    deleteMe(QListWidgetItem)
    clicked(QString)
    favoriteChange(bool)
    """
###############################################################################

    def __init__(self, project, content, itemRelated, parent=None):
        QWidget.__init__(self, parent)
        self.__content = content.toMap()
        self.__project = project
        self.__favorite = QPushButton(self)
        self.__favorite.setObjectName('web_list_button')
        self.__delete = QPushButton(self)
        self.__delete.setObjectName('web_list_button')
        self.__delete.setIcon(QIcon(resources.IMAGES['delProj']))
        self.__name = QLineEdit(self)
        self.__itemRelated = itemRelated
        self.setMouseTracking(True)
        self.__name.setText(self.__content[QString("name")].toString())

        if QString("description") in self.__content:
            description = self.__content[QString("description")].toString()
        else:
            description = self.tr("no description available")
        self.__name.setToolTip(self.tr(self.__project) + '\n\n' + description)
        self.__delete.setToolTip(self.tr("Click to delete from the list"))
        self.__favorite.setToolTip(self.tr("Click to dock on the list"))
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.__favorite)
        hbox.addWidget(self.__name)
        hbox.addWidget(self.__delete)
        self.__name.setCursor(QCursor(Qt.ArrowCursor))
        self.__name.setReadOnly(True)
        self.connect(self.__favorite, SIGNAL("clicked(bool)"),
            self.__on_click_on_favorite)
        self.connect(self.__delete, SIGNAL("clicked(bool)"),
            self.__on_click_on_delete)
        #TODO: Change this click listen it doesn't work with ReadOnly = True
        self.connect(self.__name,
            SIGNAL("cursorPositionChanged(int, int)"), self.__on_click_on_name)
        self._set_favorite(self.__content[QString("isFavorite")].toBool())

    def __on_click_on_delete(self):
        settings = QSettings()
        recent_projects = settings.value("recentProjects").toMap()
        if self.__project in recent_projects:
            del recent_projects[self.__project]
            settings.setValue("recentProjects", recent_projects)
            self.emit(SIGNAL("deleteMe(QListWidgetItem)"), self.__itemRelated)

    def __on_click_on_favorite(self):
        settings = QSettings()
        recent_projects = settings.value("recentProjects").toMap()
        properties = recent_projects[self.__project].toMap()
        properties[QString("isFavorite")] = not properties[
            QString("isFavorite")].toBool()
        recent_projects[self.__project] = properties
        settings.setValue("recentProjects", recent_projects)
        self.emit(SIGNAL("favoriteChange(bool)"), properties[
            QString("isFavorite")])
        self._set_favorite(properties[QString("isFavorite")])

    def __on_click_on_name(self, uno, dos):
        self.emit(SIGNAL("clicked(QString)"), self.__project)

    def _set_favorite(self, isFavorite):
        if isFavorite:
            self.__favorite.setIcon(QIcon(resources.IMAGES['favProj']))
            self.__favorite.setToolTip(
                self.tr("Click to remove from favorite projects"))
        else:
            self.__favorite.setIcon(QIcon(resources.IMAGES['unfavProj']))
            self.__favorite.setToolTip(
                self.tr("Click to add to favorite projects"))

    def get_project_path(self):
        return self.__project

    def get_item(self):
        return self.__itemRelated
