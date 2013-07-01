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

import os

from PyQt4.QtCore import QThread
from pyinotify import ProcessEvent, IN_CREATE, IN_DELETE, IN_DELETE_SELF, \
    IN_MODIFY, WatchManager, Notifier, ExcludeFilter

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.core.filesystem_notifications.linux')
DEBUG = logger.debug

from ninja_ide.core.filesystem_notifications import base_watcher
ADDED = base_watcher.ADDED
DELETED = base_watcher.DELETED
REMOVE = base_watcher.REMOVE
RENAME = base_watcher.RENAME
MODIFIED = base_watcher.MODIFIED
#FIXME: For some reaseon the code below raises an import error with name ADDED
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

    def process_IN_MOVED_FROM(self, event):
        self._process_callback((REMOVE, event.pathname))

    def process_IN_MOVE_SELF(self, event):
        self._process_callback((RENAME, event.pathname))


class QNotifier(QThread):
    def __init__(self, wm, processor):
        self.event_queue = list()
        self._processor = processor
        self.notifier = Notifier(wm, NinjaProcessEvent(
            self.event_queue.append))
        self.notifier.coalesce_events(True)
        self.keep_running = True
        QThread.__init__(self)

    def run(self):
        while self.keep_running:
            try:
                self.notifier.process_events()
            except OSError:
                pass  # OSError: [Errno 2] No such file or directory happens
            e_dict = {}
            while len(self.event_queue):
                e_type, e_path = self.event_queue.pop(0)
                e_dict.setdefault(e_path, []).append(e_type)

            keys = list(e_dict.keys())
            while len(keys):
                key = keys.pop(0)
                event = e_dict.pop(key)
                if (ADDED in event) and (DELETED in event):
                    event = [e for e in event if e not in (ADDED, DELETED)]
                for each_event in event:
                    self._processor(each_event, key)
            if self.notifier.check_events():
                self.notifier.read_events()

        self.notifier.stop()


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        self.watching_paths = {}
        super(NinjaFileSystemWatcher, self).__init__()
        self._ignore_hidden = ('.git', '.hg', '.svn', '.bzr')

    def add_watch(self, path):
        if path not in self.watching_paths:
            try:
                wm = WatchManager()
                notifier = QNotifier(wm, self._emit_signal_on_change)
                notifier.start()
                exclude = ExcludeFilter([os.path.join(path, folder)
                                         for folder in self._ignore_hidden])
                wm.add_watch(path, mask, rec=True, auto_add=True,
                             exclude_filter=exclude)
                self.watching_paths[path] = notifier
            except (OSError, IOError):
                pass
                #Shit happens, most likely temp file

    def remove_watch(self, path):
        if path in self.watching_paths:
            notifier = self.watching_paths.pop(path)
            notifier.keep_running = False
            notifier.quit()

    def shutdown_notification(self):
        base_watcher.BaseWatcher.shutdown_notification(self)
        for each_path in self.watching_paths:
            notifier = self.watching_paths[each_path]
            notifier.keep_running = False
            notifier.quit()
