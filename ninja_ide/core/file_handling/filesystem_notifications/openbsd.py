# -*- coding: utf-8 *-*
from ninja_ide.core.file_handling.filesystem_notifications import base_watcher
from PyQt5.QtCore import pyqtSignal


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        self.watching_paths = {}
        super(NinjaFileSystemWatcher, self).__init__()
        self._ignore_hidden = ('.git', '.hg', '.svn', '.bzr')

    def add_watch(self, path):
        pass

    def remove_watch(self, path):
        pass

    def shutdown_notification(self):
        base_watcher.BaseWatcher.shutdown_notification(self)

    def _emit_signal_on_change(self, event, path):
        self.fileChanged.emit(event, path)
