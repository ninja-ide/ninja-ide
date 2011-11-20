# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys

from ninja_ide import resources
from ninja_ide.core import cliparser


def run_ninja():
    """First obtain the execution args and create the resources folder."""
    if sys.platform != 'win32':
        try:
            import ctypes
            libc = ctypes.CDLL('libc.so.6')
            procname = 'ninja-ide'
        except:
            print "The process couldn't be renamed'"
    libc.prctl(15, '%s\0' % procname, 0, 0, 0)
    #Set the application name
    filenames, projects_path, extra_plugins = cliparser.parse()
    # Create NINJA-IDE user folder structure for plugins, themes, etc
    resources.create_home_dir_structure()

    # Start the UI
    from ninja_ide.gui import ide
    ide.start(filenames, projects_path, extra_plugins)
