# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
import logging

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QSplashScreen
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QFont

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QLocale
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtCore import QTranslator
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QTextCodec
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QPoint

from ninja_ide import resources
from ninja_ide.core import plugin_manager
from ninja_ide.core import plugin_services
from ninja_ide.core import settings
from ninja_ide.core import file_manager
from ninja_ide.gui import updates
from ninja_ide.gui import actions
from ninja_ide.gui.dialogs import preferences
from ninja_ide.gui.dialogs import traceback_widget
from ninja_ide.tools import styles
from ninja_ide.tools import json_manager
#NINJA-IDE Containers
from ninja_ide.gui import central_widget
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.explorer import explorer_container
from ninja_ide.gui.misc import misc_container
from ninja_ide.gui import status_bar
#NINJA-IDE Menus
from ninja_ide.gui.menus import menu_about
from ninja_ide.gui.menus import menu_file
from ninja_ide.gui.menus import menu_edit
from ninja_ide.gui.menus import menu_view
from ninja_ide.gui.menus import menu_plugins
from ninja_ide.gui.menus import menu_project
from ninja_ide.gui.menus import menu_source

###############################################################################
# LOGGER INITIALIZE
###############################################################################
logger = logging.getLogger('ninja_ide')
#The file is open in write mode from byte 0 (1 run logger)
handler = logging.FileHandler(resources.LOG_FILE_PATH, mode='w')
formatter = logging.Formatter("%(asctime)s %(name)s:%(lineno)-4d "
                              "%(levelname)-8s %(message)s",
                              '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

###############################################################################
# IDE: MAIN CONTAINER
###############################################################################
__ideInstance = None


def IDE(*args, **kw):
    global __ideInstance
    if __ideInstance is None:
        __ideInstance = __IDE(*args, **kw)
    return __ideInstance


class __IDE(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('NINJA-IDE {Ninja-IDE Is Not Just Another IDE}')
        self.setMinimumSize(700, 500)
        #Load the size and the position of the main window
        self.load_window_geometry()

        #Profile handler
        self.profile = None
        #Opacity
        self.opacity = settings.MAX_OPACITY

        #Define Actions object before the UI
        self.actions = actions.Actions()
        #StatusBar
        self.status = status_bar.StatusBar(self)
        self.status.hide()
        self.setStatusBar(self.status)
        #Main Widget - Create first than everything else
        self.central = central_widget.CentralWidget(self)
        self.load_ui(self.central)
        self.setCentralWidget(self.central)

        #ToolBar
        self.toolbar = QToolBar(self)
        styles.set_style(self.toolbar, 'toolbar-default')
        self.toolbar.setToolTip(self.tr("Press and Drag to Move"))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.addToolBar(settings.TOOLBAR_AREA, self.toolbar)
        if settings.HIDE_TOOLBAR:
            self.toolbar.hide()

        #Install Shortcuts after the UI has been initialized
        self.actions.install_shortcuts(self)
        self.connect(self.mainContainer, SIGNAL("currentTabChanged(QString)"),
            self.actions.update_explorer)

        #Menu
        menubar = self.menuBar()
        file_ = menubar.addMenu(self.tr("&File"))
        edit = menubar.addMenu(self.tr("&Edit"))
        view = menubar.addMenu(self.tr("&View"))
        source = menubar.addMenu(self.tr("&Source"))
        project = menubar.addMenu(self.tr("&Project"))
        self.pluginsMenu = menubar.addMenu(self.tr("&Addins"))
        about = menubar.addMenu(self.tr("Abou&t"))

        #The order of the icons in the toolbar is defined by this calls
        self._menuFile = menu_file.MenuFile(file_, self.toolbar, self)
        self._menuView = menu_view.MenuView(view, self.toolbar, self)
        self._menuEdit = menu_edit.MenuEdit(edit, self.toolbar)
        self._menuSource = menu_source.MenuSource(source)
        self._menuProject = menu_project.MenuProject(project, self.toolbar)
        self._menuPlugins = menu_plugins.MenuPlugins(self.pluginsMenu)
        self._menuAbout = menu_about.MenuAbout(about)

        self.load_toolbar()

        #Plugin Manager
        services = {
            'editor': plugin_services.MainService(),
            'toolbar': plugin_services.ToolbarService(self.toolbar),
            'menuApp': plugin_services.MenuAppService(self.pluginsMenu),
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

        self.connect(self.mainContainer, SIGNAL("fileSaved(QString)"),
            self.show_status_message)

    def load_toolbar(self):
        self.toolbar.clear()
        toolbar_items = {}
        toolbar_items.update(self._menuFile.toolbar_items)
        toolbar_items.update(self._menuView.toolbar_items)
        toolbar_items.update(self._menuEdit.toolbar_items)
        toolbar_items.update(self._menuSource.toolbar_items)
        toolbar_items.update(self._menuProject.toolbar_items)

        for item in settings.TOOLBAR_ITEMS:
            if item == 'separator':
                self.toolbar.addSeparator()
            else:
                tool_item = toolbar_items.get(item, None)
                if tool_item is not None:
                    self.toolbar.addAction(tool_item)

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
        # Update symbols
        self.connect(self.mainContainer, SIGNAL("updateLocator(QString)"),
            self.status.explore_file_code)
        #Create Explorer Panel
        self.explorer = explorer_container.ExplorerContainer(self)
        self.connect(self.central, SIGNAL("splitterCentralRotated()"),
            self.explorer.rotate_tab_position)
        self.connect(self.explorer, SIGNAL("updateLocator()"),
            self.status.explore_code)
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
        self.connect(self.mainContainer,
            SIGNAL("cursorPositionChange(int, int)"),
            self.central.lateralPanel.update_line_col)
        self.connect(self.mainContainer, SIGNAL("enabledFollowMode(bool)"),
            self.central.enable_follow_mode_scrollbar)

        if settings.SHOW_START_PAGE:
            self.mainContainer.show_start_page()

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

    def load_session_files_projects(self, filesTab1, filesTab2, projects):
        self.mainContainer.open_files(filesTab1, notIDEStart=False)
        self.mainContainer.open_files(filesTab2, mainTab=False,
            notIDEStart=False)
        self.explorer.open_session_projects(projects, notIDEStart=False)
        self.status.explore_code()

    def open_file(self, filename):
        if filename:
            self.mainContainer.open_file(unicode(filename))

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

    def wheelEvent(self, event):
        if event.modifiers() == Qt.AltModifier:
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
        openedFiles = self.mainContainer.get_opened_documents()
        if qsettings.value('preferences/general/loadFiles', True).toBool():
            projects_obj = self.explorer.get_opened_projects()
            projects = [p.path for p in projects_obj]
            qsettings.setValue('openFiles/projects',
                projects)
            if len(openedFiles) > 0:
                qsettings.setValue('openFiles/mainTab', openedFiles[0])
            if len(openedFiles) == 2:
                qsettings.setValue('openFiles/secondaryTab', openedFiles[1])
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
        qsettings.setValue("window/hide_toolbar",
            not self.toolbar.isVisible() and self.menuBar().isVisible())
        #Save Profiles
        if self.profile is not None:
            self.actions.save_profile(self.profile)
        else:
            qsettings.setValue('ide/profiles', settings.PROFILES)

    def load_window_geometry(self):
        """Load from QSettings the window size of de Ninja IDE"""
        qsettings = QSettings()
        if qsettings.value("window/maximized", True).toBool():
            self.setWindowState(Qt.WindowMaximized)
        else:
            self.resize(qsettings.value("window/size",
                QSize(800, 600)).toSize())
            self.move(qsettings.value("window/pos",
                QPoint(100, 100)).toPoint())

    def closeEvent(self, event):
        if settings.CONFIRM_EXIT and \
        self.mainContainer.check_for_unsaved_tabs():
            val = QMessageBox.question(self,
                self.tr("Some changes were not saved"),
                self.tr("Do you want to exit anyway?"),
                QMessageBox.Yes, QMessageBox.No)
            if val == QMessageBox.No:
                event.ignore()
        self.save_settings()
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


###############################################################################
# START NINJA-IDE
###############################################################################


def start(listener, filenames=None, projects_path=None, extra_plugins=None):
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName('NINJA-IDE')
    QCoreApplication.setOrganizationDomain('NINJA-IDE')
    QCoreApplication.setApplicationName('NINJA-IDE')
    app.setWindowIcon(QIcon(resources.IMAGES['icon']))

    # Create and display the splash screen
    splash_pix = QPixmap(resources.IMAGES['splash'])
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Set the cursor to unblinking
    app.setCursorFlashTime(0)

    #Set the codec for strings (QString)
    QTextCodec.setCodecForCStrings(QTextCodec.codecForName('utf-8'))

    #Translator
    qsettings = QSettings()
    language = QLocale.system().language()
    lang = unicode(qsettings.value(
        'preferences/interface/language', language).toString()) + '.qm'
    lang_path = file_manager.create_path(resources.LANGS, unicode(lang))
    if file_manager.file_exists(lang_path):
        settings.LANGUAGE = lang_path
    elif file_manager.file_exists(file_manager.create_path(
      resources.LANGS_DOWNLOAD, unicode(lang))):
        settings.LANGUAGE = file_manager.create_path(
            resources.LANGS_DOWNLOAD, unicode(lang))
    translator = QTranslator()
    if settings.LANGUAGE:
        translator.load(settings.LANGUAGE)
        app.installTranslator(translator)

    #Loading Syntax
    splash.showMessage("Loading Syntax", Qt.AlignRight | Qt.AlignTop, Qt.black)
    json_manager.load_syntax()

    #Read Settings
    splash.showMessage("Loading Settings", Qt.AlignRight | Qt.AlignTop,
        Qt.black)
    settings.load_settings()

    #Loading Themes
    splash.showMessage("Loading Themes", Qt.AlignRight | Qt.AlignTop, Qt.black)
    scheme = unicode(qsettings.value('preferences/editor/scheme',
        "default").toString())
    if scheme != 'default':
        scheme = file_manager.create_path(resources.EDITOR_SKINS,
            scheme + '.color')
        if file_manager.file_exists(scheme):
            resources.CUSTOM_SCHEME = json_manager.parse(open(scheme))

    #Loading Shortcuts
    resources.load_shortcuts()
    #Loading GUI
    splash.showMessage("Loading GUI", Qt.AlignRight | Qt.AlignTop, Qt.black)
    ide = IDE()

    #Showing GUI
    ide.show()
    #Connect listener signals
    ide.connect(listener, SIGNAL("fileOpenRequested(QString)"),
        ide.open_file)
    ide.connect(listener, SIGNAL("projectOpenRequested(QString)"),
        ide.open_project)

    #Loading Session Files
    splash.showMessage("Loading Files and Projects",
        Qt.AlignRight | Qt.AlignTop, Qt.black)
    #Files in Main Tab
    mainFiles = qsettings.value('openFiles/mainTab', []).toList()
    tempFiles = []
    for file_ in mainFiles:
        fileData = file_.toList()
        tempFiles.append((unicode(fileData[0].toString()),
            fileData[1].toInt()[0]))
    mainFiles = tempFiles
    #Files in Secondary Tab
    secondaryFiles = qsettings.value('openFiles/secondaryTab', []).toList()
    tempFiles = []
    for file_ in secondaryFiles:
        fileData = file_.toList()
        tempFiles.append((unicode(fileData[0].toString()),
            fileData[1].toInt()[0]))
    secondaryFiles = tempFiles
    #Projects
    projects = qsettings.value('openFiles/projects', []).toList()
    projects = [unicode(project.toString()) for project in projects]
    #Include files received from console args
    if filenames:
        mainFiles += [(f, 0) for f in filenames]
    #Include projects received from console args
    if projects_path:
        projects += projects_path
    ide.load_session_files_projects(mainFiles, secondaryFiles, projects)
    #Load external plugins
    if extra_plugins:
        ide.load_external_plugins(extra_plugins)

    splash.finish(ide)
    ide.notify_plugin_errors()
    sys.exit(app.exec_())
