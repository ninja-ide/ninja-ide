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

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject

from ninja_ide import resources
from ninja_ide.gui import actions


class MenuProject(QObject):

    def __init__(self, menuProject, toolbar):
        QObject.__init__(self)

        runAction = menuProject.addAction(QIcon(resources.IMAGES['play']),
            (self.trUtf8("Run Project (%s)") %
                resources.get_shortcut("Run-project").toString(
                    QKeySequence.NativeText)))
#        debugAction = menuProject.addAction(
#            QIcon(resources.IMAGES['debug']),
#            self.trUtf8("Debug Project (%s)" %
#                resources.get_shortcut("Debug").toString(
#                    QKeySequence.NativeText)))
        runFileAction = menuProject.addAction(
            QIcon(resources.IMAGES['file-run']),
            (self.trUtf8("Run File (%s)") %
                resources.get_shortcut("Run-file").toString(
                    QKeySequence.NativeText)))
        stopAction = menuProject.addAction(QIcon(resources.IMAGES['stop']),
            (self.trUtf8("Stop (%s)") %
                resources.get_shortcut("Stop-execution").toString(
                    QKeySequence.NativeText)))
        menuProject.addSeparator()
        projectPropertiesAction = menuProject.addAction(
            self.trUtf8("Open Project Properties"))
        menuProject.addSeparator()
        previewAction = menuProject.addAction(
            QIcon(resources.IMAGES['preview-web']),
            self.trUtf8("Preview Web in Default Browser"))
#        diagramView = menuProject.addAction(self.trUtf8("Diagram View"))

        self.toolbar_items = {
            'run-project': runAction,
            'run-file': runFileAction,
            'stop': stopAction,
            'preview-web': previewAction}

        self.connect(runAction, SIGNAL("triggered()"),
            actions.Actions().execute_project)
        self.connect(runFileAction, SIGNAL("triggered()"),
            actions.Actions().execute_file)
        self.connect(stopAction, SIGNAL("triggered()"),
            actions.Actions().kill_execution)
        self.connect(previewAction, SIGNAL("triggered()"),
            actions.Actions().preview_in_browser)
        self.connect(projectPropertiesAction, SIGNAL("triggered()"),
            actions.Actions().open_project_properties)
#        self.connect(debugAction, SIGNAL("triggered()"),
#            actions.Actions().debug_file)
#        self.connect(diagramView, SIGNAL("triggered()"),
#            actions.Actions().open_class_diagram)
