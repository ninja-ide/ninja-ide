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

from PyQt4.QtCore import SIGNAL
from threading import Thread
import win32con
import win32file
import win32event
import os
from ninja_ide.core import file_manager

import logging
logger = logging.getLogger('ninja_ide.core.filesystem_notifications.windows')
DEBUG = logger.debug

from ninja_ide.core.filesystem_notifications import base_watcher
ADDED = base_watcher.ADDED
DELETED = base_watcher.DELETED
REMOVE = base_watcher.REMOVE
RENAME = base_watcher.RENAME
MODIFIED = base_watcher.MODIFIED

watchmask = win32con.FILE_NOTIFY_CHANGE_FILE_NAME | \
            win32con.FILE_NOTIFY_CHANGE_SIZE | \
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME


def listdir(path):
    fdict = file_manager.open_project(path)
    for each_folder in fdict:
        files, folders = fdict[each_folder]
        yield each_folder
        for each_file in files:
            yield os.path.join(each_folder, each_file)

#Credit on this workaround for the shortsightness of windows developers goes
#to Malthe Borch http://pypi.python.org/pypi/MacFSEvents


class FileEventCallback(object):
    def __init__(self, callback, paths):
        self.snapshots = {}
        for path in paths:
            self.snapshot(path)
        self.callback = callback
        self.cookie = 0

    def __call__(self, paths):
        events = []
        deleted = {}

        for path in sorted(paths):
            path = path.rstrip('/')
            snapshot = self.snapshots[path]

            current = {}
            try:
                for name in listdir(path):
                    try:
                        current[name] = os.stat(os.path.join(path, name))
                    except OSError:
                        pass
            except OSError:
                # recursive delete causes problems with path being non-existent
                pass

            observed = set(current)
            for name, snap_stat in snapshot.items():
                filename = os.path.join(path, name)
                if name in observed:

                    stat = current[name]
                    if stat.st_mtime > snap_stat.st_mtime:
                        events.append((MODIFIED, filename))
                    observed.discard(name)
                else:
                    event = (DELETED, filename)
                    deleted[snap_stat.st_ino] = event
                    events.append(event)

            for name in observed:
                stat = current[name]
                filename = os.path.join(path, name)

                event = deleted.get(stat.st_ino)
                if event is not None:
                    event = (REMOVE, filename)
                else:
                    event = (ADDED, filename)

                if os.path.isdir(filename):
                    self.snapshot(filename)

                events.append(event)
            snapshot.clear()
            snapshot.update(current)

        for event in events:
            self.callback(*event)

    def snapshot(self, path):
        path = os.path.realpath(path)
        refs = self.snapshots
        refs[path] = {}

        for root, dirs, files in os.walk(path):
            entry = refs[root]
            for filename in files:
                try:
                    entry[filename] = os.stat(os.path.join(root, filename))
                except OSError:
                    continue
            for directory in dirs:
                refs[os.path.join(root, directory)] = {}

        if os.path.isdir(path):
            refs[os.path.join(root, path)] = {}
            for name in listdir(os.path.join(root, path)):
                try:
                    refs[path][name] = os.stat(os.path.join(path, name))
                except OSError:
                    pass


class ThreadedFSWatcher(Thread):

    def __init__(self, path, callback):
        self._watch_path = path
        self._callback = FileEventCallback(callback, (path, ))
        self._windows_sucks_flag = True
        super(ThreadedFSWatcher, self).__init__()

    def stop(self):
        self._windows_sucks_flag = False

    def run(self):
        change_handle = win32file.FindFirstChangeNotification(self._watch_path,
                                                              True, watchmask)
        while self._windows_sucks_flag:
            result = win32event.WaitForSingleObject(change_handle, 500)
            if result == win32con.WAIT_OBJECT_0:
                self._callback((self._watch_path, ))


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        super(NinjaFileSystemWatcher, self).__init__()
        # do stuff
        self.watching_paths = {}

    def add_watch(self, path):
        if path not in self.watching_paths:
            watch = ThreadedFSWatcher(path, self._emit_signal_on_change)
            watch.start()
            self.watching_paths[path] = watch
            # Add real watcher using platform specific things

    def remove_watch(self, path):
        if path in self.watching_paths:
            self.watching_paths[path].stop()
            self.watching_paths[path].join()
            del(self.watching_paths[path])
            # Remove real watcher using platform specific things

    def shutdown_notification(self):
        for each_path in self.watching_paths:
            each_path = self.watching_paths[each_path]
            each_path.stop()
            each_path.join()

    def _emit_signal_on_change(self, event, path):
        self.emit(SIGNAL("fileChanged(int, QString)"), event, path)
