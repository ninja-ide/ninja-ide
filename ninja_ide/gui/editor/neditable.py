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
import collections

from PyQt5.QtCore import (
    QObject,
    pyqtSignal
)

from ninja_ide.core.file_handling import file_manager
from ninja_ide.core.file_handling import nswapfile
from ninja_ide.gui.editor import checkers
from ninja_ide.gui.editor import helpers
from ninja_ide.core import settings


class NEditable(QObject):
    """
    SIGNALS:
    @checkersUpdated(PyQt_PyObject)
    @askForSaveFileClosing(PyQt_PyObject)
    @fileClosing(PyQt_PyObject)
    @fileSaved(PyQt_PyObject)
    """
    fileSaved = pyqtSignal('PyQt_PyObject')
    fileLoaded = pyqtSignal('PyQt_PyObject')
    canBeRecovered = pyqtSignal('PyQt_PyObject')
    fileRemoved = pyqtSignal('PyQt_PyObject')
    fileChanged = pyqtSignal('PyQt_PyObject')
    fileClosing = pyqtSignal('PyQt_PyObject')
    askForSaveFileClosing = pyqtSignal('PyQt_PyObject')
    checkersUpdated = pyqtSignal('PyQt_PyObject')

    def __init__(self, nfile=None):
        super(NEditable, self).__init__()
        self.__editor = None
        # Create NFile
        self._nfile = nfile
        self._has_checkers = False
        self.__language = None
        self.text_modified = False
        self.ignore_checkers = False
        # Swap File
        self._swap_file = None
        # Checkers:
        self.registered_checkers = []
        self._checkers_executed = 0

        # Connect signals
        if self._nfile:
            self._nfile.fileClosing['QString',
                                    bool].connect(self._about_to_close_file)
            self._nfile.fileChanged.connect(
                lambda: self.fileChanged.emit(self))
            self._nfile.fileRemoved.connect(
                self._on_file_removed_from_disk)

    def _on_file_removed_from_disk(self):
        # FIXME: maybe we should ask for save, save as...
        self._nfile.close()

    def extension(self):
        # FIXME This sucks, we should have a way to define lang
        if self._nfile is None:
            return ""
        return self._nfile.file_ext()

    def language(self):
        if self.__language is None:
            self.__language = settings.LANGUAGE_MAP.get(self.extension())
            if self.__language is None and self._nfile.is_new_file:
                self.__language = "python"
        return self.__language

    def _about_to_close_file(self, path, force_close):
        modified = False
        if self.__editor:
            modified = self.__editor.is_modified
        if modified and not force_close:
            self.askForSaveFileClosing.emit(self)
        else:
            self._nfile.remove_watcher()
            self.fileClosing.emit(self)

    def clone(self):
        clone = self.__class__(self._nfile)
        return clone

    def set_editor(self, editor):
        """Set the Editor (UI component) associated with this object."""
        self.__editor = editor
        # If we have an editor, let's include the checkers:
        self.include_checkers(self.language())
        content = ''
        if not self._nfile.is_new_file:
            content = self._nfile.read()
            self._nfile.start_watching()
            self.__editor.text = content
            self.__editor.document().setModified(False)
            self.create_swap_file()
            encoding = file_manager.get_file_encoding(content)
            self.__editor.encoding = encoding
            if not self.ignore_checkers:
                self.run_checkers(content)
            else:
                self.ignore_checkers = False

        # New file then try to add a coding line
        if not content:
            helpers.insert_coding_line(self.__editor)

        self.fileLoaded.emit(self)

    def create_swap_file(self):
        if settings.SWAP_FILE:
            self._swap_file = nswapfile.NSwapFile(self)
            self._swap_file.canBeRecovered.connect(
                lambda: self.canBeRecovered.emit(self))

    def reload_file(self):
        if self._nfile:
            content = self._nfile.read()
            self._nfile.start_watching()
            self.__editor.text = content
            self.__editor.document().setModified(False)
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
    def swap_file(self):
        return self._swap_file

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

    def save_content(self, path=None, force=False):
        """Save the content of the UI to a file."""

        if self._swap_file is None:
            self.create_swap_file()
        if self.__editor.is_modified or force:
            content = self.__editor.text
            nfile = self._nfile.save(content, path)
            self._nfile = nfile
            if not self.ignore_checkers:
                self.run_checkers(content)
            else:
                self.ignore_checkers = False
            self.__editor.document().setModified(False)
            self.fileSaved.emit(self)

    def include_checkers(self, lang='python'):
        """Initialize the Checkers, should be refreshed on checkers change."""
        self.registered_checkers = sorted(checkers.get_checkers_for(lang),
                                          key=lambda x: x[2])
        self._has_checkers = len(self.registered_checkers) > 0
        for i, values in enumerate(self.registered_checkers):
            Checker, color, priority = values
            check = Checker(self.__editor)
            self.registered_checkers[i] = (check, color, priority)
            check.finished.connect(self.show_checkers_notifications)

    def run_checkers(self, content, path=None, encoding=None):
        for items in self.registered_checkers:
            checker = items[0]
            checker.run_checks()

    def show_checkers_notifications(self):
        """Show the notifications obtained for the proper checker."""
        self._checkers_executed += 1
        if self._checkers_executed == len(self.registered_checkers):
            self._checkers_executed = 0
            self.checkersUpdated.emit(self)

    def update_checkers_display(self):
        for items in self.registered_checkers:
            checker, _, _ = items
            func = getattr(checker, 'refresh_display', None)
            if isinstance(func, collections.Callable):
                func()
