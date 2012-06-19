# -*- coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtCore import SIGNAL, QThread
from pyinotify import ProcessEvent, IN_CREATE, IN_DELETE, IN_DELETE_SELF, \
                        IN_MODIFY, WatchManager, ThreadedNotifier, Notifier

import logging
logger = logging.getLogger('ninja_ide.core.filesystem_notifications.linux')
DEBUG = logger.debug

from ninja_ide.core.filesystem_notifications import base_watcher

mask = IN_CREATE | IN_DELETE | IN_DELETE_SELF | IN_MODIFY


class NinjaProcessEvent(ProcessEvent):

    def __init__(self, process_callback):
        self._process_callback = process_callback
        ProcessEvent.__init__(self)

    def process_IN_CREATE(self, event):
        self._process_callback((base_watcher.BaseWatcher.ADDED,
                                event.pathname))

    def process_IN_DELETE(self, event):
        self._process_callback((base_watcher.BaseWatcher.DELETED,
                                event.pathname))

    def process_IN_DELETE_SELF(self, event):
        self._process_callback((base_watcher.BaseWatcher.DELETED,
                                event.pathname))

    def process_IN_MODIFY(self, event):
        self._process_callback((base_watcher.BaseWatcher.MODIFIED,
                                event.pathname))

    def process_IN_MOVED_TO(self, event):
        self._process_callback((base_watcher.BaseWatcher.REMOVE,
                                event.pathname))

    def process_IN_MOVE_SELF(self, event):
        self._process_callback((base_watcher.BaseWatcher.RENAME,
                                event.pathname))


class QNotifier(QThread):
    def __init__(self, wm, processor):
        self.event_queue = []
        self._processor = processor
        self.notifier = Notifier(wm, NinjaProcessEvent(self.event_queue.append))
        self.keep_running = True
        QThread.__init__(self)

    def run(self):
        while self.keep_running:
            self.notifier.process_events()
            if self.notifier.check_events():
                self.notifier.read_events()
            for each_event in self.event_queue:
                self._processor(*each_event)
            self.event_queue = []
        self.notifier.stop()


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        super(NinjaFileSystemWatcher, self).__init__()
        self.watching_paths = {}

    def ye_ole_add_watch(self, path):
        if path not in self.watching_paths:
            wm = WatchManager()
            notifier = ThreadedNotifier(wm,
                        NinjaProcessEvent(self._emit_signal_on_change))
            wm.add_watch(path, mask, rec=True, auto_add=True)
            notifier.start()
            self.watching_paths[path] = notifier

    def add_watch(self, path):
        if path not in self.watching_paths:
            wm = WatchManager()
#            ninja_pro = NinjaProcessEvent(self._emit_signal_on_change)
            notifier = QNotifier(wm, self._emit_signal_on_change)
            wm.add_watch(path, mask, rec=True, auto_add=True)
            self.watching_paths[path] = notifier
            notifier.start()

    def remove_watch(self, path):
        if path in self.watching_paths:
            notifier = self.watching_paths.pop(path)
            notifier.keep_running = False
            notifier.quit()

    def shutdown_notification(self):
        for each_path in self.watching_paths:
            notifier = self.watching_paths[each_path]
            notifier.keep_running = False
            notifier.quit()

    def _emit_signal_on_change(self, event, path):
        self.emit(SIGNAL("fileChanged(int, QString)"), event, path)
