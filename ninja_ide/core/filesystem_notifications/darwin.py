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

from ninja_ide.core.filesystem_notifications import base_watcher


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        super(NinjaFileSystemWatcher, self).__init__()
        # do stuff
        self.watching_paths = []

    def shutdown_notification(self):
        base_watcher.BaseWatcher.shutdown_notification(self)

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
