# *-* coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtCore import QThread

from ninja_ide.core import file_manager
from ninja_ide.dependencies import pep8mod


class Pep8Checker(QThread):

    def __init__(self, editor):
        QThread.__init__(self)
        self._editor = editor
        self.pep8checks = []
        self.pep8lines = []

    def check_style(self):
        if not self.isRunning():
            self.start()
            self.setPriority(QThread.LowPriority)

    def reset(self):
        self.pep8checks = []
        self.pep8lines = []

    def run(self):
        if file_manager.get_file_extension(self._editor.ID) == 'py':
            self.reset()
            tempChecks = []
            self.pep8checks = pep8mod.run_check(self._editor.ID)
            line = u''
            repeated = False
            addLine = True
            for p in self.pep8checks:
                if p.find('.py:') > 0:
                    if len(line) != 0:
                        tempChecks.append(line)
                        line = ''
                        addLine = True
                    startPos = p.find('.py:') + 4
                    endPos = p.find(':', startPos)
                    lineno = p[startPos:endPos]
                    if lineno.isdigit():
                        if int(lineno) in self.pep8lines:
                            repeated = True
                        else:
                            self.pep8lines.append(int(lineno))
                    else:
                        continue
                    line += unicode(p[p.find(':', endPos + 1) + 2:]) + '\n'
                elif addLine:
                    line += p + '\n'
                    addLine = False
                else:
                    line += p
            if len(line) != 0:
                if repeated:
                    repeated = False
                    previousLine = tempChecks[-1]
                    previousLine += '\n' + line
                    tempChecks[-1] = previousLine
                else:
                    tempChecks.append(line)
            self.pep8checks = tempChecks
        else:
            self.reset()
