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

import os

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager


class SessionsManager(QDialog):

    """Session Manager, to load different configurations of ninja."""

    def __init__(self, parent=None):
        super(SessionsManager, self).__init__(parent, Qt.Dialog)
        self._ide = parent
        self.setModal(True)
        self.setWindowTitle(translations.TR_SESSIONS_TITLE)
        self.setMinimumWidth(400)
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel(translations.TR_SESSIONS_DIALOG_BODY))
        self.sessionList = QListWidget()
        self.sessionList.addItems([key for key in settings.SESSIONS])
        self.sessionList.setCurrentRow(0)
        self.contentList = QListWidget()
        self.btnDelete = QPushButton(translations.TR_SESSIONS_BTN_DELETE)
        self.btnDelete.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnUpdate = QPushButton(translations.TR_SESSIONS_BTN_UPDATE)
        self.btnUpdate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnCreate = QPushButton(translations.TR_SESSIONS_BTN_CREATE)
        self.btnCreate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnOpen = QPushButton(translations.TR_SESSIONS_BTN_ACTIVATE)
        self.btnOpen.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnOpen.setDefault(True)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnDelete)
        hbox.addWidget(self.btnUpdate)
        hbox.addWidget(self.btnCreate)
        hbox.addWidget(self.btnOpen)

        vbox.addWidget(self.sessionList)
        vbox.addWidget(self.contentList)
        vbox.addLayout(hbox)

        self.sessionList.itemSelectionChanged.connect(
            self.load_session_content)
        self.btnOpen.clicked.connect(self.open_session)
        self.btnUpdate.clicked.connect(self.save_session)
        self.btnCreate.clicked.connect(self.create_session)
        self.btnDelete.clicked.connect(self.delete_session)
        self.load_session_content()

    def load_session_content(self):
        """Load the selected session, replacing the current session."""
        item = self.sessionList.currentItem()
        self.contentList.clear()
        if item is not None:
            key = item.text()
            files = [translations.TR_FILES] + \
                [file[0] for file in settings.SESSIONS[key][0]]
            projects = [translations.TR_PROJECT] + settings.SESSIONS[key][1]
            content = files + projects
            self.contentList.addItems(content)

    def create_session(self):
        """Create a new Session."""
        sessionInfo = QInputDialog.getText(
            None, translations.TR_SESSIONS_CREATE_TITLE,
            translations.TR_SESSIONS_CREATE_BODY)
        if sessionInfo[1]:
            sessionName = sessionInfo[0]
            if not sessionName or sessionName in settings.SESSIONS:
                QMessageBox.information(
                    self,
                    translations.TR_SESSIONS_MESSAGE_TITLE,
                    translations.TR_SESSIONS_MESSAGE_BODY)
                return
            SessionsManager.save_session_data(sessionName, self._ide)
        self._ide.Session = sessionName
        self.close()

    @classmethod
    def save_session_data(cls, sessionName, ide):
        """Save the updates from a session."""
        openedFiles = ide.filesystem.get_files()
        files_info = []
        for path in openedFiles:
            editable = ide.get_or_create_editable(path)
            if editable.is_dirty:
                stat_value = 0
            else:
                stat_value = os.stat(path).st_mtime
            files_info.append([path,
                               editable.editor.cursor_position, stat_value])
        projects_obj = ide.filesystem.get_projects()
        projects = [projects_obj[proj].path for proj in projects_obj]
        settings.SESSIONS[sessionName] = [files_info, projects]
        qsettings = ide.data_settings()
        qsettings.setValue('ide/sessions', settings.SESSIONS)

    def save_session(self):
        """Save current session"""
        if self.sessionList.currentItem():
            sessionName = self.sessionList.currentItem().text()
            SessionsManager.save_session_data(sessionName, self._ide)
            self._ide.show_message(translations.TR_SESSIONS_UPDATED_NOTIF %
                                   {'session': sessionName}, 2000)
            self.load_session_content()

    def open_session(self):
        """Open a saved session"""
        if self.sessionList.currentItem():
            key = self.sessionList.currentItem().text()
            self._load_session_data(key)
            self._ide.Session = key
            self.close()

    def delete_session(self):
        """Delete a session"""
        if self.sessionList.currentItem():
            key = self.sessionList.currentItem().text()
            settings.SESSIONS.pop(key)
            self.sessionList.takeItem(self.sessionList.currentRow())
            self.contentList.clear()
            qsettings = self._ide.data_settings()
            qsettings.setValue('ide/sessions', settings.SESSIONS)

    def _load_session_data(self, key):
        """Activate the selected session, closing the current files/projects"""
        main_container = self._ide.get_service('main_container')
        projects_explorer = self._ide.get_service('projects_explorer')
        if projects_explorer and main_container:
            projects_explorer.close_opened_projects()
            for fileData in settings.SESSIONS[key][0]:
                path, (line, col), stat_value = fileData
                if file_manager.file_exists(path):
                    mtime = os.stat(path).st_mtime
                    ignore_checkers = (mtime == stat_value)
                    main_container.open_file(path, line, col,
                                             ignore_checkers=ignore_checkers)
            if projects_explorer:
                projects_explorer.load_session_projects(
                    settings.SESSIONS[key][1])
