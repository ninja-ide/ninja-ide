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
from ninja_ide.core.file_handling.filesystem_notifications import base_watcher


from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.core.file_handling.filesystem_notifications.darwin')
DEBUG = logger.debug

ADDED = base_watcher.ADDED
DELETED = base_watcher.DELETED
REMOVE = base_watcher.REMOVE
RENAME = base_watcher.RENAME
MODIFIED = base_watcher.MODIFIED


class NinjaFileSystemWatcher(base_watcher.BaseWatcher):

    def __init__(self):
        super(NinjaFileSystemWatcher, self).__init__()
        # self.event_mapping = {
        # fsevents.IN_CREATE: ADDED,
        # fsevents.IN_MODIFY: MODIFIED,
        # fsevents.IN_DELETE: DELETED,
        # fsevents.IN_MOVED_FROM: REMOVE,
        # fsevents.IN_MOVED_TO: ADDED}

    def shutdown_notification(self):
        pass
        # except:

    def add_watch(self, path):
        pass
        # stream = fsevents.Stream(self._emit_signal_on_change,
        # path, file_events=True)

    def remove_watch(self, path):
        pass
        # except:

    def _emit_signal_on_change(self, event):
        pass
