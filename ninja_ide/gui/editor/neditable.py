# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.editor import checkers
from ninja_ide.gui.editor import helpers


class NEditable(QObject):
    """
    SIGNALS:
    @checkersUpdated()
    """

    def __init__(self, nfile=None):
        super(NEditable, self).__init__()
        self.__editor = None
        #Create NFile
        self._nfile = nfile
        self.text_modified = False
        self._has_checkers = False

        #Checkers:
        self.registered_checkers = []
        self._checkers_executed = 0

    def set_editor(self, editor):
        """Set the Editor (UI component) associated with this object."""
        self.__editor = editor
        content = ''
        if not self._nfile.is_new_file:
            content = self._nfile.read()
            self.__editor.setPlainText(content)
            encoding = file_manager.get_file_encoding(content)
            self.__editor.encoding = encoding

        #New file then try to add a coding line
        if not content:
            helpers.insert_coding_line(self.__editor)
        # If we have an editor, let's include the checkers:
        self.include_checkers()

    def save_content(self):
        """Save the content of the UI to a file."""
        content = self.__editor.get_text()
        self._nfile.save(content)

    @property
    def ID(self):
        return self._nfile

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

    def update_checkers_metadata(self, blockNumber, diference):
        """Update the lines in the checkers when the editor change."""
        for i, values in enumerate(self.registered_checkers):
            checker, color, priority = values
            if checker.checks:
                checker.checks = helpers.add_line_increment_for_dict(
                    checker.checks, blockNumber, diference)
        self.emit(SIGNAL("checkersUpdated()"))

    def run_checkers(self, content, path=None, encoding=None):
        for items in self.registered_checkers:
            checker = items[0]
            checker.run_checks()

    def show_checkers_notifications(self):
        """Show the notifications obtained for the proper checker."""
        if self._checkers_executed == len(self.registered_checkers):
            self._checkers_executed = 0
            self.emit(SIGNAL("checkersUpdated()"))
        else:
            self._checkers_executed += 1