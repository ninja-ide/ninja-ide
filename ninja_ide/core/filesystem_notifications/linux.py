# -*- coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtCore import SIGNAL
from pyinotify import ProcessEvent, IN_CREATE, IN_DELETE, IN_DELETE_SELF, \
                        IN_MODIFY, WatchManager, ThreadedNotifier

import logging
logger = logging.getLogger('ninja_ide.core.filesystem_notifications.linux')
DEBUG = logger.debug

from ninja_ide.core.filesystem_notifications import base_watcher

mask = IN_CREATE | IN_DELETE | IN_DELETE_SELF | IN_MODIFY


class NinjaProcessEvent(ProcessEvent):

    def __init__(self, process_callback):
        self._process_callback = process_callback

    def process_IN_CREATE(self, event):
        self._process_callback(base_watcher.BaseWatcher.ADDED, event.path)

    def process_IN_DELETE(self, event):
        self._process_callback(base_watcher.BaseWatcher.DELETED, event.path)

    def process_IN_DELETE_SELF(self, event):
        self._process_callback(base_watcher.BaseWatcher.DELETED, event.path)

    def process_IN_MODIFY(self, event):
        self._process_callback(base_watcher.BaseWatcher.MODIFIED, event.path)

    def process_IN_MOVED_TO(self, event):
        self._process_callback(base_watcher.BaseWatcher.REMOVE, event.path)

    def process_IN_MOVE_SELF(self, event):
        self._process_callback(base_watcher.BaseWatcher.RENAME, event.path)


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        super(NinjaFileSystemWatcher, self).__init__()
        self.watching_paths = {}

    def add_watch(self, path):
        if path not in self.watching_paths:
            wm = WatchManager()
            notifier = ThreadedNotifier(wm,
                        NinjaProcessEvent(self._emit_signal_on_change))
            wm.add_watch(path, mask, rec=True, auto_add=True)
            notifier.start()
            self.watching_paths[path] = notifier

    def remove_watch(self, path):
        if path in self.watching_paths:
            notifier = self.watching_paths[path]
            notifier.stop()
            notifier.join()
            del(self.watching_paths[path])

    def shutdown_notification(self):
        for each_path in self.watching_paths:
            notifier = self.watching_paths[each_path]
            notifier.stop()
            notifier.join()

    def _emit_signal_on_change(self, event, path):
        self.emit(SIGNAL("fileChanged(int, QString)"), event, path)
