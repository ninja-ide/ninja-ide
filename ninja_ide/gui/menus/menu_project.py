# *-* coding: utf-8 *-*
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
            self.tr("Run Project (%1)").arg(
                resources.get_shortcut("Run-project").toString(
                    QKeySequence.NativeText)))
#        debugAction = menuProject.addAction(
#            QIcon(resources.IMAGES['debug']),
#            self.tr("Debug Project (%1)").arg(
#                resources.get_shortcut("Debug").toString(
#                    QKeySequence.NativeText)))
        runFileAction = menuProject.addAction(
            QIcon(resources.IMAGES['file-run']),
            self.tr("Run File (%1)").arg(
                resources.get_shortcut("Run-file").toString(
                    QKeySequence.NativeText)))
        stopAction = menuProject.addAction(QIcon(resources.IMAGES['stop']),
            self.tr("Stop (%1)").arg(
                resources.get_shortcut("Stop-execution").toString(
                    QKeySequence.NativeText)))
        menuProject.addSeparator()
        previewAction = menuProject.addAction(
            QIcon(resources.IMAGES['preview-web']),
            self.tr("Preview Web in Default Browser"))
#        diagramView = menuProject.addAction(self.tr("Diagram View"))

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
#        self.connect(debugAction, SIGNAL("triggered()"),
#            actions.Actions().debug_file)
#        self.connect(diagramView, SIGNAL("triggered()"),
#            actions.Actions().open_class_diagram)
