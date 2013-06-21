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
from __future__ import unicode_literals

import collections

from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QFont
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSizeF
from PyQt4.QtCore import QPointF
from PyQt4.QtNetwork import QLocalServer

from ninja_ide import resources
from ninja_ide.core import plugin_manager
from ninja_ide.core import plugin_services
from ninja_ide.core import settings
from ninja_ide.core import ipc
from ninja_ide.gui import updates
from ninja_ide.gui import actions
from ninja_ide.gui.dialogs import preferences
from ninja_ide.gui.dialogs import traceback_widget
from ninja_ide.tools.completion import completion_daemon
#NINJA-IDE Containers
from ninja_ide.gui import central_widget
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.explorer import explorer_container
from ninja_ide.gui.misc import misc_container

###############################################################################
# LOGGER INITIALIZE
###############################################################################

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.ide')


###############################################################################
# IDE: MAIN CONTAINER
###############################################################################

class IDE(QMainWindow):
###############################################################################
# SIGNALS
#
# goingDown()
###############################################################################

    __IDESERVICES = {}
    __IDECONNECTIONS = {}
    # CONNECTIONS structure:
    # ({'target': service_name, 'signal_name': string,
    #   'slot': 'name_of_function'},)
    # On modify add: {connected: True}
    __created = False

    def __init__(self, start_server=False):
        QMainWindow.__init__(self)
        self.setWindowTitle('NINJA-IDE {Ninja-IDE Is Not Just Another IDE}')
        self.setMinimumSize(700, 500)
        #Load the size and the position of the main window
        self.load_window_geometry()
        self.__project_to_open = 0

        #Start server if needed
        self.s_listener = None
        if start_server:
            self.s_listener = QLocalServer()
            self.s_listener.listen("ninja_ide")
            self.connect(self.s_listener, SIGNAL("newConnection()"),
                self._process_connection)

        #Profile handler
        self.profile = None
        #Opacity
        self.opacity = settings.MAX_OPACITY

        #Define Actions object before the UI
        self.actions = actions.Actions()
        #Main Widget - Create first than everything else
        self.central = central_widget.CentralWidget(self)
        self.load_ui(self.central)
        self.setCentralWidget(self.central)

        #ToolBar
        self.toolbar = QToolBar(self)
        self.toolbar.setToolTip(self.tr("Press and Drag to Move"))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.addToolBar(settings.TOOLBAR_AREA, self.toolbar)
        if settings.HIDE_TOOLBAR:
            self.toolbar.hide()

        #Install Shortcuts after the UI has been initialized
        self.actions.install_shortcuts(self)
        self.connect(self.mainContainer, SIGNAL("currentTabChanged(QString)"),
            self.actions.update_explorer)

        #Plugin Manager
        services = {
            'editor': plugin_services.MainService(),
            'toolbar': plugin_services.ToolbarService(self.toolbar),
            #'menuApp': plugin_services.MenuAppService(self.pluginsMenu),
            'menuApp': plugin_services.MenuAppService(None),
            'explorer': plugin_services.ExplorerService(),
            'misc': plugin_services.MiscContainerService(self.misc)}
        serviceLocator = plugin_manager.ServiceLocator(services)
        self.plugin_manager = plugin_manager.PluginManager(resources.PLUGINS,
            serviceLocator)
        self.plugin_manager.discover()
        #load all plugins!
        self.plugin_manager.load_all()

        #Tray Icon
        self.trayIcon = updates.TrayIconUpdates(self)
        self.trayIcon.show()

        self.connect(self._menuFile, SIGNAL("openFile(QString)"),
            self.mainContainer.open_file)
        self.connect(self.mainContainer,
            SIGNAL("recentTabsModified(QStringList)"),
            self._menuFile.update_recent_files)

        self.register_service(self, 'ide')
        #Actions is temporal
        self.register_service(self.actions, 'actions')
        #Register signals connections
        connections = (
            {'target': 'main_container',
            'signal_name': 'fileSaved(QString)',
            'slot': 'show_status_message'}
            )
        self.register_signals('ide', connections)
        #Actions is temporal
        actions_connections = (
            {'target': 'main_container',
            'signal_name': 'currentTabChanged(QString)',
            'slot': 'update_migration_tips'},
            {'target': 'main_container',
            'signal_name': 'updateFileMetadata(QString)',
            'slot': 'update_migration_tips'},
            {'target': 'main_container',
            'signal_name': 'migrationAnalyzed()',
            'slot': 'update_migration_tips'}
            )
        self.register_signals('actions', actions_connections)
        for service_name in self.__IDECONNECTIONS:
            self.install_service(service_name)

    @classmethod
    def get_service(cls, service_name):
        return IDE.__IDESERVICES.get(service_name, None)

    @classmethod
    def register_service(cls, obj, service_name):
        IDE.__IDESERVICES[service_name] = obj
        if IDE.__created:
            IDE().install_service(service_name)

    def install_service(self, service_name):
        obj = self.__IDESERVICES.get(service_name, None)
        func = getattr(obj, 'install', None)
        if isinstance(func, collections.Callable):
            func(self)
        self._connect_signals()

    @classmethod
    def register_signals(cls, service_name, connections):
        IDE.__IDECONNECTIONS[service_name] = connections

    def _connect_signals(self):
        for service_name in self.__IDECONNECTIONS:
            connections = self.__IDECONNECTIONS[service_name]
            for connection in connections:
                if connection.get('connected', False):
                    continue
                target = self.__IDESERVICES.get(
                    connection['target'], None)
                service = self.__IDESERVICES.get(service_name, None)
                slot = getattr(service, connection['slot'], None)
                signal_name = connection['signal_name']
                if target and isinstance(slot, collections.Callable):
                    self.connect(target, SIGNAL(signal_name), slot)
                    connection['connected'] = True

    def _process_connection(self):
        connection = self.s_listener.nextPendingConnection()
        connection.waitForReadyRead()
        data = connection.readAll()
        connection.close()
        if data:
            files, projects = str(data).split(ipc.project_delimiter, 1)
            files = [(x.split(':')[0], int(x.split(':')[1]))
                for x in files.split(ipc.file_delimiter)]
            projects = projects.split(ipc.project_delimiter)
            self.load_session_files_projects(files, [], projects, None)

    def load_external_plugins(self, paths):
        for path in paths:
            self.plugin_manager.add_plugin_dir(path)
        #load all plugins!
        self.plugin_manager.discover()
        self.plugin_manager.load_all()

    def show_status_message(self, message):
        self.status.showMessage(message, 2000)

    def load_ui(self, centralWidget):
        #Set Application Font for ToolTips
        QToolTip.setFont(QFont(settings.FONT_FAMILY, 10))
        #Create Main Container to manage Tabs
        self.mainContainer = main_container.MainContainer(self)
        self.connect(self.mainContainer, SIGNAL("currentTabChanged(QString)"),
            self.change_window_title)
        self.connect(self.mainContainer,
            SIGNAL("locateFunction(QString, QString, bool)"),
            self.actions.locate_function)
        self.connect(self.mainContainer,
            SIGNAL("navigateCode(bool, int)"),
            self.actions.navigate_code_history)
        self.connect(self.mainContainer,
            SIGNAL("addBackItemNavigation()"),
            self.actions.add_back_item_navigation)
        self.connect(self.mainContainer, SIGNAL("updateFileMetadata()"),
            self.actions.update_explorer)
        self.connect(self.mainContainer, SIGNAL("updateLocator(QString)"),
            self.actions.update_explorer)
        self.connect(self.mainContainer, SIGNAL("openPreferences()"),
            self._show_preferences)
        self.connect(self.mainContainer, SIGNAL("dontOpenStartPage()"),
            self._dont_show_start_page_again)
        # When close the last tab cleanup
        self.connect(self.mainContainer, SIGNAL("allTabsClosed()"),
            self._last_tab_closed)
        #Create Explorer Panel
        self.explorer = explorer_container.ExplorerContainer(self)
        self.connect(self.central, SIGNAL("splitterCentralRotated()"),
            self.explorer.rotate_tab_position)
        self.connect(self.explorer, SIGNAL("goToDefinition(int)"),
            self.actions.editor_go_to_line)
        self.connect(self.explorer, SIGNAL("projectClosed(QString)"),
            self.actions.close_files_from_project)
        #Create Misc Bottom Container
        self.misc = misc_container.MiscContainer(self)
        self.connect(self.mainContainer, SIGNAL("findOcurrences(QString)"),
            self.misc.show_find_occurrences)

        centralWidget.insert_central_container(self.mainContainer)
        centralWidget.insert_lateral_container(self.explorer)
        centralWidget.insert_bottom_container(self.misc)
        if self.explorer.count() == 0:
            centralWidget.change_explorer_visibility(force_hide=True)
        self.connect(self.mainContainer,
            SIGNAL("cursorPositionChange(int, int)"),
            self.central.lateralPanel.update_line_col)
        # TODO: Change current symbol on move
        #self.connect(self.mainContainer,
            #SIGNAL("cursorPositionChange(int, int)"),
            #self.explorer.update_current_symbol)
        self.connect(self.mainContainer, SIGNAL("enabledFollowMode(bool)"),
            self.central.enable_follow_mode_scrollbar)

        if settings.SHOW_START_PAGE:
            self.mainContainer.show_start_page()

    def _last_tab_closed(self):
        """
        Called when the last tasb is closed
        """
        self.explorer.cleanup_tabs()

    def _show_preferences(self):
        pref = preferences.PreferencesWidget(self.mainContainer)
        pref.show()

    def _dont_show_start_page_again(self):
        settings.SHOW_START_PAGE = False
        qsettings = QSettings()
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('general')
        qsettings.setValue('showStartPage', settings.SHOW_START_PAGE)
        qsettings.endGroup()
        qsettings.endGroup()
        self.mainContainer.actualTab.close_tab()

    def load_session_files_projects(self, filesTab1, filesTab2, projects,
        current_file, recent_files=None):
        self.__project_to_open = len(projects)
        self.connect(self.explorer, SIGNAL("projectOpened(QString)"),
            self._set_editors_project_data)
        self.explorer.open_session_projects(projects, notIDEStart=False)
        self.mainContainer.open_files(filesTab1, notIDEStart=False)
        self.mainContainer.open_files(filesTab2, mainTab=False,
            notIDEStart=False)
        if current_file:
            self.mainContainer.open_file(current_file, notStart=False)
        if recent_files is not None:
            self._menuFile.update_recent_files(recent_files)

    def _set_editors_project_data(self):
        self.__project_to_open -= 1
        if self.__project_to_open == 0:
            self.disconnect(self.explorer, SIGNAL("projectOpened(QString)"),
                self._set_editors_project_data)
            self.mainContainer.update_editor_project()

    def open_file(self, filename):
        if filename:
            self.mainContainer.open_file(filename)

    def open_project(self, project):
        if project:
            self.actions.open_project(project)

    def __get_profile(self):
        return self.profile

    def __set_profile(self, profileName):
        self.profile = profileName
        if self.profile is not None:
            self.setWindowTitle('NINJA-IDE (PROFILE: %s)' % self.profile)
        else:
            self.setWindowTitle(
                'NINJA-IDE {Ninja-IDE Is Not Just Another IDE}')

    Profile = property(__get_profile, __set_profile)

    def change_window_title(self, title):
        if self.profile is None:
            self.setWindowTitle('NINJA-IDE - %s' % title)
        else:
            self.setWindowTitle('NINJA-IDE (PROFILE: %s) - %s' % (
                self.profile, title))
        currentEditor = self.mainContainer.get_actual_editor()
        if currentEditor is not None:
            line = currentEditor.textCursor().blockNumber() + 1
            col = currentEditor.textCursor().columnNumber()
            self.central.lateralPanel.update_line_col(line, col)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            if event.delta() == 120 and self.opacity < settings.MAX_OPACITY:
                self.opacity += 0.1
            elif event.delta() == -120 and self.opacity > settings.MIN_OPACITY:
                self.opacity -= 0.1
            self.setWindowOpacity(self.opacity)
            event.ignore()
        else:
            QMainWindow.wheelEvent(self, event)

    def save_settings(self):
        """Save the settings before the application is closed with QSettings.

        Info saved: Tabs and projects opened, windows state(size and position).
        """
        qsettings = QSettings()
        editor_widget = self.mainContainer.get_actual_editor()
        current_file = ''
        if editor_widget is not None:
            current_file = editor_widget.ID
        if qsettings.value('preferences/general/loadFiles', True, type=bool):
            openedFiles = self.mainContainer.get_opened_documents()
            projects_obj = self.explorer.get_opened_projects()
            projects = [p.path for p in projects_obj]
            qsettings.setValue('openFiles/projects',
                projects)
            if len(openedFiles) > 0:
                qsettings.setValue('openFiles/mainTab', openedFiles[0])
            if len(openedFiles) == 2:
                qsettings.setValue('openFiles/secondaryTab', openedFiles[1])
            qsettings.setValue('openFiles/currentFile', current_file)
            qsettings.setValue('openFiles/recentFiles',
                self.mainContainer._tabMain.get_recent_files_list())
        qsettings.setValue('preferences/editor/bookmarks', settings.BOOKMARKS)
        qsettings.setValue('preferences/editor/breakpoints',
            settings.BREAKPOINTS)
        qsettings.setValue('preferences/general/toolbarArea',
            self.toolBarArea(self.toolbar))
        #Save if the windows state is maximixed
        if(self.isMaximized()):
            qsettings.setValue("window/maximized", True)
        else:
            qsettings.setValue("window/maximized", False)
            #Save the size and position of the mainwindow
            qsettings.setValue("window/size", self.size())
            qsettings.setValue("window/pos", self.pos())
        #Save the size of de splitters
        qsettings.setValue("window/central/areaSize",
            self.central.get_area_sizes())
        qsettings.setValue("window/central/mainSize",
            self.central.get_main_sizes())
        #Save the toolbar visibility
        if not self.toolbar.isVisible() and self.menuBar().isVisible():
            qsettings.setValue("window/hide_toolbar", True)
        else:
            qsettings.setValue("window/hide_toolbar", False)
        #Save Misc state
        qsettings.setValue("window/show_misc", self.misc.isVisible())
        #Save Profiles
        if self.profile is not None:
            self.actions.save_profile(self.profile)
        else:
            qsettings.setValue('ide/profiles', settings.PROFILES)

    def load_window_geometry(self):
        """Load from QSettings the window size of de Ninja IDE"""
        qsettings = QSettings()
        if qsettings.value("window/maximized", True, type=bool):
            self.setWindowState(Qt.WindowMaximized)
        else:
            self.resize(qsettings.value("window/size",
                QSizeF(800, 600).toSize(), type='QSize'))
            self.move(qsettings.value("window/pos",
                QPointF(100, 100).toPoint(), type='QPoint'))

    def closeEvent(self, event):
        if self.s_listener:
            self.s_listener.close()
        if (settings.CONFIRM_EXIT and
                self.mainContainer.check_for_unsaved_tabs()):
            unsaved_files = self.mainContainer.get_unsaved_files()
            txt = '\n'.join(unsaved_files)
            val = QMessageBox.question(self,
                self.tr("Some changes were not saved"),
                (self.tr("%s\n\nDo you want to save them?") % txt),
                QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
            if val == QMessageBox.Yes:
                #Saves all open files
                self.mainContainer.save_all()
            if val == QMessageBox.Cancel:
                event.ignore()
        self.emit(SIGNAL("goingDown()"))
        self.save_settings()
        completion_daemon.shutdown_daemon()
        #close python documentation server (if running)
        self.mainContainer.close_python_doc()
        #Shutdown PluginManager
        self.plugin_manager.shutdown()

    def notify_plugin_errors(self):
        errors = self.plugin_manager.errors
        if errors:
            plugin_error_dialog = traceback_widget.PluginErrorDialog()
            for err_tuple in errors:
                plugin_error_dialog.add_traceback(err_tuple[0], err_tuple[1])
            #show the dialog
            plugin_error_dialog.exec_()
