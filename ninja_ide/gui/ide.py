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

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QShortcut
from PyQt4.QtGui import QInputDialog
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSizeF
from PyQt4.QtCore import QPointF
from PyQt4.QtNetwork import QLocalServer

from ninja_ide import resources
from ninja_ide.core import plugin_manager
#from ninja_ide.core import plugin_services
from ninja_ide.core import settings
from ninja_ide.core import ipc
from ninja_ide.gui import updates
from ninja_ide.gui.dialogs import preferences
from ninja_ide.gui.dialogs import traceback_widget
from ninja_ide.tools.completion import completion_daemon
from ninja_ide.tools import ui_tools

###############################################################################
# LOGGER INITIALIZE
###############################################################################

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.ide')


###############################################################################
# IDE: MAIN CONTAINER
###############################################################################

class IDE(QMainWindow):
    """This class is like the Sauron's Ring:
    One ring to rule them all, One ring to find them,
    One ring to bring them all and in the darkness bind them.

    This Class knows all the containers, and its know by all the containers,
    but the containers don't need to know between each other, in this way we
    can keep a better api without the need to tie the behaviour between
    the widgets, and let them just consume the 'actions' they need."""

###############################################################################
# SIGNALS
#
# goingDown()
###############################################################################

    __IDESERVICES = {}
    __IDECONNECTIONS = {}
    __IDESHORTCUTS = {}
    # CONNECTIONS structure:
    # ({'target': service_name, 'signal_name': string, 'slot': function_obj},)
    # On modify add: {connected: True}
    __instance = None
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

        #ToolBar
        self.toolbar = QToolBar(self)
        self.toolbar.setToolTip(self.tr("Press and Drag to Move"))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.addToolBar(settings.TOOLBAR_AREA, self.toolbar)
        if settings.HIDE_TOOLBAR:
            self.toolbar.hide()

        #Plugin Manager
        #services = {
            #'editor': plugin_services.MainService(),
            #'toolbar': plugin_services.ToolbarService(self.toolbar),
            ##'menuApp': plugin_services.MenuAppService(self.pluginsMenu),
            #'menuApp': plugin_services.MenuAppService(None),
            #'explorer': plugin_services.ExplorerService(),
            #'misc': plugin_services.MiscContainerService(self.misc)}
        #serviceLocator = plugin_manager.ServiceLocator(services)
        serviceLocator = plugin_manager.ServiceLocator(None)
        self.plugin_manager = plugin_manager.PluginManager(resources.PLUGINS,
            serviceLocator)
        self.plugin_manager.discover()
        #load all plugins!
        self.plugin_manager.load_all()

        #Tray Icon
        self.trayIcon = updates.TrayIconUpdates(self)
        self.trayIcon.show()

        #Shortcuts
        shortFullscreen = QShortcut(
            resources.get_shortcut("Full-screen"), self)
        IDE.register_shortcut('Full-screen', shortFullscreen)
        self.connect(shortFullscreen, SIGNAL("activated()"),
            self.fullscreen_mode)

        key = Qt.Key_1
        for i in range(10):
            if settings.IS_MAC_OS:
                short = TabShortcuts(
                    QKeySequence(Qt.CTRL + Qt.ALT + key), self, i)
            else:
                short = TabShortcuts(QKeySequence(Qt.ALT + key), self, i)
            key += 1
            self.connect(short, SIGNAL("activated()"), self._change_tab_index)
        short = TabShortcuts(QKeySequence(Qt.ALT + Qt.Key_0), self, 10)
        self.connect(short, SIGNAL("activated()"), self._change_tab_index)

        short = resources.get_shortcut
        shortFullscreen = QShortcut(short("Full-screen"), self)
        shortSwitchFocus = QShortcut(short("Switch-Focus"), self)
        IDE.register_shortcut('Full-screen', shortFullscreen)
        IDE.register_shortcut('Switch-Focus', shortSwitchFocus)
        self.connect(shortFullscreen, SIGNAL("activated()"),
            self.fullscreen_mode)
        self.connect(shortSwitchFocus, SIGNAL("activated()"),
            self.fullscreen_mode)

        self.register_service('ide', self)
        self.register_service('toolbar', self.toolbar)
        #Register signals connections
        connections = (
            {'target': 'main_container',
            'signal_name': 'fileSaved(QString)',
            'slot': self.show_status_message},
            {'target': 'main_container',
            'signal_name': 'currentTabChanged(QString)',
            'slot': self.change_window_title},
            {'target': 'main_container',
            'signal_name': 'openPreferences()',
            'slot': self._show_preferences},
            {'target': 'main_container',
            'signal_name': 'allTabsClosed()',
            'slot': self._last_tab_closed},
            {'target': 'explorer_container',
            'signal_name': 'changeWindowTitle(QString)',
            'slot': self.change_window_title},
            )
        self.register_signals('ide', connections)
        # Central Widget MUST always exists
        self.central = IDE.get_service('central_container')
        self.setCentralWidget(self.central)
        # Install Services
        for service_name in self.__IDESERVICES:
            self.install_service(service_name)
        QToolTip.setFont(QFont(settings.FONT_FAMILY, 10))
        self.__created = True

    @classmethod
    def get_service(cls, service_name):
        return IDE.__IDESERVICES.get(service_name, None)

    @classmethod
    def register_service(cls, service_name, obj):
        IDE.__IDESERVICES[service_name] = obj
        if IDE.__created:
            IDE.__instance.install_service(service_name)

    def install_service(self, service_name):
        obj = self.__IDESERVICES.get(service_name, None)
        func = getattr(obj, 'install', None)
        if isinstance(func, collections.Callable):
            func(self)
        self._connect_signals()

    def place_me_on(self, region=None):
        pass

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
                slot = connection['slot']
                signal_name = connection['signal_name']
                if target and isinstance(slot, collections.Callable):
                    self.connect(target, SIGNAL(signal_name), slot)
                    connection['connected'] = True

    @classmethod
    def register_shortcut(cls, shortcut_name, obj):
        IDE.__IDESHORTCUTS[shortcut_name] = obj

    @classmethod
    def update_shortcut(cls, shortcut_name):
        short = resources.get_shortcut
        shortcut = IDE.__IDESHORTCUTS.get(shortcut_name)
        if shortcut:
            shortcut.setKey(short(shortcut_name))

    def _change_tab_index(self):
        widget = QApplication.focusWidget()
        shortcut_index = getattr(widget, 'shortcut_index', None)
        if shortcut_index:
            obj = self.sender()
            shortcut_index(obj.index)

    def switch_focus(self):
        widget = QApplication.focusWidget()
        main_container = IDE.get_service('main_container')
        tools_dock = IDE.get_service('tools_dock')
        explorer_container = IDE.get_service('explorer_container')
        if widget and main_container and tools_dock and explorer_container:
            if widget in (main_container.actualTab,
               main_container.actualTab.currentWidget()):
                explorer_container.currentWidget().setFocus()
            elif widget in (explorer_container,
                 explorer_container.currentWidget()):
                if tools_dock.isVisible():
                    tools_dock.stack.currentWidget().setFocus()
                else:
                    main_container.actualTab.currentWidget().setFocus()
            elif widget.parent() is tools_dock.stack:
                main_container.actualTab.currentWidget().setFocus()

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

    def fullscreen_mode(self):
        """Change to fullscreen mode."""
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def load_external_plugins(self, paths):
        for path in paths:
            self.plugin_manager.add_plugin_dir(path)
        #load all plugins!
        self.plugin_manager.discover()
        self.plugin_manager.load_all()

    def show_status_message(self, message):
        self.status.showMessage(message, 2000)

    def _last_tab_closed(self):
        """
        Called when the last tasb is closed
        """
        self.explorer.cleanup_tabs()

    def _show_preferences(self):
        pref = preferences.PreferencesWidget(self.mainContainer)
        pref.set_IDE(self)
        pref.show()

    def load_session_files_projects(self, filesTab1, filesTab2, projects,
        current_file, recent_files=None):
        self.__project_to_open = len(projects)
        explorer = IDE.get_service('explorer_container')
        main_container = IDE.get_service('main_container')
        if explorer and main_container:
            self.connect(explorer, SIGNAL("projectOpened(QString)"),
                self._set_editors_project_data)
            explorer.open_session_projects(projects, notIDEStart=False)
            main_container.open_files(filesTab1, notIDEStart=False)
            main_container.open_files(filesTab2, mainTab=False,
                notIDEStart=False)
            if current_file:
                main_container.open_file(current_file, notStart=False)
            if recent_files is not None:
                menu_file = IDE.get_service('menu_file')
                menu_file.update_recent_files(recent_files)

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
        qsettings.setValue("window/central/baseSize",
            self.central.get_area_sizes())
        qsettings.setValue("window/central/insideSize",
            self.central.get_main_sizes())
        #Save the toolbar visibility
        if not self.toolbar.isVisible() and self.menuBar().isVisible():
            qsettings.setValue("window/hide_toolbar", True)
        else:
            qsettings.setValue("window/hide_toolbar", False)
        #Save Misc state
        qsettings.setValue("window/show_region1", self.misc.isVisible())
        #Save Profiles
        if self.profile is not None:
            self.actions.save_profile(self.profile)
        else:
            qsettings.setValue('ide/profiles', settings.PROFILES)

    def create_profile(self):
        """Create a profile binding files and projects to a key."""
        profileInfo = QInputDialog.getText(None,
            self.tr("Create Profile"), self.tr(
                "The Current Files and Projects will "
                "be associated to this profile.\n"
                "Profile Name:"))
        if profileInfo[1]:
            profileName = profileInfo[0]
            if not profileName or profileName in settings.PROFILES:
                QMessageBox.information(self, self.tr("Profile Name Invalid"),
                    self.tr("The Profile name is invalid or already exists."))
                return
            self.save_profile(profileName)
            return profileName

    def save_profile(self, profileName):
        """Save the updates from a profile."""
        explorer = IDE.get_service('explorer_container')
        main_container = IDE.get_service('main_container')
        if explorer and main_container:
            projects_obj = explorer.get_opened_projects()
            projects = [p.path for p in projects_obj]
            files = main_container.get_opened_documents()
            files = files[0] + files[1]
            settings.PROFILES[profileName] = [files, projects]
            qsettings = QSettings()
            qsettings.setValue('ide/profiles', settings.PROFILES)

    def activate_profile(self):
        """Show the Profile Manager dialog."""
        profilesLoader = ui_tools.ProfilesLoader(self._load_profile_data,
            self.create_profile, self.save_profile,
            settings.PROFILES, self.ide)
        profilesLoader.show()

    def deactivate_profile(self):
        """Close the Profile Session."""
        self.Profile = None

    def _load_profile_data(self, key):
        """Activate the selected profile, closing the current files/projects"""
        explorer = IDE.get_service('explorer_container')
        main_container = IDE.get_service('main_container')
        if explorer and main_container:
            explorer.close_opened_projects()
            main_container.open_files(settings.PROFILES[key][0])
            explorer.open_session_projects(settings.PROFILES[key][1])

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
                main_container = IDE.get_service('main_container')
                if main_container:
                    main_container.save_all()
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


class TabShortcuts(QShortcut):

    def __init__(self, key, parent, index):
        super(TabShortcuts, self).__init__(key, parent)
        self.index = index
