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

import sys

from PyQt4.QtGui import QSplashScreen
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QPixmap
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QTextCodec
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtCore import QTranslator
from PyQt4.QtCore import QLibraryInfo
from PyQt4.QtCore import QLocale

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core import ipc
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import json_manager

#Register Components:
#lint:disable
import ninja_ide.gui.central_widget
import ninja_ide.gui.status_bar
import ninja_ide.gui.main_panel.main_container
#import ninja_ide.gui.tools_dock.tools_dock
import ninja_ide.gui.menus.menubar
#from ninja_ide.tools.completion import completion_daemon
# Explorer Container
from ninja_ide.gui.explorer.tabs import tree_projects_widget
from ninja_ide.gui.explorer.tabs import tree_symbols_widget
from ninja_ide.gui.explorer.tabs import web_inspector
# Checkers
from ninja_ide.gui.editor.checkers import errors_checker
from ninja_ide.gui.editor.checkers import pep8_checker
from ninja_ide.gui.editor.checkers import migration_2to3

from ninja_ide.gui.editor.checkers import migration_lists
import ninja_ide.gui.explorer.explorer_container

from ninja_ide.gui import ide
#lint:enable


def start_ide(app, filenames, projects_path, extra_plugins, linenos):
    """Load all the settings necessary before loading the UI, and start IDE."""
    QCoreApplication.setOrganizationName('NINJA-IDE')
    QCoreApplication.setOrganizationDomain('NINJA-IDE')
    QCoreApplication.setApplicationName('NINJA-IDE')
    app.setWindowIcon(QIcon(":img/icon"))

    # Check if there is another session of ninja-ide opened
    # and in that case send the filenames and projects to that session
    running = ipc.is_running()
    start_server = not running[0]
    if running[0] and (filenames or projects_path):
        sended = ipc.send_data(running[1], filenames, projects_path, linenos)
        running[1].close()
        if sended:
            sys.exit()
    else:
        running[1].close()

    # Create and display the splash screen
    splash_pix = QPixmap(":img/splash")
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Set the cursor to unblinking
    if not settings.IS_WINDOWS:
        app.setCursorFlashTime(0)

    #Set the codec for strings (QString)
    QTextCodec.setCodecForCStrings(QTextCodec.codecForName('utf-8'))

    #Translator
    qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
    language = QLocale.system().name()
    lang = qsettings.value('preferences/interface/language',
        defaultValue=language, type='QString') + '.qm'
    lang_path = file_manager.create_path(resources.LANGS, lang)
    if file_manager.file_exists(lang_path):
        settings.LANGUAGE = lang_path
    translator = QTranslator()
    if settings.LANGUAGE:
        translator.load(settings.LANGUAGE)
        app.installTranslator(translator)

        qtTranslator = QTranslator()
        qtTranslator.load("qt_" + language,
            QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        app.installTranslator(qtTranslator)

    #Loading Syntax
    splash.showMessage("Loading Syntax", Qt.AlignRight | Qt.AlignTop, Qt.black)
    json_manager.load_syntax()

    #Read Settings
    splash.showMessage("Loading Settings", Qt.AlignRight | Qt.AlignTop,
        Qt.black)
    settings.load_settings()

    #Set Stylesheet
    style_applied = False
    if settings.NINJA_SKIN not in ('Default', 'Classic Theme'):
        file_name = ("%s.qss" % settings.NINJA_SKIN)
        qss_file = file_manager.create_path(resources.NINJA_THEME_DOWNLOAD,
            file_name)
        if file_manager.file_exists(qss_file):
            with open(qss_file) as f:
                qss = f.read()
                app.setStyleSheet(qss)
                style_applied = True
    if not style_applied:
        if settings.NINJA_SKIN == 'Default':
            with open(resources.NINJA_THEME) as f:
                qss = f.read()
        else:
            with open(resources.NINJA_THEME_CLASSIC) as f:
                qss = f.read()
        app.setStyleSheet(qss)

    #Loading Schemes
    splash.showMessage("Loading Schemes",
        Qt.AlignRight | Qt.AlignTop, Qt.black)
    scheme = qsettings.value('preferences/editor/scheme', "default",
        type='QString')
    if scheme != 'default':
        scheme = file_manager.create_path(resources.EDITOR_SKINS,
            scheme + '.color')
        if file_manager.file_exists(scheme):
            resources.CUSTOM_SCHEME = json_manager.parse(open(scheme))

    #Loading Shortcuts
    resources.load_shortcuts()
    #Loading GUI
    splash.showMessage("Loading GUI", Qt.AlignRight | Qt.AlignTop, Qt.black)
    ninjaide = ide.IDE(start_server)

    #Showing GUI
    ninjaide.show()
    #OSX workaround for ninja window not in front
    try:
        ninjaide.raise_()
    except:
        pass  # I really dont mind if this fails in any form
    #Loading Session Files
    splash.showMessage("Loading Files and Projects",
        Qt.AlignRight | Qt.AlignTop, Qt.black)

    #First check if we need to load last session files
    if qsettings.value('preferences/general/loadFiles', True, type=bool):
        #Files in Main Tab
        main_files = qsettings.value('openFiles/mainTab', [])
        tempFiles = []
        if main_files:
            for file_ in main_files:
                fileData = list(file_)
                if fileData:
                    lineno = fileData[1]
                    tempFiles.append((fileData[0], lineno))
        main_files = tempFiles
        #Files in Secondary Tab
        sec_files = qsettings.value('openFiles/secondaryTab', [])
        tempFiles = []
        if sec_files:
            for file_ in sec_files:
                fileData = list(file_)
                if fileData:
                    lineno = fileData[1]
                    tempFiles.append((fileData[0], lineno))
        sec_files = tempFiles

        # Recent Files
        recent_files = qsettings.value('openFiles/recentFiles', [])
        #Current File
        current_file = qsettings.value(
                        'openFiles/currentFile', '', type='QString')
        #Projects
        projects = qsettings.value('openFiles/projects', [])
    else:
        main_files = []
        sec_files = []
        recent_files = []
        current_file = ''
        projects = []

    #Include files received from console args
    file_with_nro = list([(f[0], f[1] - 1) for f in zip(filenames, linenos)])
    file_without_nro = list([(f, 0) for f in filenames[len(linenos):]])
    main_files += file_with_nro + file_without_nro
    #Include projects received from console args
    if projects_path:
        projects += projects_path
    #FIXME: IMPROVE THIS WITH THE NEW WAY OF DO IT
    #ninjaide.load_session_files_projects(main_files, sec_files,
        #projects, current_file, recent_files)
    #Load external plugins
    #if extra_plugins:
        #ninjaide.load_external_plugins(extra_plugins)

    splash.finish(ninjaide)
    ninjaide.notify_plugin_errors()
    ninjaide.show_python_detection()
