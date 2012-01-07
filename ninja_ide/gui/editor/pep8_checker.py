# *-* coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtCore import QThread

from ninja_ide.core import file_manager
from ninja_ide.dependencies import pep8mod


class Pep8Checker(QThread):

    def __init__(self, editor):
        QThread.__init__(self)
        self._editor = editor
        self.pep8checks = {}

    def check_style(self):
        if not self.isRunning():
            self.start()
            self.setPriority(QThread.LowPriority)

    def reset(self):
        self.pep8checks = {}

    def run(self):
        if file_manager.get_file_extension(self._editor.ID) == 'py':
            self.reset()
            tempData = pep8mod.run_check(self._editor.ID)
            i = 0
            while i < len(tempData):
                lineno = -1
                try:
                    startPos = tempData[i].find('.py:') + 4
                    endPos = tempData[i].find(':', startPos)
                    lineno = int(tempData[i][startPos:endPos])
                    error = unicode(tempData[i][tempData[i].find(
                        ':', endPos + 1) + 2:])
                    line = u'\n'.join(
                        [error, tempData[i + 1], tempData[i + 2]])
                except:
                    line = ''
                finally:
                    i += 3
                if line and lineno > -1:
                    if lineno not in self.pep8checks:
                        self.pep8checks[lineno] = [line]
                    else:
                        message = self.pep8checks[lineno]
                        message += [line]
                        self.pep8checks[lineno] = message
        else:
            self.reset()
