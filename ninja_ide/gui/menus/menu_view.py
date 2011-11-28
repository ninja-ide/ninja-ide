from __future__ import absolute_import

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QWheelEvent
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide.core import settings


class MenuView(QObject):

    def __init__(self, menuView, toolbar, ide):
        QObject.__init__(self)
        self.__ide = ide

        self.hideConsoleAction = menuView.addAction(
            self.tr("Show/Hide &Console (%1)").arg(
                resources.get_shortcut("Hide-misc").toString(
                    QKeySequence.NativeText)))
        self.hideEditorAction = menuView.addAction(
            self.tr("Show/Hide &Editor (%1)").arg(
                resources.get_shortcut("Hide-editor").toString(
                    QKeySequence.NativeText)))
        self.hideAllAction = menuView.addAction(
            self.tr("Show/Hide &All (%1)").arg(
                resources.get_shortcut("Hide-all").toString(
                    QKeySequence.NativeText)))
        self.hideExplorerAction = menuView.addAction(
            self.tr("Show/Hide &Explorer (%1)").arg(
                resources.get_shortcut("Hide-explorer").toString(
                    QKeySequence.NativeText)))
        self.hideToolbarAction = menuView.addAction(
            self.tr("Show/Hide &Toolbar"))
        self.fullscreenAction = menuView.addAction(
            QIcon(resources.IMAGES['fullscreen']),
            self.tr("Full Screen &Mode (%1)").arg(
                resources.get_shortcut("Full-screen").toString(
                    QKeySequence.NativeText)))
        menuView.addSeparator()
        splitTabHAction = menuView.addAction(
            QIcon(resources.IMAGES['splitH']),
            self.tr("Split Tabs Horizontally (%1)").arg(
                resources.get_shortcut("Split-horizontal").toString(
                    QKeySequence.NativeText)))
        splitTabVAction = menuView.addAction(
            QIcon(resources.IMAGES['splitV']),
            self.tr("Split Tabs Vertically (%1)").arg(
                resources.get_shortcut("Split-vertical").toString(
                    QKeySequence.NativeText)))
        followModeAction = menuView.addAction(
            QIcon(resources.IMAGES['follow']),
            self.tr("Follow Mode (%1)").arg(
                resources.get_shortcut("Follow-mode").toString(
                    QKeySequence.NativeText)))
        groupTabsAction = menuView.addAction(self.tr("Group Tabs by Project"))
        deactivateGroupTabsAction = menuView.addAction(
            self.tr("Deactivate Group Tabs"))
        menuView.addSeparator()
        #Zoom
        zoomInAction = menuView.addAction(QIcon(resources.IMAGES['zoom-in']),
            self.tr("Zoom &In (%1+Wheel-Up)").arg(settings.OS_KEY))
        zoomOutAction = menuView.addAction(QIcon(resources.IMAGES['zoom-out']),
            self.tr("Zoom &Out (%1+Wheel-Down)").arg(settings.OS_KEY))
        menuView.addSeparator()
        fadeInAction = menuView.addAction(self.tr("Fade In (Alt+Wheel-Up)"))
        fadeOutAction = menuView.addAction(
            self.tr("Fade Out (Alt+Wheel-Down)"))

        self.toolbar_items = {
            'splith': splitTabHAction,
            'splitv': splitTabVAction,
            'follow-mode': followModeAction,
            'zoom-in': zoomInAction,
            'zoom-out': zoomOutAction}

        self.connect(self.hideConsoleAction, SIGNAL("triggered()"),
            self.__ide.central.change_misc_visibility)
        self.connect(self.hideEditorAction, SIGNAL("triggered()"),
            self.__ide.central.change_main_visibility)
        self.connect(self.hideExplorerAction, SIGNAL("triggered()"),
            self.__ide.central.change_explorer_visibility)
        self.connect(self.hideAllAction, SIGNAL("triggered()"),
            self.__ide.actions.hide_all)
        self.connect(self.fullscreenAction, SIGNAL("triggered()"),
            self.__ide.actions.fullscreen_mode)
        self.connect(splitTabHAction, SIGNAL("triggered()"),
            lambda: self.__ide.mainContainer.split_tab(True))
        self.connect(splitTabVAction, SIGNAL("triggered()"),
            lambda: self.__ide.mainContainer.split_tab(False))
        QObject.connect(followModeAction, SIGNAL("triggered()"),
            self.__ide.mainContainer.show_follow_mode)
        self.connect(zoomInAction, SIGNAL("triggered()"),
            self.zoom_in_editor)
        self.connect(zoomOutAction, SIGNAL("triggered()"),
            self.zoom_out_editor)
        self.connect(fadeInAction, SIGNAL("triggered()"), self._fade_in)
        self.connect(fadeOutAction, SIGNAL("triggered()"), self._fade_out)
        self.connect(self.hideToolbarAction, SIGNAL("triggered()"),
            self._hide_show_toolbar)
        self.connect(groupTabsAction, SIGNAL("triggered()"),
            self.__ide.actions.group_tabs_together)
        self.connect(deactivateGroupTabsAction, SIGNAL("triggered()"),
            self.__ide.actions.deactivate_tabs_groups)

    def _hide_show_toolbar(self):
        if self.__ide.toolbar.isVisible():
            self.__ide.toolbar.hide()
        else:
            self.__ide.toolbar.show()

    def zoom_in_editor(self):
        editor = self.__ide.mainContainer.get_actual_editor()
        if editor:
            editor.zoom_in()

    def zoom_out_editor(self):
        editor = self.__ide.mainContainer.get_actual_editor()
        if editor:
            editor.zoom_out()

    def _fade_in(self):
        event = QWheelEvent(QPoint(), 120, Qt.NoButton, Qt.AltModifier)
        self.__ide.wheelEvent(event)

    def _fade_out(self):
        event = QWheelEvent(QPoint(), -120, Qt.NoButton, Qt.AltModifier)
        self.__ide.wheelEvent(event)
