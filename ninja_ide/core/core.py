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

import sys
import signal

from PyQt4.QtGui import QApplication
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
from ninja_ide.core import cliparser
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import json_manager


def run_ninja():
    """First obtain the execution args and create the resources folder."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Change the process name only for linux yet
    if sys.platform != 'win32' and sys.platform != 'darwin':
        try:
            import ctypes
            libc = ctypes.CDLL('libc.so.6')
            procname = 'ninja-ide'
            libc.prctl(15, '%s\0' % procname, 0, 0, 0)
        except:
            print("The process couldn't be renamed'")
    #Set the application name
    filenames, projects_path, extra_plugins, linenos, log_level, log_file = \
                                                            cliparser.parse()
    # Create NINJA-IDE user folder structure for plugins, themes, etc
    resources.create_home_dir_structure()
    from ninja_ide.tools.logger import NinjaLogger
    NinjaLogger.argparse(log_level, log_file)

    # Start the UI
    from ninja_ide.gui import ide
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName('NINJA-IDE')
    QCoreApplication.setOrganizationDomain('NINJA-IDE')
    QCoreApplication.setApplicationName('NINJA-IDE')
    app.setWindowIcon(QIcon(resources.IMAGES['icon']))

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
    splash_pix = QPixmap(resources.IMAGES['splash'])
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Set the cursor to unblinking
    if sys.platform != 'win32':
        app.setCursorFlashTime(0)

    #Set the codec for strings (QString)
    QTextCodec.setCodecForCStrings(QTextCodec.codecForName('utf-8'))

    #Translator
    qsettings = QSettings()
    language = QLocale.system().name()
    lang = qsettings.value('preferences/interface/language',
        defaultValue=language, type='QString') + '.qm'
    lang_path = file_manager.create_path(resources.LANGS, lang)
    if file_manager.file_exists(lang_path):
        settings.LANGUAGE = lang_path
    elif file_manager.file_exists(file_manager.create_path(
      resources.LANGS_DOWNLOAD, lang)):
        settings.LANGUAGE = file_manager.create_path(
            resources.LANGS_DOWNLOAD, lang)
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
            with open(resources.NINJA__THEME_CLASSIC) as f:
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
    ninja_ide = ide.IDE(start_server)

    #Showing GUI
    ninja_ide.show()

    #Loading Session Files
    splash.showMessage("Loading Files and Projects",
        Qt.AlignRight | Qt.AlignTop, Qt.black)
    #Files in Main Tab
    main_files = qsettings.value('openFiles/mainTab', [])
    if main_files is not None:
        mainFiles = list(main_files)
    else:
        mainFiles = list()
    tempFiles = []
    for file_ in mainFiles:
        fileData = list(file_)
        if fileData:
            lineno = fileData[1]
            tempFiles.append((fileData[0], lineno))
    mainFiles = tempFiles
    #Files in Secondary Tab
    sec_files = qsettings.value('openFiles/secondaryTab', [])
    if sec_files is not None:
        secondaryFiles = list(sec_files)
    else:
        secondaryFiles = list()
    tempFiles = []
    for file_ in secondaryFiles:
        fileData = list(file_)
        lineno = fileData[1]
        tempFiles.append((fileData[0], lineno))
    secondaryFiles = tempFiles
    # Recent Files
    recent = qsettings.value('openFiles/recentFiles', [])
    if recent is not None:
        recent_files = list(recent)
    else:
        recent_files = list()
    recent_files = [file_ for file_ in recent_files]
    #Current File
    current_file = qsettings.value('openFiles/currentFile', '', type='QString')
    #Projects
    projects_list = qsettings.value('openFiles/projects', [])
    if projects_list is not None:
        projects = list(projects_list)
    else:
        projects = list()
    projects = [project for project in projects]
    #Include files received from console args
    file_with_nro = list([(f[0], f[1] - 1) for f in zip(filenames, linenos)])
    file_without_nro = list([(f, 0) for f in filenames[len(linenos):]])
    mainFiles += file_with_nro + file_without_nro
    #Include projects received from console args
    if projects_path:
        projects += projects_path
    ninja_ide.load_session_files_projects(mainFiles, secondaryFiles, projects,
        current_file, recent_files)
    #Load external plugins
    if extra_plugins:
        ninja_ide.load_external_plugins(extra_plugins)

    splash.finish(ninja_ide)
    ninja_ide.notify_plugin_errors()
    sys.exit(app.exec_())