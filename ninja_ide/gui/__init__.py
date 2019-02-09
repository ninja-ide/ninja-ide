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

from PyQt5.QtWidgets import QSplashScreen

from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt

from ninja_ide import resources
from ninja_ide.core import ipc
from ninja_ide.tools import json_manager
from ninja_ide.gui import ide

# Templates
from ninja_ide.core.template_registry import ntemplate_registry  # noqa
from ninja_ide.core.template_registry import bundled_project_types  # noqa
###########################################################################
# Start Virtual Env that supports encapsulation of plugins
###########################################################################
# from ninja_ide.core.encapsulated_env import nenvironment

# Syntax
from ninja_ide.gui.syntax_registry import syntax_registry  # noqa


def start_ide(app, filenames, projects_path, extra_plugins, linenos):
    """Load all the settings necessary before loading the UI, and start IDE."""

    def _add_splash(message):
        splash.showMessage(
            message, Qt.AlignTop | Qt.AlignRight | Qt.AlignAbsolute, Qt.black)
        QCoreApplication.processEvents()

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

    qsettings = ide.IDE.ninja_settings()
    data_qsettings = ide.IDE.data_settings()
    # FIXME: handle this
    # Translator
    # language = QLocale.system().name()
    # lang = qsettings.value('preferences/interface/language',
    #                       defaultValue=language, type='QString') + '.qm'
    # lang_path = file_manager.create_path(resources.LANGS, lang)
    # if file_manager.file_exists(lang_path):
    #    settings.LANGUAGE = lang_path
    # translator = QTranslator()
    # if settings.LANGUAGE:
    #    translator.load(settings.LANGUAGE)
    #    app.installTranslator(translator)

    #    qtTranslator = QTranslator()
    #    qtTranslator.load(
    #        "qt_" + language,
    #        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    #    app.installTranslator(qtTranslator)

    # Loading Syntax
    _add_splash("Loading Syntax..")
    json_manager.load_syntax()

    load_fonts()

    # Loading Schemes
    _add_splash("Loading Schemes...")
    all_schemes = json_manager.load_editor_schemes()
    resources.COLOR_SCHEME = all_schemes["Ninja Dark"]
    # Load Services
    _add_splash("Loading IDE Services...")
    # Register tools dock service after load some settings
    # FIXME: Find a better way to do this
    import ninja_ide.gui.tools_dock.tools_dock  # noqa
    import ninja_ide.gui.tools_dock.console_widget  # noqa
    import ninja_ide.gui.tools_dock.run_widget  # noqa
    import ninja_ide.gui.tools_dock.find_in_files  # noqa

    import ninja_ide.gui.main_panel.main_container  # noqa
    import ninja_ide.gui.central_widget  # noqa
    import ninja_ide.gui.status_bar  # noqa
    import ninja_ide.gui.menus.menubar  # noqa

    # Explorer Container
    import ninja_ide.gui.explorer.explorer_container  # noqa
    from ninja_ide.gui.explorer.tabs import tree_projects_widget  # noqa
    from ninja_ide.gui.explorer.tabs import tree_symbols_widget  # noqa
    from ninja_ide.gui.explorer.tabs import bookmark_manager  # noqa
    # from ninja_ide.gui.explorer.tabs import web_inspector
    # Checkers
    from ninja_ide.gui.editor.checkers import errors_checker  # noqa
    from ninja_ide.gui.editor.checkers import pep8_checker  # noqa
    # from ninja_ide.gui.editor.checkers import not_import_checker  # noqa
    # from ninja_ide.gui.editor.checkers import migration_2to3
    # Preferences
    # from ninja_ide.gui.dialogs.preferences import preferences_general  # noqa
    # from ninja_ide.gui.dialogs.preferences import preferences_execution  # noqa
    # # from ninja_ide.gui.dialogs.preferences import preferences_shortcuts
    # from ninja_ide.gui.dialogs.preferences import preferences_interface  # noqa
    # from ninja_ide.gui.dialogs.preferences import preferences_editor_general  # noqa
    # from ninja_ide.gui.dialogs.preferences import preferences_editor_display  # noqa
    # from ninja_ide.gui.dialogs.preferences import preferences_editor_behavior  # noqa
    # from ninja_ide.gui.dialogs.preferences import preferences_editor_intellisense  # noqa
    from ninja_ide.intellisensei import intellisense_registry  # noqa
    from ninja_ide.intellisensei import python_intellisense  # noqa
    # from ninja_ide.gui.dialogs.preferences import preferences_editor_completion
    # from ninja_ide.gui.dialogs.preferences import preferences_plugins
    # from ninja_ide.gui.dialogs.preferences import preferences_theme
    from ninja_ide.gui.editor.checkers import errors_lists  # noqa
    from ninja_ide.gui.editor.checkers import errors_checker  # noqa
    from ninja_ide.gui.editor.checkers import pep8_checker  # noqa

    # Loading Shortcuts
    # resources.load_shortcuts()
    # Loading GUI
    _add_splash("Loading GUI...")
    ninjaide = ide.IDE(start_server)
    # Loading Session Files
    _add_splash("Loading Files and Projects...")
    # First check if we need to load last session files
    if qsettings.value('general/loadFiles', True, type=bool):
        files = data_qsettings.value('lastSession/openedFiles')
        projects = data_qsettings.value('lastSession/projects')
        current_file = data_qsettings.value('lastSession/currentFile')
        if files is None:
            files = []
        if projects is None:
            projects = []
        # Include files received from console args
        files_with_lineno = [(f[0], (f[1] - 1, 0))
                             for f in zip(filenames, linenos)]
        files_without_lineno = [(f, (0, 0))
                                for f in filenames[len(linenos):]]
        files += files_with_lineno + files_without_lineno
        # Include projects received from console args
        if projects_path:
            projects += projects_path
        ninjaide.load_session_files_projects(
            files, projects, current_file)

    # Showing GUI
    ninjaide.show()
    # OSX workaround for ninja window not in front
    try:
        ninjaide.raise_()
    except Exception:
        pass  # I really dont mind if this fails in any form
    # Load external plugins
    # if extra_plugins:
    #     ninjaide.load_external_plugins(extra_plugins)
    splash.finish(ninjaide)
    # ninjaide.notify_plugin_errors()
    # ninjaide.show_python_detection()


def load_fonts():
    import os
    from PyQt5.QtGui import QFontDatabase

    fonts = [f for f in os.listdir(resources.FONTS)
             if f.endswith(".ttf")]
    for font in fonts:
        QFontDatabase.addApplicationFont(os.path.join(resources.FONTS, font))
