# -*- coding: utf-8 *-*
from PyQt4.QtCore import QObject


class BaseWatcher(QObject):

###############################################################################
# SIGNALS
#
# fileChanged(int, QString)  [added, deleted, modified, rename, remove]
###############################################################################

    ADDED = 1
    MODIFIED = 2
    DELETED = 3
    RENAME = 4
    REMOVE = 5

    def __init__(self):
        super(BaseWatcher, self).__init__()
