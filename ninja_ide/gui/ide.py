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
from ninja_ide.gui import actions
from ninja_ide.gui import translations
from ninja_ide.gui import updates
from ninja_ide.gui.editor import neditable
from ninja_ide.gui.dialogs import about_ninja
from ninja_ide.gui.dialogs import plugins_manager
from ninja_ide.gui.dialogs import themes_manager
from ninja_ide.gui.dialogs import language_manager
from ninja_ide.gui.dialogs import preferences
from ninja_ide.gui.dialogs import traceback_widget
from ninja_ide.gui.dialogs import python_detect_dialog
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
    __IDEMENUSCATEGORY = {}
    __IDEMENUS = {}
    # CONNECTIONS structure:
    # ({'target': service_name, 'signal_name': string, 'slot': function_obj},)
    # On modify add: {connected: True}
    __instance = None
    __created = False

    def __init__(self, start_server=False):
        QMainWindow.__init__(self)
        self.setWindowTitle('NINJA-IDE {Ninja-IDE Is Not Just Another IDE}')
        self.setMinimumSize(700, 500)
        QToolTip.setFont(QFont(settings.FONT_FAMILY, 10))
        #Load the size and the position of the main window
        self.load_window_geometry()
        self.__project_to_open = 0

        #Editables
        self.__neditables = {}

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
        IDE.register_menu_category(translations.TR_MENU_FILE, 100)
        IDE.register_menu_category(translations.TR_MENU_EDIT, 110)
        IDE.register_menu_category(translations.TR_MENU_VIEW, 120)
        IDE.register_menu_category(translations.TR_MENU_SOURCE, 130)
        IDE.register_menu_category(translations.TR_MENU_PROJECT, 140)
        IDE.register_menu_category(translations.TR_MENU_ADDINS, 150)
        IDE.register_menu_category(translations.TR_MENU_ABOUT, 160)
        # Register General Menu Items
        ui_tools.install_shortcuts(self, actions.ACTIONS_GENERAL, self)

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
            'slot': self.show_preferences},
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
        self.__created = True
        menu_bar = IDE.get_service('menu_bar')
        if menu_bar:
            menu_bar.load_menu(self)
            #These two are the same service, I think that's ok
            menu_bar.load_toolbar(self)

    @classmethod
    def get_service(cls, service_name):
        """Return the instance of a registered service."""
        return cls.__IDESERVICES.get(service_name, None)

    def get_menuitems(self):
        """Return a dictionary with the registered menu items."""
        return self.__IDEMENUS

    def get_menu_categories(self):
        """Get the registered Categories for the Application menus."""
        return self.__IDEMENUSCATEGORY

    @classmethod
    def register_service(cls, service_name, obj):
        """Register a service providing the service name and the instance."""
        cls.__IDESERVICES[service_name] = obj
        if cls.__created:
            cls.__instance.install_service(service_name)

    def install_service(self, service_name):
        """Activate the registered service."""
        obj = self.__IDESERVICES.get(service_name, None)
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
    def register_menu_category(cls, category_name, weight):
        """Register a Menu Category to be created with the proper weight.
        @category_name: string
        @weight: int"""
        cls.__IDEMENUSCATEGORY[category_name] = weight

    @classmethod
    def update_shortcut(cls, shortcut_name):
        """Update all the shortcuts of the application."""
        short = resources.get_shortcut
        shortcut, action = cls.__IDESHORTCUTS.get(shortcut_name)
        if shortcut:
            shortcut.setKey(short(shortcut_name))
        if action:
            action.setShortcut(short(shortcut_name))

    def get_editable(self, filename):
        editable = self.__neditables.get(filename)
        if editable is None:
            editable = neditable.NEditable()
            self.__neditables[editable.ID] = editable
        return editable

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

    def switch_focus(self):
        """Switch the current keyboard focus to the next widget."""
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
        pref = preferences.PreferencesWidget(self)
        pref.show()

    def load_session_files_projects(self, filesTab1, filesTab2, projects,
        current_file, recent_files=None):
        """Load the files and projects from previous session."""
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
        """Change the title of the Application."""
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

    def save_settings(self):
        """Save the settings before the application is closed with QSettings.

        Info saved: Tabs and projects opened, windows state(size and position).
        """
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
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
            qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
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
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        if qsettings.value("window/maximized", True, type=bool):
            self.setWindowState(Qt.WindowMaximized)
        else:
            self.resize(qsettings.value("window/size",
                QSizeF(800, 600).toSize(), type='QSize'))
            self.move(qsettings.value("window/pos",
                QPointF(100, 100).toPoint(), type='QPoint'))

    def closeEvent(self, event):
        """Saves some global settings before closing."""
        if self.s_listener:
            self.s_listener.close()
        #if (settings.CONFIRM_EXIT and
                #self.mainContainer.check_for_unsaved_tabs()):
            #unsaved_files = self.mainContainer.get_unsaved_files()
            #txt = '\n'.join(unsaved_files)
            #val = QMessageBox.question(self,
                #self.tr("Some changes were not saved"),
                #(self.tr("%s\n\nDo you want to save them?") % txt),
                #QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
            #if val == QMessageBox.Yes:
                ##Saves all open files
                #main_container = IDE.get_service('main_container')
                #if main_container:
                    #main_container.save_all()
            #if val == QMessageBox.Cancel:
                #event.ignore()
        #self.emit(SIGNAL("goingDown()"))
        #self.save_settings()
        #completion_daemon.shutdown_daemon()
        ##close python documentation server (if running)
        #self.mainContainer.close_python_doc()
        ##Shutdown PluginManager
        self.plugin_manager.shutdown()
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

    def show_status_message(self, message, duration=1000):
        """Show status message."""
        pass

    def show_manager(self):
        """Open the Plugins Manager to install/uninstall plugins."""
        manager = plugins_manager.PluginsManagerWidget(self)
        manager.show()
        if manager._requirements:
            dependencyDialog = plugins_manager.DependenciesHelpDialog(
                manager._requirements)
            dependencyDialog.show()

    def show_languages(self):
        """Open the Language Manager to install/uninstall languages."""
        manager = language_manager.LanguagesManagerWidget(self)
        manager.show()

    def show_themes(self):
        """Open the Themes Manager to install/uninstall themes."""
        manager = themes_manager.ThemesManagerWidget(self)
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