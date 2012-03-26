# *-* coding: utf-8 *-*
from __future__ import absolute_import

import compiler

from PyQt4.QtCore import QThread

from ninja_ide.core import file_manager
from ninja_ide.core import settings
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
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._editor.ID)
        if file_ext in exts:
            try:
                self.reset()
                parseResult = compiler.parse(open(self._editor.ID).read())
                self.checker = checker.Checker(parseResult, self._editor.ID)
                for m in self.checker.messages:
                    lineno = m.lineno - 1
                    if lineno not in self.errorsSummary:
                        message = [m.message % m.message_args]
                    else:
                        message = self.errorsSummary[lineno]
                        message += [m.message % m.message_args]
                    self.errorsSummary[lineno] = message
            except Exception, reason:
                self.errorsSummary[reason.lineno - 1] = [reason.msg]
        else:
            self.reset()
