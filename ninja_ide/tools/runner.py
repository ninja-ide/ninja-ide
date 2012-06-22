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
import code
import subprocess

from PyQt4.QtNetwork import QHostAddress
from PyQt4.QtNetwork import QTcpServer


def run_code(codes):
    interpreter = code.InteractiveInterpreter()
    interpreter.runcode(codes)


def run_code_from_file(fileName):
    subprocess.Popen(['python', fileName])


def isAvailable(port):
    server = QTcpServer()
    result = server.listen(QHostAddress("127.0.0.1"), port)
    server.close()
    return result


def start_pydoc():
    port = 6452
    retry = 10
    while retry > 0 and not isAvailable(port):
        retry -= 1
        port += 10
    proc = subprocess.Popen(['pydoc', '-p', str(port)]), \
        ('http://127.0.0.1:' + str(port) + '/')
    return proc
