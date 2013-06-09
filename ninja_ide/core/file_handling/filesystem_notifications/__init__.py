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

try:
    if sys.platform == 'win32':
        from ninja_ide.core.file_handling.filesystem_notifications import windows
        source = windows
    elif sys.platform == 'darwin':
        from ninja_ide.core.file_handling.filesystem_notifications import darwin
        source = darwin
    elif sys.platform.startswith("linux"):
        from ninja_ide.core.file_handling.filesystem_notifications import linux
        source = linux
    else:
        #Aything we do not have a clue how to handle
        from ninja_ide.core.file_handling.filesystem_notifications import openbsd
        source = openbsd
except:
    from ninja_ide.core.file_handling.filesystem_notifications import openbsd
    source = openbsd


NinjaFileSystemWatcher = source.NinjaFileSystemWatcher()
