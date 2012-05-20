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
        self.sleep(2)
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(self._editor.ID)
        if file_ext in exts:
            try:
                self.reset()
                source = self._editor.get_text()
                if self._editor.encoding is not None:
                    source = source.encode(self._editor.encoding)
                parseResult = compiler.parse(source)
                lint_checker = checker.Checker(parseResult, self._editor.ID)
                for m in lint_checker.messages:
                    lineno = m.lineno - 1
                    if lineno not in self.errorsSummary:
                        message = [m.message % m.message_args]
                    else:
                        message = self.errorsSummary[lineno]
                        message += [m.message % m.message_args]
                    self.errorsSummary[lineno] = message
            except Exception, reason:
                print 'yesssssss'
                message = ''
                if hasattr(reason, 'msg'):
                    message = reason.msg
                else:
                    message = reason.message

                if hasattr(reason, 'lineno'):
                    self.errorsSummary[reason.lineno - 1] = [message]
                else:
                    self.errorsSummary[0] = [message]
        else:
            self.reset()
