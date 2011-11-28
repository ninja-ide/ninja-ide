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
        menuFile.addSeparator()
        activateProfileAction = menuFile.addAction(
            QIcon(resources.IMAGES['activate-profile']),
            self.tr("Activate Profile"))
        deactivateProfileAction = menuFile.addAction(
            QIcon(resources.IMAGES['deactivate-profile']),
            self.tr("Deactivate Profile"))
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

        self.toolbar_items = {
            'new-file': newAction,
            'new-project': newProjectAction,
            'save-file': saveAction,
            'save-as': saveAsAction,
            'save-all': saveAllAction,
            'save-project': saveProjectAction,
            'reload-file': reloadFileAction,
            'open-file': openAction,
            'open-project': openProjectAction,
            'activate-profile': activateProfileAction,
            'deactivate-profile': deactivateProfileAction,
            'print-file': printFile,
            'close-file': closeAction,
            'close-projects': closeProjectsAction}

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
        self.connect(closeProjectsAction, SIGNAL("triggered()"),
            ide.explorer.close_opened_projects)
        self.connect(deactivateProfileAction, SIGNAL("triggered()"),
            ide.actions.deactivate_profile)
        self.connect(activateProfileAction, SIGNAL("triggered()"),
            ide.actions.activate_profile)

    def _open_project_type(self):
        pass
