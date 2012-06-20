# -*- coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtCore import SIGNAL, QThread
from pyinotify import ProcessEvent, IN_CREATE, IN_DELETE, IN_DELETE_SELF, \
                        IN_MODIFY, WatchManager, Notifier

import logging
logger = logging.getLogger('ninja_ide.core.filesystem_notifications.linux')
DEBUG = logger.debug

from ninja_ide.core.filesystem_notifications import base_watcher
ADDED = base_watcher.ADDED
DELETED = base_watcher.DELETED
REMOVE = base_watcher.REMOVE
RENAME = base_watcher.RENAME
MODIFIED = base_watcher.MODIFIED
#from ninja_ide.core.filesystem_notifications.base_watcher import ADDED, \
#                                            DELETED, REMOVE, RENAME, MODIFIED

mask = IN_CREATE | IN_DELETE | IN_DELETE_SELF | IN_MODIFY


class NinjaProcessEvent(ProcessEvent):

    def __init__(self, process_callback):
        self._process_callback = process_callback
        ProcessEvent.__init__(self)

    def process_IN_CREATE(self, event):
        self._process_callback((ADDED, event.pathname))

    def process_IN_DELETE(self, event):
        self._process_callback((DELETED, event.pathname))

    def process_IN_DELETE_SELF(self, event):
        self._process_callback((DELETED, event.pathname))

    def process_IN_MODIFY(self, event):
        self._process_callback((MODIFIED, event.pathname))

    def process_IN_MOVED_TO(self, event):
        self._process_callback((REMOVE, event.pathname))

    def process_IN_MOVE_SELF(self, event):
        self._process_callback((RENAME, event.pathname))


class QNotifier(QThread):
    def __init__(self, wm, processor):
        self.event_queue = list()
        self._processor = processor
        self.notifier = Notifier(wm, NinjaProcessEvent(self.event_queue.append))
        self.keep_running = True
        QThread.__init__(self)

    def run(self):
        while self.keep_running:
            self.notifier.process_events()
            if self.notifier.check_events():
                self.notifier.read_events()
            e_dict = {}
            while len(self.event_queue):
                e_type, e_path = self.event_queue.pop(0)
                e_dict.setdefault(e_path, []).append(e_type)

            keys = e_dict.keys()
            while len(keys):
                key = keys.pop(0)
                event = e_dict.pop(key)
                if (ADDED in event) and (DELETED in event):
                    event = [e for e in event if e not in (ADDED, DELETED)]
#                if (ADDED in event) and (MODIFIED in event):
#                    event = [e for e in event if e != ADDED]
                for each_event in event:
                    self._processor(each_event, key)
        self.notifier.stop()


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        super(NinjaFileSystemWatcher, self).__init__()
        self.watching_paths = {}

    def add_watch(self, path):
        if path not in self.watching_paths:
            wm = WatchManager()
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
