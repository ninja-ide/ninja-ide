# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
import signal

from ninja_ide import resources
from ninja_ide.core import cliparser
from ninja_ide.core import ipc


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
            print "The process couldn't be renamed'"
    #Set the application name
    filenames, projects_path, extra_plugins = cliparser.parse()
    # Check if there is another session of ninja-ide opened
    # and in that case send the filenames and projects to that session
    if ipc.is_running() and (filenames or projects_path):
        sended = ipc.send_data(filenames, projects_path)
        if sended:
            sys.exit()
    listener = ipc.SessionListener()
    listener.start()
    # Create NINJA-IDE user folder structure for plugins, themes, etc
    resources.create_home_dir_structure()

    # Start the UI
    from ninja_ide.gui import ide
    try:
        ide.start(listener, filenames, projects_path, extra_plugins)
    finally:
        ipc.close_listener(listener)
