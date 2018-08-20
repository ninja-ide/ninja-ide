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

import os

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)


class _SessionManager(QObject):

    aboutToSaveSession = pyqtSignal()
    sessionChanged = pyqtSignal()

    def __init__(self, ninjaide):
        QObject.__init__(self)
        self._ide = ninjaide
        self.__sessions = {}
        self.__session = None

        self._ide.goingDown.connect(self.save)
        self.sessionChanged.connect(self._ide.change_window_title)

    @property
    def sessions(self):
        return self.__sessions

    def get_session(self, session_name):
        return self.__sessions.get(session_name)

    def current_session(self):
        return self.__session

    def set_current_session(self, session_name):
        if session_name != self.__session:
            self.__session = session_name
            self.sessionChanged.emit()

    def delete_session(self, session_name):
        if session_name in self.__sessions:
            del self.__sessions[session_name]
            data_settings = self._ide.data_settings()
            data_settings.setValue("ide/sessions", self.__sessions)

    def load_sessions(self):
        data_settings = self._ide.data_settings()
        sessions = data_settings.value("ide/sessions")
        if sessions:
            self.__sessions = sessions

    def load_session(self, session_name):
        """Activate the selected session, closing the current files/projects"""

        main_container = self._ide.get_service("main_container")
        projects_explorer = self._ide.get_service("projects_explorer")
        if projects_explorer and main_container:
            projects_explorer.close_opened_projects()

            for file_data in self.__sessions[session_name][0]:
                path, (line, col), stat_value = file_data
                if file_manager.file_exists(path):
                    mtime = os.stat(path).st_mtime
                    ignore_checkers = (mtime == stat_value)
                    main_container.open_file(path, line, col,
                                             ignore_checkers=ignore_checkers)
            if projects_explorer:
                projects_explorer.load_session_projects(
                    self.__sessions[session_name][1])

    def __len__(self):
        return len(self.__sessions)

    def save_session_data(self, session_name):
        self.aboutToSaveSession.emit()
        opened_files = self._ide.filesystem.get_files()
        files_info = []
        for path in opened_files:
            editable = self._ide.get_or_create_editable(path)
            if editable.is_dirty:
                stat_value = 0
            else:
                stat_value = os.stat(path).st_mtime
            files_info.append(
                [path, editable.editor.cursor_position, stat_value])

        projects_obj = self._ide.filesystem.get_projects()
        projects = [projects_obj[proj].path for proj in projects_obj]
        self.__sessions[session_name] = (files_info, projects)

    def save(self):
        logger.debug("Saving {} sessions...".format(len(self)))
        for session_name in self.__sessions.keys():
            self.save_session_data(session_name)
        data_settings = self._ide.data_settings()
        data_settings.setValue("ide/sessions", self.__sessions)


class SessionsManager(QDialog):
    """Session Manager, to load different configurations of ninja."""

    def __init__(self, parent=None):
        super(SessionsManager, self).__init__(parent, Qt.Dialog)
        self._ninja = parent
        self.setModal(True)
        self.setWindowTitle(translations.TR_SESSIONS_TITLE)
        self.setMinimumWidth(550)
        self.setMinimumHeight(450)
        self._manager = _SessionManager(parent)
        self._load_ui()

    def install(self):
        self._manager.load_sessions()

    def _load_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel(translations.TR_SESSIONS_DIALOG_BODY))
        main_hbox = QHBoxLayout()
        # Session list
        session_layout = QVBoxLayout()
        self._session_list = QTreeWidget()
        self._session_list.setHeaderLabels(["Session", "Last Modified"])
        session_layout.addWidget(self._session_list)
        # Content frame
        content_frame = QFrame()
        content_frame.hide()
        frame_layout = QVBoxLayout(content_frame)
        content_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        session_layout.addWidget(content_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        self._content_list = QTreeWidget()
        self._content_list.setHeaderHidden(True)
        frame_layout.addWidget(self._content_list)
        # Separator line
        line_frame = QFrame()
        line_frame.setFrameStyle(QFrame.VLine | QFrame.Sunken)
        # Buttons
        btn_layout = QVBoxLayout()
        btn_create = QPushButton(translations.TR_SESSIONS_BTN_CREATE)
        btn_activate = QPushButton(translations.TR_SESSIONS_BTN_ACTIVATE)
        btn_update = QPushButton(translations.TR_SESSIONS_BTN_UPDATE)
        btn_delete = QPushButton(translations.TR_SESSIONS_BTN_DELETE)
        btn_details = QPushButton(translations.TR_SESSIONS_BTN_DETAILS)
        btn_details.setCheckable(True)
        # Add buttons to layout
        btn_layout.addWidget(btn_create)
        btn_layout.addWidget(btn_activate)
        btn_layout.addWidget(btn_update)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_details)
        # Add widgets and layouts to the main layout
        main_layout.addLayout(main_hbox)
        main_hbox.addLayout(session_layout)
        main_hbox.addWidget(line_frame)
        main_hbox.addLayout(btn_layout)
        main_hbox.setSizeConstraint(QLayout.SetFixedSize)
        btn_details.toggled[bool].connect(content_frame.setVisible)
        # Connections
        self._session_list.itemSelectionChanged.connect(
            self.load_session_content)
        btn_activate.clicked.connect(self.open_session)
        btn_update.clicked.connect(self.save_session)
        btn_create.clicked.connect(self.create_session)
        btn_delete.clicked.connect(self.delete_session)

    def __load_sessions(self):
        for session_name in self._manager.sessions:
            item = QTreeWidgetItem()
            item.setText(0, session_name)
            item.setText(1, "FIXME: manage this!")
            self._session_list.addTopLevelItem(item)
        self._session_list.setCurrentItem(
            self._session_list.topLevelItem(0))

    def load_session_content(self):
        """Load the selected session, replacing the current session."""
        item = self._session_list.currentItem()
        self._content_list.clear()
        if item is not None:
            key = item.text(0)
            files, projects = self._manager.get_session(key)
            files_parent = QTreeWidgetItem(
                self._content_list, [translations.TR_FILES])
            for ffile in files:
                QTreeWidgetItem(files_parent, [ffile[0]])
            projects_parent = QTreeWidgetItem(
                self._content_list, [translations.TR_PROJECT])
            for project in projects:
                QTreeWidgetItem(projects_parent, [project])

            files_parent.setExpanded(True)
            projects_parent.setExpanded(True)

    def create_session(self):
        """Create a new Session."""
        session_info = QInputDialog.getText(
            None, translations.TR_SESSIONS_CREATE_TITLE,
            translations.TR_SESSIONS_CREATE_BODY)
        if session_info[1]:
            session_name = session_info[0]
            if not session_name or session_name in settings.SESSIONS:
                QMessageBox.information(
                    self,
                    translations.TR_SESSIONS_MESSAGE_TITLE,
                    translations.TR_SESSIONS_MESSAGE_BODY)
                return
            self._manager.save_session_data(session_name)
        self.close()

    def save_session(self):
        """Save current session"""
        if self._session_list.currentItem():
            session_name = self._session_list.currentItem().text(0)
            self._manager.save_session_data(session_name)
            self._ninja.show_message(
                translations.TR_SESSIONS_UPDATED_NOTIF.format(session_name))
            self.load_session_content()

    def open_session(self):
        """Open a saved session"""
        if self._session_list.currentItem():
            session_name = self._session_list.currentItem().text(0)
            self._manager.load_session(session_name)
            self._manager.set_current_session(session_name)
            self.close()

    def delete_session(self):
        """Delete a session"""
        if self._session_list.currentItem():
            key = self._session_list.currentItem().text(0)
            self._manager.delete_session(key)
            self._session_list.takeTopLevelItem(
                self._session_list.currentIndex().row())

    @property
    def current_session(self):
        return self._manager.current_session()

    def showEvent(self, event):
        super().showEvent(event)
        self.__load_sessions()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._session_list.clear()
