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
# GNU General Public License for more details. #
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

from threading import Thread
import win32con
import win32file
import win32event
import pywintypes
import os
from ninja_ide.core import file_manager

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.core.filesystem_notifications.windows')
DEBUG = logger.debug

from ninja_ide.core.filesystem_notifications import base_watcher
ADDED = base_watcher.ADDED
DELETED = base_watcher.DELETED
REMOVE = base_watcher.REMOVE
RENAME = base_watcher.RENAME
MODIFIED = base_watcher.MODIFIED

ACTIONS = {
    1: ADDED,
    2: DELETED,
    3: MODIFIED,
    4: RENAME,
    5: RENAME
}

# Thanks to Claudio Grondi for the correct set of numbers
FILE_LIST_DIRECTORY = 0x0001

watchmask = (win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
             win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
             win32con.FILE_NOTIFY_CHANGE_DIR_NAME)


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
        self._path_last_time = {}
        self.cookie = 0

    def pulentastack(self, path):
        return os.stat(path)

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
                        current[name] = self.pulentastack(os.path.join(path,
                                                                       name))
                    except OSError:
                        pass
            except OSError:
                # recursive delete causes problems with path being non-existent
                pass

            observed = set(current)
            for name, snap_stat in list(snapshot.items()):
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
                if name != path:
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
                    entry[filename] = self.pulentastack(os.path.join(root,
                                                                     filename))
                except OSError:
                    continue
            for directory in dirs:
                refs[os.path.join(root, directory)] = {}

        if os.path.isdir(path):
            refs[os.path.join(root, path)] = {}
            for name in listdir(os.path.join(root, path)):
                try:
                    refs[path][name] = self.pulentastack(os.path.join(path,
                                                                      name))
                except OSError:
                    pass


class ThreadedFSWatcher(Thread):

    def __init__(self, path, callback):
        self._watch_path = path
        self._callback = callback  # FileEventCallback(callback, (path, ))
        self._windows_sucks_flag = True
        self._wait_stop = win32event.CreateEvent(None, 0, 0, None)
        self._overlapped = pywintypes.OVERLAPPED()
        self._overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)
        super(ThreadedFSWatcher, self).__init__()

    def stop(self):
        self._windows_sucks_flag = False
        win32event.SetEvent(self._wait_stop)

    def run(self):
        hDir = win32file.CreateFileW(self._watch_path,
                                     FILE_LIST_DIRECTORY,
                                     win32con.FILE_SHARE_READ |
                                     win32con.FILE_SHARE_WRITE,
                                     None,
                                     win32con.OPEN_EXISTING,
                                     win32con.FILE_FLAG_BACKUP_SEMANTICS |
                                     win32con.FILE_FLAG_OVERLAPPED,
                                     None
                                     )
        while self._windows_sucks_flag:
            buf = win32file.AllocateReadBuffer(1024)
            win32file.ReadDirectoryChangesW(
                hDir,
                buf,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
                self._overlapped
            )
            result_stack = {}
            rc = win32event.WaitForMultipleObjects((self._wait_stop,
                                                    self._overlapped.hEvent),
                                                   0, win32event.INFINITE)
            if rc == win32event.WAIT_OBJECT_0:
                # Stop event
                break

            data = win32file.GetOverlappedResult(hDir, self._overlapped, True)
            # lets read the data and store it in the results
            results = win32file.FILE_NOTIFY_INFORMATION(buf, data)

            for action, afile in results:
                if action in ACTIONS:
                    full_filename = os.path.join(self._watch_path, afile)
                    result_stack.setdefault(full_filename,
                                            []).append(ACTIONS.get(action))
            keys = list(result_stack.keys())
            while len(keys):
                key = keys.pop(0)
                event = result_stack.pop(key)
                if (ADDED in event) and (DELETED in event):
                    event = [e for e in event if e not in (ADDED, DELETED)]
                noticed = []
                for each_event in event:
                    if each_event not in noticed:
                        self._callback(each_event, full_filename)
                        noticed.append(each_event)


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
        base_watcher.BaseWatcher.shutdown_notification(self)
        for each_path in self.watching_paths:
            each_path = self.watching_paths[each_path]
            each_path.stop()
            each_path.join()
