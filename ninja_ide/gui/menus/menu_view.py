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
from PyQt4.QtGui import QWheelEvent
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import Qt

from ninja_ide import resources


class MenuView(QObject):

    def __init__(self, menuView, toolbar, ide):
        QObject.__init__(self)
        self.__ide = ide

        self.hideConsoleAction = menuView.addAction(
            (self.trUtf8("Show/Hide &Console (%s)") %
                resources.get_shortcut("Hide-misc").toString(
                    QKeySequence.NativeText)))
        self.hideConsoleAction.setCheckable(True)
        self.hideEditorAction = menuView.addAction(
            (self.trUtf8("Show/Hide &Editor (%s)") %
                resources.get_shortcut("Hide-editor").toString(
                    QKeySequence.NativeText)))
        self.hideEditorAction.setCheckable(True)
        self.hideAllAction = menuView.addAction(
            (self.trUtf8("Show/Hide &All (%s)") %
                resources.get_shortcut("Hide-all").toString(
                    QKeySequence.NativeText)))
        self.hideAllAction.setCheckable(True)
        self.hideExplorerAction = menuView.addAction(
            (self.trUtf8("Show/Hide &Explorer (%s)") %
                resources.get_shortcut("Hide-explorer").toString(
                    QKeySequence.NativeText)))
        self.hideExplorerAction.setCheckable(True)
        self.hideToolbarAction = menuView.addAction(
            self.trUtf8("Show/Hide &Toolbar"))
        self.hideToolbarAction.setCheckable(True)
        self.fullscreenAction = menuView.addAction(
            QIcon(resources.IMAGES['fullscreen']),
            (self.trUtf8("Full Screen &Mode (%s)") %
                resources.get_shortcut("Full-screen").toString(
                    QKeySequence.NativeText)))
        menuView.addSeparator()
        splitTabHAction = menuView.addAction(
            QIcon(resources.IMAGES['splitH']),
            (self.trUtf8("Split Tabs Horizontally (%s)") %
                resources.get_shortcut("Split-horizontal").toString(
                    QKeySequence.NativeText)))
        splitTabVAction = menuView.addAction(
            QIcon(resources.IMAGES['splitV']),
            (self.trUtf8("Split Tabs Vertically (%s)") %
                resources.get_shortcut("Split-vertical").toString(
                    QKeySequence.NativeText)))
        followModeAction = menuView.addAction(
            QIcon(resources.IMAGES['follow']),
            (self.trUtf8("Follow Mode (%s)") %
                resources.get_shortcut("Follow-mode").toString(
                    QKeySequence.NativeText)))
        groupTabsAction = menuView.addAction(
            self.trUtf8("Group Tabs by Project"))
        deactivateGroupTabsAction = menuView.addAction(
            self.trUtf8("Deactivate Group Tabs"))
        menuView.addSeparator()
        #Zoom
        zoomInAction = menuView.addAction(QIcon(resources.IMAGES['zoom-in']),
            self.trUtf8("Zoom &In (Ctrl+Wheel-Up)"))
        zoomOutAction = menuView.addAction(QIcon(resources.IMAGES['zoom-out']),
            self.trUtf8("Zoom &Out (Ctrl+Wheel-Down)"))
        menuView.addSeparator()
        fadeInAction = menuView.addAction(
            self.trUtf8("Fade In (Alt+Wheel-Up)"))
        fadeOutAction = menuView.addAction(
            self.trUtf8("Fade Out (Alt+Wheel-Down)"))

        self.toolbar_items = {
            'splitv': splitTabVAction,
            'splith': splitTabHAction,
            'follow-mode': followModeAction,
            'zoom-in': zoomInAction,
            'zoom-out': zoomOutAction}

        self.connect(self.hideConsoleAction, SIGNAL("triggered()"),
            self.__ide.actions.view_misc_visibility)
        self.connect(self.hideEditorAction, SIGNAL("triggered()"),
            self.__ide.actions.view_main_visibility)
        self.connect(self.hideExplorerAction, SIGNAL("triggered()"),
            self.__ide.actions.view_explorer_visibility)
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

        #Set proper MenuView checks values:
        self.hideAllAction.setChecked(True)
        self.hideConsoleAction.setChecked(False)
        self.hideEditorAction.setChecked(True)
        self.hideExplorerAction.setChecked(True)
        self.hideToolbarAction.setChecked(True)

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
