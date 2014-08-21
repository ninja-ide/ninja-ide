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

import os
import collections

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSizeF
from PyQt4.QtCore import QPointF
from PyQt4.QtCore import QSize
from PyQt4.QtNetwork import QLocalServer

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import plugin_manager
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core.file_handling import nfilesystem
#from ninja_ide.core import plugin_services
from ninja_ide.core import settings
from ninja_ide.core import nsettings
from ninja_ide.core import ipc
from ninja_ide.gui import actions
from ninja_ide.gui import updates
from ninja_ide.gui import notification
from ninja_ide.gui.editor import neditable
from ninja_ide.gui.explorer import nproject
from ninja_ide.gui.dialogs import about_ninja
from ninja_ide.gui.dialogs import schemes_manager
from ninja_ide.gui.dialogs import language_manager
from ninja_ide.gui.dialogs import session_manager
from ninja_ide.gui.dialogs.preferences import preferences
from ninja_ide.gui.dialogs import traceback_widget
from ninja_ide.gui.dialogs import python_detect_dialog
from ninja_ide.gui.dialogs import plugins_store
from ninja_ide.tools import ui_tools
#from ninja_ide.tools.completion import completion_daemon

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
    __IDEBARCATEGORIES = {}
    __IDEMENUS = {}
    __IDETOOLBAR = {}
    # CONNECTIONS structure:
    # ({'target': service_name, 'signal_name': string, 'slot': function_obj},)
    # On modify add: {connected: True}
    __instance = None
    __created = False

    def __init__(self, start_server=False):
        QMainWindow.__init__(self)
        self.setWindowTitle('NINJA-IDE {Ninja-IDE Is Not Just Another IDE}')
        self.setMinimumSize(750, 500)
        QToolTip.setFont(QFont(settings.FONT.family(), 10))
        #Load the size and the position of the main window
        self.load_window_geometry()
        self.__project_to_open = 0

        #Editables
        self.__neditables = {}
        #Filesystem
        self.filesystem = nfilesystem.NVirtualFileSystem()

        #Sessions handler
        self._session = None
        #Opacity
        self.opacity = settings.MAX_OPACITY

        #ToolBar
        self.toolbar = QToolBar(self)
        if settings.IS_MAC_OS:
            self.toolbar.setIconSize(QSize(36, 36))
        else:
            self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setToolTip(translations.TR_IDE_TOOLBAR_TOOLTIP)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        # Set toggleViewAction text and tooltip
        self.toggleView = self.toolbar.toggleViewAction()
        self.toggleView.setText(translations.TR_TOOLBAR_VISIBILITY)
        self.toggleView.setToolTip(translations.TR_TOOLBAR_VISIBILITY)
        self.addToolBar(settings.TOOLBAR_AREA, self.toolbar)
        if settings.HIDE_TOOLBAR:
            self.toolbar.hide()
        #Notificator
        self.notification = notification.Notification(self)

        #Plugin Manager
        # CHECK ACTIVATE PLUGINS SETTING
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
        self.connect(self.trayIcon, SIGNAL("closeTrayIcon()"),
                     self._close_tray_icon)
        self.trayIcon.show()

        key = Qt.Key_1
        for i in range(10):
            if settings.IS_MAC_OS:
                short = ui_tools.TabShortcuts(
                    QKeySequence(Qt.CTRL + Qt.ALT + key), self, i)
            else:
                short = ui_tools.TabShortcuts(
                    QKeySequence(Qt.ALT + key), self, i)
            key += 1
            self.connect(short, SIGNAL("activated()"), self._change_tab_index)
        short = ui_tools.TabShortcuts(QKeySequence(Qt.ALT + Qt.Key_0), self, 10)
        self.connect(short, SIGNAL("activated()"), self._change_tab_index)

        # Register menu categories
        IDE.register_bar_category(translations.TR_MENU_FILE, 100)
        IDE.register_bar_category(translations.TR_MENU_EDIT, 110)
        IDE.register_bar_category(translations.TR_MENU_VIEW, 120)
        IDE.register_bar_category(translations.TR_MENU_SOURCE, 130)
        IDE.register_bar_category(translations.TR_MENU_PROJECT, 140)
        IDE.register_bar_category(translations.TR_MENU_EXTENSIONS, 150)
        IDE.register_bar_category(translations.TR_MENU_ABOUT, 160)
        # Register General Menu Items
        ui_tools.install_shortcuts(self, actions.ACTIONS_GENERAL, self)

        self.register_service('ide', self)
        self.register_service('toolbar', self.toolbar)
        self.register_service('filesystem', self.filesystem)
        #Register signals connections
        connections = (
            {'target': 'main_container',
             'signal_name': 'fileSaved(QString)',
             'slot': self.show_message},
            {'target': 'main_container',
             'signal_name': 'currentEditorChanged(QString)',
             'slot': self.change_window_title},
            {'target': 'main_container',
             'signal_name': 'openPreferences()',
             'slot': self.show_preferences},
            {'target': 'main_container',
             'signal_name': 'allTabsClosed()',
             'slot': self._last_tab_closed},
            {'target': 'explorer_container',
             'signal_name': 'changeWindowTitle(QString)',
             'slot': self.change_window_title},
            {'target': 'explorer_container',
             'signal_name': 'projectClosed(QString)',
             'slot': self.close_project},
            )
        self.register_signals('ide', connections)
        # Central Widget MUST always exists
        self.central = IDE.get_service('central_container')
        self.setCentralWidget(self.central)
        # Install Services
        for service_name in self.__IDESERVICES:
            self.install_service(service_name)
        IDE.__created = True
        # Place Status Bar
        main_container = IDE.get_service('main_container')
        status_bar = IDE.get_service('status_bar')
        main_container.add_status_bar(status_bar)
        # Load Menu Bar
        menu_bar = IDE.get_service('menu_bar')
        if menu_bar:
            menu_bar.load_menu(self)
            #These two are the same service, I think that's ok
            menu_bar.load_toolbar(self)

        #Start server if needed
        self.s_listener = None
        if start_server:
            self.s_listener = QLocalServer()
            self.s_listener.listen("ninja_ide")
            self.connect(self.s_listener, SIGNAL("newConnection()"),
                         self._process_connection)

        IDE.__instance = self

    @classmethod
    def get_service(cls, service_name):
        """Return the instance of a registered service."""
        return cls.__IDESERVICES.get(service_name, None)

    def get_menuitems(self):
        """Return a dictionary with the registered menu items."""
        return IDE.__IDEMENUS

    def get_bar_categories(self):
        """Get the registered Categories for the Application menus."""
        return IDE.__IDEBARCATEGORIES

    def get_toolbaritems(self):
        """Return a dictionary with the registered menu items."""
        return IDE.__IDETOOLBAR

    @classmethod
    def register_service(cls, service_name, obj):
        """Register a service providing the service name and the instance."""
        cls.__IDESERVICES[service_name] = obj
        if cls.__created:
            cls.__instance.install_service(service_name)

    def install_service(self, service_name):
        """Activate the registered service."""
        obj = IDE.__IDESERVICES.get(service_name, None)
        func = getattr(obj, 'install', None)
        if isinstance(func, collections.Callable):
            func()
        self._connect_signals()

    def place_me_on(self, name, obj, region="central", top=False):
        """Place a widget in some of the areas in the IDE.
        @name: id to access to that widget later if needed.
        @obj: the instance of the widget to be placed.
        @region: the area where to put the widget [central, lateral]
        @top: place the widget as the first item in the split."""
        self.central.add_to_region(name, obj, region, top)

    @classmethod
    def register_signals(cls, service_name, connections):
        """Register all the signals that a particular service wants to be
        attached of.
        @service_name: id of the service
        @connections: list of dictionaries for the connection with:
            - 'target': 'the_other_service_name',
            - 'signal_name': 'name of the signal in the other service',
            - 'slot': function object in this service"""
        cls.__IDECONNECTIONS[service_name] = connections
        if cls.__created:
            cls.__instance._connect_signals()

    def _connect_signals(self):
        """Connect the signals between the different services."""
        for service_name in IDE.__IDECONNECTIONS:
            connections = IDE.__IDECONNECTIONS[service_name]
            for connection in connections:
                if connection.get('connected', False):
                    continue
                target = IDE.__IDESERVICES.get(
                    connection['target'], None)
                slot = connection['slot']
                signal_name = connection['signal_name']
                if target and isinstance(slot, collections.Callable):
                    self.connect(target, SIGNAL(signal_name), slot)
                    connection['connected'] = True

    @classmethod
    def register_shortcut(cls, shortcut_name, shortcut, action=None):
        """Register a shortcut and action."""
        cls.__IDESHORTCUTS[shortcut_name] = (shortcut, action)

    @classmethod
    def register_menuitem(cls, menu_action, section, weight):
        """Register a QAction or QMenu in the IDE to be loaded later in the
        menubar using the section(string) to define where is going to be
        contained, and the weight define the order where is going to be
        placed.
        @menu_action: QAction or QMenu
        @section: String (name)
        @weight: int"""
        cls.__IDEMENUS[menu_action] = (section, weight)

    @classmethod
    def register_toolbar(cls, action, section, weight):
        """Register a QAction in the IDE to be loaded later in the
        toolbar using the section(string) to define where is going to be
        contained, and the weight define the order where is going to be
        placed.
        @action: QAction
        @section: String (name)
        @weight: int"""
        cls.__IDETOOLBAR[action] = (section, weight)

    @classmethod
    def register_bar_category(cls, category_name, weight):
        """Register a Menu Category to be created with the proper weight.
        @category_name: string
        @weight: int"""
        cls.__IDEBARCATEGORIES[category_name] = weight

    @classmethod
    def update_shortcut(cls, shortcut_name):
        """Update all the shortcuts of the application."""
        short = resources.get_shortcut
        shortcut, action = cls.__IDESHORTCUTS.get(shortcut_name)
        if shortcut:
            shortcut.setKey(short(shortcut_name))
        if action:
            action.setShortcut(short(shortcut_name))

    def get_or_create_nfile(self, filename):
        """For convenience access to files from ide"""
        return self.filesystem.get_file(nfile_path=filename)

    def get_or_create_editable(self, filename="", nfile=None):
        if nfile is None:
            nfile = self.filesystem.get_file(nfile_path=filename)
        editable = self.__neditables.get(nfile)
        if editable is None:
            editable = neditable.NEditable(nfile)
            self.connect(editable, SIGNAL("fileClosing(PyQt_PyObject)"),
                         self._unload_neditable)
            self.__neditables[nfile] = editable
        return editable

    def _unload_neditable(self, editable):
        self.__neditables.pop(editable.nfile)
        editable.nfile.deleteLater()
        editable.editor.deleteLater()
        editable.deleteLater()

    @property
    def opened_files(self):
        return tuple(self.__neditables.keys())

    def get_project_for_file(self, filename):
        project = None
        if filename:
            project = self.filesystem.get_project_for_file(filename)
        return project

    def create_project(self, path):
        nproj = nproject.NProject(path)
        self.filesystem.open_project(nproj)
        return nproj

    def close_project(self, project_path):
        self.filesystem.close_project(project_path)

    def get_projects(self):
        return self.filesystem.get_projects()

    def get_current_project(self):
        current_project = None
        projects = self.filesystem.get_projects()
        for project in projects:
            if projects[project].is_current:
                current_project = projects[project]
                break
        return current_project

    @classmethod
    def select_current(cls, widget):
        """Show the widget with a 4px lightblue border line."""
        widget.setProperty("highlight", True)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    @classmethod
    def unselect_current(cls, widget):
        """Remove the 4px lightblue border line from the widget."""
        widget.setProperty("highlight", False)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _close_tray_icon(self):
        """Close the System Tray Icon."""
        self.trayIcon.hide()
        self.trayIcon.deleteLater()

    def _change_tab_index(self):
        """Change the tabs of the current TabWidget using alt+numbers."""
        widget = QApplication.focusWidget()
        shortcut_index = getattr(widget, 'shortcut_index', None)
        if shortcut_index:
            obj = self.sender()
            shortcut_index(obj.index)

    def _process_connection(self):
        """Read the ipc input from another instance of ninja."""
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

    def change_toolbar_visibility(self):
        """Switch the toolbar visibility"""
        if self.toolbar.isVisible():
            self.toolbar.hide()
        else:
            self.toolbar.show()

    def load_external_plugins(self, paths):
        """Load external plugins, the ones added to ninja throw the cmd."""
        for path in paths:
            self.plugin_manager.add_plugin_dir(path)
        #load all plugins!
        self.plugin_manager.discover()
        self.plugin_manager.load_all()

    def _last_tab_closed(self):
        """
        Called when the last tasb is closed
        """
        self.explorer.cleanup_tabs()

    def show_preferences(self):
        """Open the Preferences Dialog."""
        pref = preferences.Preferences(self)
        main_container = IDE.get_service("main_container")
        if main_container:
            main_container.show_dialog(pref)
        else:
            pref.show()

    def load_session_files_projects(self, files, projects,
                                    current_file, recent_files=None):
        """Load the files and projects from previous session."""
        main_container = IDE.get_service('main_container')
        projects_explorer = IDE.get_service('projects_explorer')
        if main_container and files:
            for fileData in files:
                if file_manager.file_exists(fileData[0]):
                    mtime = os.stat(fileData[0]).st_mtime
                    ignore_checkers = (mtime == fileData[2])
                    main_container.open_file(fileData[0], fileData[1],
                                             ignore_checkers=ignore_checkers)
            if current_file:
                main_container.open_file(current_file)
        if projects_explorer and projects:
            projects_explorer.load_session_projects(projects)
            #if recent_files is not None:
                #menu_file = IDE.get_service('menu_file')
                #menu_file.update_recent_files(recent_files)

    #def _set_editors_project_data(self):
        #self.__project_to_open -= 1
        #if self.__project_to_open == 0:
            #self.disconnect(self.explorer, SIGNAL("projectOpened(QString)"),
                #self._set_editors_project_data)
            #self.mainContainer.update_editor_project()

    #def open_file(self, filename):
        #if filename:
            #self.mainContainer.open_file(filename)

    #def open_project(self, project):
        #if project:
            #self.actions.open_project(project)

    def __get_session(self):
        return self._session

    def __set_session(self, sessionName):
        self._session = sessionName
        if self._session is not None:
            self.setWindowTitle(translations.TR_SESSION_IDE_HEADER %
                                {'session': self._session})
        else:
            self.setWindowTitle(
                'NINJA-IDE {Ninja-IDE Is Not Just Another IDE}')

    Session = property(__get_session, __set_session)

    def change_window_title(self, title):
        """Change the title of the Application."""
        if self._session is None:
            self.setWindowTitle('NINJA-IDE - %s' % title)
        else:
            self.setWindowTitle((translations.TR_SESSION_IDE_HEADER %
                                {'session': self._session}) + ' - %s' % title)

    def wheelEvent(self, event):
        """Change the opacity of the application."""
        if event.modifiers() == Qt.ShiftModifier:
            if event.delta() == 120 and self.opacity < settings.MAX_OPACITY:
                self.opacity += 0.1
            elif event.delta() == -120 and self.opacity > settings.MIN_OPACITY:
                self.opacity -= 0.1
            self.setWindowOpacity(self.opacity)
            event.ignore()
        else:
            QMainWindow.wheelEvent(self, event)

    @classmethod
    def ninja_settings(cls):
        qsettings = nsettings.NSettings(resources.SETTINGS_PATH,
                                        prefix="ns")
        if cls.__created:
            cls.__instance.connect(
                qsettings,
                SIGNAL("valueChanged(QString, PyQt_PyObject)"),
                cls.__instance._settings_value_changed)
        return qsettings

    @classmethod
    def data_settings(cls):
        qsettings = nsettings.NSettings(resources.DATA_SETTINGS_PATH,
                                        prefix="ds")
        if cls.__created:
            cls.__instance.connect(
                qsettings,
                SIGNAL("valueChanged(QString, PyQt_PyObject)"),
                cls.__instance._settings_value_changed)
        return qsettings

    def _settings_value_changed(self, key, value):
        signal_name = "%s(PyQt_PyObject)" % key.replace("/", "_")
        self.emit(SIGNAL(signal_name), value)

    def save_settings(self):
        """Save the settings before the application is closed with QSettings.

        Info saved: Tabs and projects opened, windows state(size and position).
        """
        qsettings = IDE.ninja_settings()
        data_qsettings = IDE.data_settings()
        main_container = self.get_service("main_container")
        editor_widget = None
        if main_container:
            editor_widget = main_container.get_current_editor()
        current_file = ''
        if editor_widget is not None:
            current_file = editor_widget.file_path
        if qsettings.value('preferences/general/loadFiles', True, type=bool):
            openedFiles = self.filesystem.get_files()
            projects_obj = self.filesystem.get_projects()
            projects = [projects_obj[proj].path for proj in projects_obj]
            data_qsettings.setValue('lastSession/projects', projects)
            files_info = []
            for path in openedFiles:
                editable = self.__neditables.get(openedFiles[path])
                if editable is not None and editable.is_dirty:
                    stat_value = 0
                else:
                    stat_value = os.stat(path).st_mtime
                files_info.append([path,
                                  editable.editor.get_cursor_position(),
                                  stat_value])
            data_qsettings.setValue('lastSession/openedFiles', files_info)
            if current_file is not None:
                data_qsettings.setValue('lastSession/currentFile', current_file)
            data_qsettings.setValue('lastSession/recentFiles',
                                    settings.LAST_OPENED_FILES)
        data_qsettings.setValue('preferences/editor/bookmarks',
                                settings.BOOKMARKS)
        data_qsettings.setValue('preferences/editor/breakpoints',
                                settings.BREAKPOINTS)

        # Session
        if self._session is not None:
            val = QMessageBox.question(
                self,
                translations.TR_SESSION_ACTIVE_IDE_CLOSING_TITLE,
                (translations.TR_SESSION_ACTIVE_IDE_CLOSING_BODY %
                    {'session': self.Session}),
                QMessageBox.Yes, QMessageBox.No)
            if val == QMessageBox.Yes:
                session_manager.SessionsManager.save_session_data(
                    self.Session, self)
        #qsettings.setValue('preferences/general/toolbarArea',
            #self.toolBarArea(self.toolbar))
        #Save if the windows state is maximixed
        if(self.isMaximized()):
            qsettings.setValue("window/maximized", True)
        else:
            qsettings.setValue("window/maximized", False)
            #Save the size and position of the mainwindow
            qsettings.setValue("window/size", self.size())
            qsettings.setValue("window/pos", self.pos())
        self.central.save_configuration()

        #Save the toolbar visibility
        qsettings.setValue("window/hide_toolbar", not self.toolbar.isVisible())

        #else:
            #qsettings.setValue("window/hide_toolbar", False)
        #Save Misc state
        #qsettings.setValue("window/show_region1", self.misc.isVisible())
        #Save Profiles
        #if self.profile is not None:
            #self.actions.save_profile(self.profile)
        #else:
            #qsettings.setValue('ide/profiles', settings.PROFILES)

    def activate_profile(self):
        """Show the Session Manager dialog."""
        profilesLoader = session_manager.SessionsManager(self)
        profilesLoader.show()

    def deactivate_profile(self):
        """Close the Session Session."""
        self.Session = None

    def load_window_geometry(self):
        """Load from QSettings the window size of de Ninja IDE"""
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        if qsettings.value("window/maximized", True, type=bool):
            self.setWindowState(Qt.WindowMaximized)
        else:
            self.resize(qsettings.value(
                "window/size",
                QSizeF(800, 600).toSize(), type='QSize'))
            self.move(qsettings.value(
                "window/pos",
                QPointF(100, 100).toPoint(), type='QPoint'))

    def _get_unsaved_files(self):
        """Return an array with the path of the unsaved files."""
        unsaved = []
        files = self.opened_files
        for f in files:
            editable = self.__neditables.get(f)
            if editable is not None and editable.editor.is_modified:
                unsaved.append(f)
        return unsaved

    def _save_unsaved_files(self, files):
        """Save the files from the paths in the array."""
        for f in files:
            editable = self.get_or_create_editable(f)
            editable.ignore_checkers = True
            editable.save_content()

    def closeEvent(self, event):
        """Saves some global settings before closing."""
        if self.s_listener:
            self.s_listener.close()
        main_container = self.get_service("main_container")
        unsaved_files = self._get_unsaved_files()
        if (settings.CONFIRM_EXIT and unsaved_files):
            txt = '\n'.join([nfile.file_name for nfile in unsaved_files])
            val = QMessageBox.question(
                self,
                translations.TR_IDE_CONFIRM_EXIT_TITLE,
                (translations.TR_IDE_CONFIRM_EXIT_BODY % {'files': txt}),
                QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
            if val == QMessageBox.Yes:
                #Saves all open files
                self._save_unsaved_files(unsaved_files)
            if val == QMessageBox.Cancel:
                event.ignore()
                return
        self.save_settings()
        self.emit(SIGNAL("goingDown()"))
        #close python documentation server (if running)
        main_container.close_python_doc()
        #Shutdown PluginManager
        self.plugin_manager.shutdown()
        #completion_daemon.shutdown_daemon()
        super(IDE, self).closeEvent(event)

    def notify_plugin_errors(self):
        #TODO: Check if the Plugin Error dialog can be improved
        errors = self.plugin_manager.errors
        if errors:
            plugin_error_dialog = traceback_widget.PluginErrorDialog()
            for err_tuple in errors:
                plugin_error_dialog.add_traceback(err_tuple[0], err_tuple[1])
            #show the dialog
            plugin_error_dialog.exec_()

    def show_message(self, message, duration=3000):
        """Show status message."""
        self.notification.set_message(message, duration)
        self.notification.show()

    def show_plugins_store(self):
        """Open the Plugins Manager to install/uninstall plugins."""
        store = plugins_store.PluginsStore(self)
        main_container = IDE.get_service("main_container")
        if main_container:
            main_container.show_dialog(store)
        else:
            store.show()

    def show_languages(self):
        """Open the Language Manager to install/uninstall languages."""
        manager = language_manager.LanguagesManagerWidget(self)
        manager.show()

    def show_schemes(self):
        """Open the Schemes Manager to install/uninstall schemes."""
        manager = schemes_manager.SchemesManagerWidget(self)
        manager.show()

    def show_about_qt(self):
        """Show About Qt Dialog."""
        QMessageBox.aboutQt(self, translations.TR_ABOUT_QT)

    def show_about_ninja(self):
        """Show About NINJA-IDE Dialog."""
        about = about_ninja.AboutNinja(self)
        about.show()

    def show_python_detection(self):
        """Show Python detection dialog for windows."""
        #TODO: Notify the user when no python version could be found
        suggested = settings.detect_python_path()
        if suggested:
            dialog = python_detect_dialog.PythonDetectDialog(suggested, self)
            dialog.show()
