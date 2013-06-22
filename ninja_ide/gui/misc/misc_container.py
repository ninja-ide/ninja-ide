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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QShortcut
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtWebKit import QWebPage

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.misc import console_widget
from ninja_ide.gui.misc import run_widget
from ninja_ide.gui.misc import web_render
from ninja_ide.gui.misc import find_in_files
from ninja_ide.gui.misc import results
from ninja_ide.tools import ui_tools
from ninja_ide.tools import json_manager


class _ToolsDock(QWidget):
    """Former Miscellaneous, contains all the widgets in the bottom area."""

    def __init__(self, parent=None):
        super(_ToolsDock, self).__init__(parent)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self.__toolbar = QToolBar()
        self.__toolbar.setObjectName('custom')
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        self.stack = StackedWidget()
        vbox.addWidget(self.stack)

        self._console = console_widget.ConsoleWidget()
        self.stack.addWidget(self._console)

        self._runWidget = run_widget.RunWidget()
        self.stack.addWidget(self._runWidget)

        self._web = web_render.WebRender()
        self.stack.addWidget(self._web)

        self._findInFilesWidget = find_in_files.FindInFilesWidget(
            self.parent())
        self.stack.addWidget(self._findInFilesWidget)

        #Last Element in the Stacked widget
        self._results = results.Results(self)
        self.stack.addWidget(self._results)

        self._btnConsole = QPushButton(QIcon(resources.IMAGES['console']), '')
        self._btnConsole.setToolTip(self.tr("Console"))
        self._btnRun = QPushButton(QIcon(resources.IMAGES['play']), '')
        self._btnRun.setToolTip(self.tr("Output"))
        self._btnWeb = QPushButton(QIcon(resources.IMAGES['web']), '')
        self._btnWeb.setToolTip(self.tr("Web Preview"))
        self._btnFind = QPushButton(QIcon(resources.IMAGES['find']), '')
        self._btnFind.setToolTip(self.tr("Find in Files"))
        #Toolbar
        hbox.addWidget(self.__toolbar)
        self.__toolbar.addWidget(self._btnConsole)
        self.__toolbar.addWidget(self._btnRun)
        self.__toolbar.addWidget(self._btnWeb)
        self.__toolbar.addWidget(self._btnFind)
        self.__toolbar.addSeparator()
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        btn_close = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        btn_close.setObjectName('navigation_button')
        btn_close.setToolTip(self.tr('F4: Show/Hide'))
        hbox.addWidget(btn_close)

        # Not Configurable Shortcuts
        shortEscMisc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.connect(shortEscMisc, SIGNAL("activated()"), self.hide)

        self.connect(self._btnConsole, SIGNAL("clicked()"),
            lambda: self._item_changed(0))
        self.connect(self._btnRun, SIGNAL("clicked()"),
            lambda: self._item_changed(1))
        self.connect(self._btnWeb, SIGNAL("clicked()"),
            lambda: self._item_changed(2))
        self.connect(self._btnFind, SIGNAL("clicked()"),
            lambda: self._item_changed(3))
        self.connect(btn_close, SIGNAL('clicked()'), self.hide)
        IDE.register_service(self, "tools_dock")

    def install(self, ide):
        #Register signals connections
        connections = (
            {'target': 'main_container',
            'signal_name':     "findOcurrences(QString)",
            'slot': self.show_find_occurrences},
            {'target': 'main_container',
            'signal_name': "runFile()",
            'slot': self.execute_file},
            {'target': 'explorer_container',
            'signal_name': "removeProjectFromConsole(QString)",
            'slot': self.remove_project_from_console},
            {'target': 'explorer_container',
            'signal_name': "addProjectToConsole(QString)",
            'slot': self.add_project_to_console}
            )
        IDE.register_signals('tools_dock', connections)
        self.install_shortcuts(ide)

    def install_shortcuts(self, ide):
        short = resources.get_shortcut
        shortFindInFiles = QShortcut(short("Find-in-files"), ide)
        IDE.register_shortcut('Find-in-files', shortFindInFiles)
        shortRunFile = QShortcut(short("Run-file"), ide)
        IDE.register_shortcut('Run-file', shortRunFile)
        shortRunProject = QShortcut(short("Run-project"), ide)
        IDE.register_shortcut('Run-project', shortRunProject)
        shortStopExecution = QShortcut(short("Stop-execution"), ide)
        IDE.register_shortcut('Stop-execution', shortStopExecution)

        self.connect(shortFindInFiles, SIGNAL("activated()"),
            self.show_find_in_files_widget)
        self.connect(shortRunFile, SIGNAL("activated()"),
            self.execute_file)
        self.connect(shortRunProject, SIGNAL("activated()"),
            self.execute_project)
        self.connect(self.shortStopExecution, SIGNAL("activated()"),
            self.kill_application)

    def add_project_to_console(self, projectFolder):
        """Add the namespace of the project received into the ninja-console."""
        self._console.load_project_into_console(projectFolder)

    def remove_project_from_console(self, projectFolder):
        """Remove the namespace of the project received from the console."""
        self._console.unload_project_from_console(projectFolder)

    def gain_focus(self):
        self._console.setFocus()

    def _item_changed(self, val):
        if not self.isVisible():
            self.show()
        self.stack.show_display(val)

    def show_find_in_files_widget(self):
        index_of = self.stack.indexOf(self._findInFilesWidget)
        self._item_changed(index_of)
        self._findInFilesWidget.open()

    def show_find_occurrences(self, word):
        index_of = self.stack.indexOf(self._findInFilesWidget)
        self._item_changed(index_of)
        self._findInFilesWidget.find_occurrences(word)

    def load_toolbar(self, toolbar):
        toolbar.addWidget(self._combo)
        toolbar.addSeparator()

    def execute_file(self):
        """Execute the current file."""
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        editorWidget = main_container.get_actual_editor()
        if editorWidget:
            #emit a signal for plugin!
            self.emit(SIGNAL("fileExecuted(QString)"), editorWidget.ID)
            main_container.save_file(editorWidget)
            ext = file_manager.get_file_extension(editorWidget.ID)
            #TODO: Remove the IF statment with polymorphism using Handler
            if ext == 'py':
                self.run_application(editorWidget.ID)
            elif ext == 'html':
                self.render_web_page(editorWidget.ID)

    def execute_project(self):
        """Execute the project marked as Main Project."""
        explorer_container = IDE.get_service('explorer_container')
        if not explorer_container:
            return
        mainFile = explorer_container.get_project_main_file()
        if not mainFile and explorer_container._treeProjects and \
          explorer_container._treeProjects._actualProject:
            explorer_container._treeProjects.open_project_properties()
        elif mainFile:
            self.save_project()
            path = explorer_container.get_actual_project()
            #emit a signal for plugin!
            self.emit(SIGNAL("projectExecuted(QString)"), path)

            # load our jutsus!
            project = json_manager.read_ninja_project(path)
            python_exec = project.get('venv', False)
            if not python_exec:
                python_exec = project.get('pythonPath', 'python')
            PYTHONPATH = project.get('PYTHONPATH', None)
            params = project.get('programParams', '')
            preExec = project.get('preExecScript', '')
            postExec = project.get('postExecScript', '')
            mainFile = file_manager.create_path(path, mainFile)
            self.run_application(mainFile, pythonPath=python_exec,
                PYTHONPATH=PYTHONPATH,
                programParams=params, preExec=preExec, postExec=postExec)

    def run_application(self, fileName, pythonPath=False, PYTHONPATH=None,
            programParams='', preExec='', postExec=''):
        self._item_changed(1)
        self.show()
        self._runWidget.start_process(fileName, pythonPath, PYTHONPATH,
            programParams, preExec, postExec)
        self._runWidget.input.setFocus()

    def show_results(self, items):
        self._item_changed(4)
        self.show()
        self._results.update_result(items)
        self._results._tree.setFocus()

    def kill_application(self):
        self._runWidget.kill_process()

    def render_web_page(self, url):
        self._item_changed(2)
        self.show()
        self._web.render_page(url)
        if settings.SHOW_WEB_INSPECTOR:
            explorer_container = IDE.get_service('explorer_container')
            if explorer_container:
                explorer_container.set_inspection_page(
                self._web.webFrame.page())
                self._web.webFrame.triggerPageAction(
                    QWebPage.InspectElement, True)
                explorer_container.refresh_inspector()

    def add_to_stack(self, widget, icon_path, description):
        """
        Add a widget to the container and an button(with icon))to the toolbar
        to show the widget
        """
        #add the widget
        self.stack.addWidget(widget)
        #create a button in the toolbar to show the widget
        button = QPushButton(QIcon(icon_path), '')
        button.setToolTip(description)
        index = self.stack.count() - 1
        func = lambda: self._item_changed(index)
        self.connect(button, SIGNAL("clicked()"), func)
        self.__toolbar.addWidget(button)


class StackedWidget(QStackedWidget):

    def __init__(self):
        QStackedWidget.__init__(self)

    def setCurrentIndex(self, index):
        self.fader_widget = ui_tools.FaderWidget(self.currentWidget(),
            self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def show_display(self, index):
        self.setCurrentIndex(index)

ToolsDock = _ToolsDock()
