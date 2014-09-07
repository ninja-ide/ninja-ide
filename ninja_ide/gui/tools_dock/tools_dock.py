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
from PyQt4.QtCore import QSize
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtWebKit import QWebPage

from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.tools_dock import actions
from ninja_ide.gui.tools_dock import console_widget
from ninja_ide.gui.tools_dock import run_widget
from ninja_ide.gui.tools_dock import web_render
from ninja_ide.gui.tools_dock import find_in_files
from ninja_ide.gui.tools_dock import results
from ninja_ide.tools import ui_tools
from ninja_ide import translations


class _ToolsDock(QWidget):
    """Former Miscellaneous, contains all the widgets in the bottom area."""

    def __init__(self, parent=None):
        super(_ToolsDock, self).__init__(parent)
        #Register signals connections
        connections = (
            {'target': 'main_container',
             'signal_name': "findOcurrences(QString)",
             'slot': self.show_find_occurrences},
            {'target': 'main_container',
             'signal_name': "runFile(QString)",
             'slot': self.execute_file},
        )
        IDE.register_signals('tools_dock', connections)
        IDE.register_service("tools_dock", self)

    def setup_ui(self):
        """Load all the components of the ui during the install process."""
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
        self._runWidget = run_widget.RunWidget()
        self._web = web_render.WebRender()
        self._findInFilesWidget = find_in_files.FindInFilesWidget(
            self.parent())

        # Not Configurable Shortcuts
        shortEscMisc = QShortcut(QKeySequence(Qt.Key_Escape), self)

        self.connect(shortEscMisc, SIGNAL("activated()"), self.hide)

        #Toolbar
        hbox.addWidget(self.__toolbar)
        self.add_to_stack(self._console, ":img/console",
                          translations.TR_CONSOLE)
        self.add_to_stack(self._runWidget, ":img/play",
                          translations.TR_OUTPUT)
        self.add_to_stack(self._web, ":img/web",
                          translations.TR_WEB_PREVIEW)
        self.add_to_stack(self._findInFilesWidget, ":img/find",
                          translations.TR_FIND_IN_FILES)
        #Last Element in the Stacked widget
        self._results = results.Results(self)
        self.stack.addWidget(self._results)
        self.__toolbar.addSeparator()

        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        btn_close = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        btn_close.setIconSize(QSize(24, 24))
        btn_close.setObjectName('navigation_button')
        btn_close.setToolTip('F4: ' + translations.TR_ALL_VISIBILITY)
        hbox.addWidget(btn_close)
        self.connect(btn_close, SIGNAL('clicked()'), self.hide)

    def install(self):
        """Install triggered by the ide."""
        self.setup_ui()
        ninjaide = IDE.get_service('ide')
        ninjaide.place_me_on("tools_dock", self, "central")
        ui_tools.install_shortcuts(self, actions.ACTIONS, ninjaide)

        self.connect(ninjaide, SIGNAL("goingDown()"), self.save_configuration)

        qsettings = IDE.ninja_settings()
        value = qsettings.value("tools_dock/visible", True, type=bool)
        self.setVisible(value)

    def save_configuration(self):
        qsettings = IDE.ninja_settings()
        qsettings.setValue("tools_dock/visible", self.isVisible())

    def change_visibility(self):
        """Change tools dock visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def add_project_to_console(self, projectFolder):
        """Add the namespace of the project received into the ninja-console."""
        self._console.load_project_into_console(projectFolder)

    def remove_project_from_console(self, projectFolder):
        """Remove the namespace of the project received from the console."""
        self._console.unload_project_from_console(projectFolder)

    def _item_changed(self, val):
        """Change the current item."""
        if not self.isVisible():
            self.show()
        self.stack.show_display(val)

    def show_find_in_files_widget(self):
        """Show the Find In Files widget."""
        index_of = self.stack.indexOf(self._findInFilesWidget)
        self._item_changed(index_of)
        self._findInFilesWidget.open()
        self._findInFilesWidget.setFocus()

    def show_find_occurrences(self, word):
        """Show Find In Files widget in find occurrences mode."""
        index_of = self.stack.indexOf(self._findInFilesWidget)
        self._item_changed(index_of)
        self._findInFilesWidget.find_occurrences(word)
        self._findInFilesWidget.setFocus()

    def execute_file(self):
        """Execute the current file."""
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        editorWidget = main_container.get_current_editor()
        if editorWidget:
            #emit a signal for plugin!
            self.emit(SIGNAL("fileExecuted(QString)"),
                      editorWidget.file_path)
            main_container.save_file(editorWidget)
            ext = file_manager.get_file_extension(editorWidget.file_path)
            #TODO: Remove the IF statment and use Handlers
            if ext == 'py':
                self._run_application(editorWidget.file_path)
            elif ext == 'html':
                self.render_web_page(editorWidget.file_path)

    def execute_project(self):
        """Execute the project marked as Main Project."""
        projects_explorer = IDE.get_service('projects_explorer')
        if projects_explorer is None:
            return
        nproject = projects_explorer.current_project
        if nproject:
            main_file = nproject.main_file
            if not main_file and projects_explorer.current_tree:
                projects_explorer.current_tree.open_project_properties()
            elif main_file:
                projects_explorer.save_project()
                #emit a signal for plugin!
                self.emit(SIGNAL("projectExecuted(QString)"), nproject.path)

                main_file = file_manager.create_path(nproject.path,
                                                     nproject.main_file)
                self._run_application(
                    main_file,
                    pythonExec=nproject.python_exec_command,
                    PYTHONPATH=nproject.python_path,
                    programParams=nproject.program_params,
                    preExec=nproject.pre_exec_script,
                    postExec=nproject.post_exec_script)

    def _run_application(self, fileName, pythonExec=False, PYTHONPATH=None,
                         programParams='', preExec='', postExec=''):
        """Execute the process to run the application."""
        self._item_changed(1)
        self.show()
        self._runWidget.start_process(fileName, pythonExec, PYTHONPATH,
                                      programParams, preExec, postExec)
        self._runWidget.input.setFocus()

    def show_results(self, items):
        """Show Results of Navigate to for several occurrences."""
        index_of = self.stack.indexOf(self._results)
        self._item_changed(index_of)
        self.show()
        self._results.update_result(items)
        self._results._tree.setFocus()
        self._results.setFocus()

    def kill_application(self):
        """Kill the process of the application being executed."""
        self._runWidget.kill_process()

    def render_web_page(self, url):
        """Render a webpage from the url path."""
        index_of = self.stack.indexOf(self._web)
        self._item_changed(index_of)
        self.show()
        self._web.render_page(url)
        if settings.SHOW_WEB_INSPECTOR:
            web_inspector = IDE.get_service('web_inspector')
            if web_inspector:
                web_inspector.set_inspection_page(self._web.webFrame.page())
                self._web.webFrame.triggerPageAction(
                    QWebPage.InspectElement, True)
                web_inspector.refresh_inspector()
        self._web.setFocus()

    def add_to_stack(self, widget, icon_path, description):
        """
        Add a widget to the container and an button(with icon))to the toolbar
        to show the widget
        """
        #add the widget
        self.stack.addWidget(widget)
        #create a button in the toolbar to show the widget
        button = QPushButton(QIcon(icon_path), '')
        button.setIconSize(QSize(16, 16))
        button.setToolTip(description)
        index = self.stack.count() - 1
        func = lambda: self._item_changed(index)
        self.connect(button, SIGNAL("clicked()"), func)
        self.__toolbar.addWidget(button)

    def showEvent(self, event):
        super(_ToolsDock, self).showEvent(event)
        widget = self.stack.currentWidget()
        if widget:
            widget.setFocus()


class StackedWidget(QStackedWidget):

    """Handle the different widgets in the stack of tools dock."""

    def setCurrentIndex(self, index):
        """Change the current widget being displayed with an animation."""
        self.fader_widget = ui_tools.FaderWidget(self.currentWidget(),
                                                 self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def show_display(self, index):
        """Change the current widget and trigger the animation."""
        self.setCurrentIndex(index)


ToolsDock = _ToolsDock()
