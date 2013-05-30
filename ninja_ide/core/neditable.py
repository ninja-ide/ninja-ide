# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.editor import checkers


class NEditable(QObject):

    def __init__(self):
        super(NEditable, self).__init__()
        self.text_modified = False
        self.new_document = True

        self.registered_checkers = checkers.get_checkers_for()
        for i, values in self.registered_checkers:
            Checker, color = values
            check = Checker(self)
            self.registered_checkers[i] = (check, color)
            self.connect(check, SIGNAL("finished()"),
                self.show_errors_notifications)

    def show_errors_notifications(self):
        """Show the notifications obtained for the proper checker."""
        pass