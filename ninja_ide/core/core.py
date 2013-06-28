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

from __future__ import absolute_import

import sys
import signal

from ninja_ide import resources
from ninja_ide.core import cliparser


def run_ninja():
    """First obtain the execution args and create the resources folder."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Change the process name only for linux yet
    if sys.platform != 'win32' and sys.platform != 'darwin':
        try:
            import ctypes
            libc = ctypes.CDLL('libc.so.6')
            procname = 'ninja-ide'
            libc.prctl(15, '%s\0' % procname, 0, 0, 0)
        except:
            print("The process couldn't be renamed'")
    #Set the application name
    (filenames, projects_path,
     extra_plugins, linenos, log_level, log_file) = cliparser.parse()
    # Create NINJA-IDE user folder structure for plugins, themes, etc
    resources.create_home_dir_structure()
    from ninja_ide.tools.logger import NinjaLogger
    NinjaLogger.argparse(log_level, log_file)

    # Start the UI
    from ninja_ide.gui import ide
    ide.start(filenames, projects_path, extra_plugins, linenos)
