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
from __future__ import unicode_literals

import collections

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.editor import checkers
from ninja_ide.gui.editor import helpers


class NEditable(QObject):
    """
    SIGNALS:
    @checkersUpdated(PyQt_PyObject)
    @askForSaveFileClosing(PyQt_PyObject)
    @fileClosing(PyQt_PyObject)
    @fileSaved(PyQt_PyObject)
    """

    def __init__(self, nfile=None):
        super(NEditable, self).__init__()
        self.__editor = None
        # Create NFile
        self._nfile = nfile
        self.text_modified = False
        self._has_checkers = False
        self.ignore_checkers = False

        # Checkers:
        self.registered_checkers = []
        self._checkers_executed = 0

        # Connect signals
        if self._nfile:
            self.connect(self._nfile, SIGNAL("fileClosing(QString, bool)"),
                         self._about_to_close_file)
            self.connect(
                self._nfile, SIGNAL("fileChanged()"),
                lambda: self.emit(SIGNAL("fileChanged(PyQt_PyObject)"), self))

    def extension(self):
        # FIXME This sucks, we should have a way to define lang
        if self._nfile is None:
            return ""
        return self._nfile.file_ext()

    def _about_to_close_file(self, path, force_close):
        modified = False
        if self.__editor:
            modified = self.__editor.is_modified
        if modified and not force_close:
            self.emit(SIGNAL("askForSaveFileClosing(PyQt_PyObject)"), self)
        else:
            self._nfile.remove_watcher()
            self.emit(SIGNAL("fileClosing(PyQt_PyObject)"), self)

    def set_editor(self, editor):
        """Set the Editor (UI component) associated with this object."""
        self.__editor = editor
        # If we have an editor, let's include the checkers:
        self.include_checkers()
        content = ''
        if not self._nfile.is_new_file:
            content = self._nfile.read()
            self._nfile.start_watching()
            self.__editor.setText(content)
            self.__editor.setModified(False)
            encoding = file_manager.get_file_encoding(content)
            self.__editor.encoding = encoding
            if not self.ignore_checkers:
                self.run_checkers(content)
            else:
                self.ignore_checkers = False

        # New file then try to add a coding line
        if not content:
            helpers.insert_coding_line(self.__editor)

    def reload_file(self):
        if self._nfile:
            content = self._nfile.read()
            self._nfile.start_watching()
            self.__editor.setText(content)
            self.__editor.setModified(False)
            encoding = file_manager.get_file_encoding(content)
            self.__editor.encoding = encoding
            if not self.ignore_checkers:
                self.run_checkers(content)
            else:
                self.ignore_checkers = False

    @property
    def file_path(self):
        return self._nfile.file_path

    @property
    def document(self):
        if self.__editor:
            return self.__editor.document()
        return None

    @property
    def display_name(self):
        return self._nfile.display_name

    @property
    def new_document(self):
        return self._nfile.is_new_file

    @property
    def has_checkers(self):
        """Return True if checkers where installaed, False otherwise"""
        return self._has_checkers

    @property
    def editor(self):
        return self.__editor

    @property
    def nfile(self):
        return self._nfile

    @property
    def sorted_checkers(self):
        return sorted(self.registered_checkers,
                      key=lambda x: x[2], reverse=True)

    @property
    def is_dirty(self):
        dirty = False
        for items in self.registered_checkers:
            checker, _, _ = items
            if checker.dirty:
                dirty = True
                break
        return dirty

    def save_content(self, path=None):
        """Save the content of the UI to a file."""
        if self.__editor.is_modified:
            content = self.__editor.text()
            nfile = self._nfile.save(content, path)
            self._nfile = nfile
            if not self.ignore_checkers:
                self.run_checkers(content)
            else:
                self.ignore_checkers = False
            self.__editor.setModified(False)
            self.emit(SIGNAL("fileSaved(PyQt_PyObject)"), self)

    def include_checkers(self, lang='python'):
        """Initialize the Checkers, should be refreshed on checkers change."""
        self.registered_checkers = sorted(checkers.get_checkers_for(lang),
                                          key=lambda x: x[2])
        self._has_checkers = len(self.registered_checkers) > 0
        for i, values in enumerate(self.registered_checkers):
            Checker, color, priority = values
            check = Checker(self.__editor)
            self.registered_checkers[i] = (check, color, priority)
            self.connect(check, SIGNAL("finished()"),
                         self.show_checkers_notifications)

    def run_checkers(self, content, path=None, encoding=None):
        for items in self.registered_checkers:
            checker = items[0]
            checker.run_checks()

    def show_checkers_notifications(self):
        """Show the notifications obtained for the proper checker."""
        self._checkers_executed += 1
        if self._checkers_executed == len(self.registered_checkers):
            self._checkers_executed = 0
            self.emit(SIGNAL("checkersUpdated(PyQt_PyObject)"), self)

    def update_checkers_display(self):
        for items in self.registered_checkers:
            checker, _, _ = items
            func = getattr(checker, 'refresh_display', None)
            if isinstance(func, collections.Callable):
                func()
