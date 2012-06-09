# -*- coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtCore import SIGNAL

from ninja_ide.core.filesystem_notifications import base_watcher


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        super(NinjaFileSystemWatcher, self).__init__()
        # do stuff
        self.watching_paths = []

    def add_watch(self, path):
        if path not in self.watching_paths:
            self.watching_paths.append(path)
            # Add real watcher using platform specific things

    def remove_watch(self, path):
        if path in self.watching_paths:
            self.watching_paths.remove(path)
            # Remove real watcher using platform specific things

    def _emit_signal_on_change(self, event):
        oper = event.operation
        path = event.path
        self.emit(SIGNAL("fileChanged(int, QString)"), oper, path)
