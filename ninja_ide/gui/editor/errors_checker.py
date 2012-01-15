# *-* coding: utf-8 *-*
from __future__ import absolute_import

import compiler

from PyQt4.QtCore import QThread

from ninja_ide.core import file_manager
from ninja_ide.dependencies.pyflakes_mod import checker


class ErrorsChecker(QThread):

    def __init__(self, editor):
        QThread.__init__(self)
        self._editor = editor
        self.errorsSummary = {}

    def check_errors(self):
        if not self.isRunning():
            self.start()
            self.setPriority(QThread.LowPriority)

    def reset(self):
        self.errorsSummary = {}

    def run(self):
        if file_manager.get_file_extension(self._editor.ID) == 'py':
            try:
                self.reset()
                parseResult = compiler.parse(open(self._editor.ID).read())
                self.checker = checker.Checker(parseResult, self._editor.ID)
                for m in self.checker.messages:
                    print m.message
                    if m.lineno not in self.errorsSummary:
                        message = [m.message % m.message_args]
                    else:
                        message = self.errorsSummary[m.lineno]
                        message += [m.message % m.message_args]
                    self.errorsSummary[m.lineno] = message
            except Exception, reason:
                self.errorsSummary[reason.lineno] = [reason.msg]
        else:
            self.reset()
