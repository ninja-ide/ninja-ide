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
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL


class SessionsManager(QDialog):

    """Session Manager, to load different configurations of ninja."""

    def __init__(self, load_func, create_func, save_func,
            profiles, parent=None):
        super(ProfilesManager, self).__init__(parent, Qt.Dialog)
        self.setWindowTitle(self.tr("Session Manager"))
        self.setMinimumWidth(400)
        self._profiles = profiles
        self.load_function = load_func
        self.create_function = create_func
        self.save_function = save_func
        self.ide = parent
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel(self.tr("Save your opened files and projects "
                        "into a profile and change really quick\n"
                        "between projects and files sessions.\n"
                        "This allows you to save your working environment, "
                        "keep working in another\nproject and then go back "
                        "exactly where you left.")))
        self.profileList = QListWidget()
        self.profileList.addItems([key for key in profiles])
        self.profileList.setCurrentRow(0)
        self.contentList = QListWidget()
        self.btnDelete = QPushButton(self.tr("Delete Profile"))
        self.btnDelete.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnUpdate = QPushButton(self.tr("Update Profile"))
        self.btnUpdate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnCreate = QPushButton(self.tr("Create New Profile"))
        self.btnCreate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnOpen = QPushButton(self.tr("Open Profile"))
        self.btnOpen.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnOpen.setDefault(True)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnDelete)
        hbox.addWidget(self.btnUpdate)
        hbox.addWidget(self.btnCreate)
        hbox.addWidget(self.btnOpen)

        vbox.addWidget(self.profileList)
        vbox.addWidget(self.contentList)
        vbox.addLayout(hbox)

        self.connect(self.profileList, SIGNAL("itemSelectionChanged()"),
            self.load_profile_content)
        self.connect(self.btnOpen, SIGNAL("clicked()"), self.open_profile)
        self.connect(self.btnUpdate, SIGNAL("clicked()"), self.save_profile)
        self.connect(self.btnCreate, SIGNAL("clicked()"), self.create_profile)
        self.connect(self.btnDelete, SIGNAL("clicked()"), self.delete_profile)

    def load_profile_content(self):
        """Load the selected profile, replacing the current session."""
        item = self.profileList.currentItem()
        self.contentList.clear()
        if item is not None:
            key = item.text()
            files = [self.tr('Files:')] + \
                [file[0] for file in self._profiles[key][0]]
            projects = [self.tr('Projects:')] + self._profiles[key][1]
            content = files + projects
            self.contentList.addItems(content)

    def create_profile(self):
        """Create a new Profile."""
        profileName = self.create_function()
        self.ide.Profile = profileName
        self.close()

    def save_profile(self):
        if self.profileList.currentItem():
            profileName = self.profileList.currentItem().text()
            self.save_function(profileName)
            self.ide.show_message(self.tr("Profile %s Updated!") %
                profileName, 2000)
            self.load_profile_content()

    def open_profile(self):
        if self.profileList.currentItem():
            key = self.profileList.currentItem().text()
            self.load_function(key)
            self.ide.Profile = key
            self.close()

    def delete_profile(self):
        if self.profileList.currentItem():
            key = self.profileList.currentItem().text()
            self._profiles.pop(key)
            self.profileList.takeItem(self.profileList.currentRow())
            self.contentList.clear()
