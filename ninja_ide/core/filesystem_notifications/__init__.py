# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys


if sys.platform == 'win32':
    from ninja_ide.core.filesystem_notifications import windows
    source = windows
elif sys.platform == 'darwin':
    from ninja_ide.core.filesystem_notifications import darwin
    source = darwin
else:
    from ninja_ide.core.filesystem_notifications import linux
    source = linux


NinjaFileSystemWatcher = source.NinjaFileSystemWatcher()
