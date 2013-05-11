# -*- coding: utf-8 *-*
from ninja_ide.core.filesystem_notifications import base_watcher
from PyQt4.QtCore import SIGNAL


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
        self.emit(SIGNAL("fileChanged(int, QString)"), event, path)
