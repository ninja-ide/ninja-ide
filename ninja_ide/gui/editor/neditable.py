# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.editor import checkers
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.editor import editor


class NEditable(QObject):
    """
    SIGNALS:
    @checkersUpdated()
    """

    def __init__(self, filename=None):
        super(NEditable, self).__init__()
        self.__id = ''
        #Create NFile
        if filename is None:
            #temp file
            self.__id = 'temp'
        else:
            self.__id = filename
        self.text_modified = False
        self.new_document = True
        self._has_checkers = False
        self._lang = 'python'

        #Checkers:
        self.registered_checkers = []
        self._checkers_executed = 0

        self._ui_instance = None

        self.include_checkers()

    @property
    def ID(self):
        return self.__id

    @property
    def has_checkers(self):
        """Return True if checkers where installaed, False otherwise"""
        return self._has_checkers

    def build_ui(self):
        """Return an Editor instance."""
        if not self._ui_instance:
            #TODO: Complete Editor data (analyze)
            self._ui_instance = editor.create_editor(self)
        return self._ui_instance

    def include_checkers(self, lang='python'):
        """Initialize the Checkers, should be refreshed on checkers change."""
        self._lang = lang
        self.registered_checkers = sorted(checkers.get_checkers_for(lang),
            key=lambda x: x[2])
        self._has_checkers = len(self.registered_checkers) > 0
        for i, values in enumerate(self.registered_checkers):
            Checker, color, priority = values
            check = Checker(self)
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

    def run_checkers(self):
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