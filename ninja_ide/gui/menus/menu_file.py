# *-* coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QStyle
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources


class MenuFile(QObject):

    def __init__(self, menuFile, toolbar, ide):
        QObject.__init__(self)

        newAction = menuFile.addAction(QIcon(resources.IMAGES['new']),
            self.tr("&New File (%1)").arg(
                resources.get_shortcut("New-file").toString(
                    QKeySequence.NativeText)))
#        newAction.setShortcut(resources.get_shortcut("New-file"))
        newProjectAction = menuFile.addAction(
            QIcon(resources.IMAGES['newProj']),
            self.tr("New Pro&ject (%1)").arg(
                resources.get_shortcut("New-project").toString(
                    QKeySequence.NativeText)))
        menuFile.addSeparator()
        saveAction = menuFile.addAction(QIcon(resources.IMAGES['save']),
            self.tr("&Save (%1)").arg(
                resources.get_shortcut("Save-file").toString(
                    QKeySequence.NativeText)))
        saveAsAction = menuFile.addAction(QIcon(resources.IMAGES['saveAs']),
            self.tr("Save &As"))
        saveAllAction = menuFile.addAction(QIcon(resources.IMAGES['saveAll']),
            self.tr("Save All"))
        saveProjectAction = menuFile.addAction(QIcon(
            resources.IMAGES['saveAll']),
            self.tr("Save Pro&ject  (%1)").arg(
                resources.get_shortcut("Save-project").toString(
                    QKeySequence.NativeText)))
        saveProfileAction = menuFile.addAction(
            self.tr("Save Profile (Group together the opened projects)"))
        menuFile.addSeparator()
        reloadFileAction = menuFile.addAction(
            QIcon(resources.IMAGES['reload-file']),
            self.tr("Reload File (%1)").arg(
                resources.get_shortcut("Reload-file").toString(
                    QKeySequence.NativeText)))
        menuFile.addSeparator()
        openAction = menuFile.addAction(QIcon(resources.IMAGES['open']),
            self.tr("&Open (%1)").arg(
                resources.get_shortcut("Open-file").toString(
                    QKeySequence.NativeText)))
        openProjectAction = menuFile.addAction(
            QIcon(resources.IMAGES['openProj']),
            self.tr("Open &Project (%1)").arg(
                resources.get_shortcut("Open-project").toString(
                    QKeySequence.NativeText)))
        openProjectTypeAction = menuFile.addAction(
            QIcon(resources.IMAGES['openProj']), self.tr("Open Project &Type"))
        openProfileAction = menuFile.addAction(self.tr("Open Profile"))
        menuFile.addSeparator()
        printFile = menuFile.addAction(QIcon(resources.IMAGES['print']),
            self.tr("Pr&int File (%1)").arg(
                resources.get_shortcut("Print-file").toString(
                    QKeySequence.NativeText)))
        closeAction = menuFile.addAction(
            ide.style().standardIcon(QStyle.SP_DialogCloseButton),
            self.tr("&Close Tab (%1)").arg(
                resources.get_shortcut("Close-tab").toString(
                    QKeySequence.NativeText)))
        closeProjectsAction = menuFile.addAction(
            ide.style().standardIcon(QStyle.SP_DialogCloseButton),
            self.tr("&Close All Projects"))
        menuFile.addSeparator()
        exitAction = menuFile.addAction(
            ide.style().standardIcon(QStyle.SP_DialogCloseButton),
            self.tr("&Exit"))

        toolbar.addAction(newAction)
        toolbar.addAction(newProjectAction)
        toolbar.addAction(openAction)
        toolbar.addAction(openProjectAction)
        toolbar.addAction(saveAction)
        toolbar.addSeparator()

        self.connect(newAction, SIGNAL("triggered()"),
            ide.mainContainer.add_editor)
        self.connect(newProjectAction, SIGNAL("triggered()"),
            ide.explorer.create_new_project)
        self.connect(openAction, SIGNAL("triggered()"),
            ide.mainContainer.open_file)
        self.connect(saveAction, SIGNAL("triggered()"),
            ide.mainContainer.save_file)
        self.connect(saveAsAction, SIGNAL("triggered()"),
            ide.mainContainer.save_file_as)
        self.connect(saveAllAction, SIGNAL("triggered()"),
            ide.actions.save_all)
        self.connect(saveProjectAction, SIGNAL("triggered()"),
            ide.actions.save_project)
        self.connect(openProjectAction, SIGNAL("triggered()"),
            ide.explorer.open_project_folder)
        self.connect(openProjectTypeAction, SIGNAL("triggered()"),
            self._open_project_type)
        self.connect(closeAction, SIGNAL("triggered()"),
            ide.mainContainer.actualTab.close_tab)
        self.connect(exitAction, SIGNAL("triggered()"),
            ide.close)
        QObject.connect(reloadFileAction, SIGNAL("triggered()"),
            ide.mainContainer.reload_file)
        self.connect(printFile, SIGNAL("triggered()"), ide.actions.print_file)
        self.connect(saveProfileAction, SIGNAL("triggered()"),
            ide.actions.save_profile)
        self.connect(openProfileAction, SIGNAL("triggered()"),
            ide.actions.open_profile)
        self.connect(closeProjectsAction, SIGNAL("triggered()"),
            ide.explorer.close_opened_projects)

    def _open_project_type(self):
        pass
