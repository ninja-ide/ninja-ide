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

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QSpacerItem,
    QSizePolicy,
    QStyleOption,
    QStyle,
    QApplication
)
from PyQt5.QtGui import QPainter

from PyQt5.QtCore import (
    pyqtSlot,
    pyqtSignal,
    Qt
)
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.tools_dock import console_widget, run_widget
from ninja_ide.tools import ui_tools
from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.gui.tools_dock import actions
from ninja_ide.core.file_handling import file_manager


logger = NinjaLogger(__name__)
DEBUG = logger.debug


class Separator(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(10)

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOption()
        option.rect = self.rect()
        option.state = QStyle.State_Horizontal
        option.palette = self.palette()
        self.style().drawPrimitive(
            QStyle.PE_IndicatorToolBarSeparator, option, painter, self)


class ToolButton(QPushButton):

    def __init__(self, number, text, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        self.setCheckable(True)
        self._number = str(number)
        self._text = text

    def paintEvent(self, event):
        super().paintEvent(event)
        fm = self.fontMetrics()
        base_line = (self.height() - fm.height()) / 2 + fm.ascent()
        number_width = fm.width(self._number)

        painter = QPainter(self)
        # Draw shortcut number
        painter.drawText(
            (15 - number_width) / 2,
            base_line,
            self._number
        )
        # Draw display name of tool button
        painter.drawText(
            18,
            base_line,
            fm.elidedText(self._text, Qt.ElideRight, self.width()))

    def sizeHint(self):
        self.ensurePolished()
        s = self.fontMetrics().size(Qt.TextSingleLine, self._text)

        s.setWidth(s.width() + 25)

        return s.expandedTo(QApplication.globalStrut())


class _ToolsDock(QWidget):

    projectExecuted = pyqtSignal("QString")

    def __init__(self, parent=None):
        super().__init__(parent)
        # Register signals connections
        # connections = (
        #    {
        #        "target": "main_container",
        #        "signal_name": "runFile",
        #        "slot": self.execute_file
        #    },
        # )
        # Buttons Widget
        self._buttons_widget = QWidget()
        self._buttons_widget.setObjectName("tools_dock")
        self._buttons_widget.setFixedHeight(26)
        self._buttons_widget.setLayout(QHBoxLayout())
        self._buttons_widget.layout().setContentsMargins(2, 2, 0, 2)
        self._buttons_widget.layout().setSpacing(10)
        IDE.register_service('tools_dock', self)

    def install(self):
        self.setup_ui()
        ide = IDE.get_service('ide')
        ide.place_me_on('tools_dock', self, 'central')
        ui_tools.install_shortcuts(self, actions.ACTIONS, ide)
        ide.goingDown.connect(self._save_settings)
        self.hide()
        # settings = IDE.ninja_settings()
        # index = int(settings.value("tools_dock/tool_visible", -1))
        # if index == -1:
        #     self.hide()
        # else:
        #     self.set_current_index(index)

    def setup_ui(self):
        self._stack = QStackedWidget()
        self.__current_widget = None
        self.__last_index = -1
        self.__buttons = []

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # toolbar = StyledBar()
        tool_layout = QVBoxLayout()
        tool_layout.setContentsMargins(0, 0, 0, 0)
        tool_layout.setSpacing(0)

        self._run_widget = run_widget.RunWidget()
        self._run_widget.allTabsClosed.connect(self.hide)

        main_layout.addLayout(tool_layout)
        self._tool_stack = QStackedWidget()
        # self._tool_stack.setMaximumHeight(22)
        self._tool_stack.setMaximumWidth(22)

        tool_layout.addWidget(self._tool_stack)
        # FIXME: poner en stack
        # clear_btn = QToolButton()
        # clear_btn.setIcon(QIcon(self.style().standardIcon(QStyle.SP_LineEditClearButton)))
        # clear_btn.clicked.connect(self._run_widget.output.clear)
        # tool_layout.addWidget(clear_btn)
        # tool_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding))
        # tool_layout.addWidget(close_button)
        # main_layout.addWidget(toolbar)
        main_layout.addWidget(self._stack)

        # Widgets
        # errors_tree = IDE.get_service('errors_tree')
        from ninja_ide.gui.tools_dock import find_in_files
        self.widgets = [
            self._run_widget,
            console_widget.ConsoleWidget(),
            find_in_files.FindInFilesWidget(),
            # errors_tree
        ]
        # Install widgets
        number = 1
        for wi in self.widgets:
            if wi is None:
                continue
            btn = ToolButton(number, wi.display_name())
            # Action
            # action = QAction(wi.display_name(), self)
            # action.triggered.connect(self._triggered)
            number += 1
            self.__buttons.append(btn)
            self._buttons_widget.layout().addWidget(btn)
            self._stack.addWidget(wi)
            btn.clicked.connect(self._button_triggered)
            # Toolbar buttons
            container = QWidget(self._tool_stack)
            tool_buttons_layout = QVBoxLayout()
            tool_buttons_layout.setContentsMargins(0, 0, 0, 0)
            tool_buttons_layout.setSpacing(0)
            for b in wi.button_widgets():
                tool_buttons_layout.addWidget(b)
            tool_buttons_layout.addStretch(5)
            container.setLayout(tool_buttons_layout)
            self._tool_stack.addWidget(container)

        self._buttons_widget.layout().addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding))
        self.__current_widget = self._stack.currentWidget()

        self.set_current_index(0)

    def execute_file(self):
        """Execute the current file"""

        main_container = IDE.get_service("main_container")
        editor_widget = main_container.get_current_editor()
        if editor_widget is not None and (editor_widget.is_modified or
                                          editor_widget.file_path):
            main_container.save_file(editor_widget)
            # FIXME: Emit a signal for plugin!
            # self.fileExecuted.emit(editor_widget.file_path)
            file_path = editor_widget.file_path
            extension = file_manager.get_file_extension(file_path)
            # TODO: Remove the IF statment and use Handlers
            if extension == "py":
                self._run_application(file_path)

    def execute_selection(self):
        """Execute selected text or current line if not have a selection"""

        main_container = IDE.get_service("main_container")
        editor_widget = main_container.get_current_editor()
        if editor_widget is not None:
            text = editor_widget.selected_text().splitlines()
            if not text:
                # Execute current line
                text = [editor_widget.line_text()]
            code = []
            for line_text in text:
                # Get part before firs '#'
                code.append(line_text.split("#", 1)[0])
            # Join to execute with python -c command
            final_code = ";".join([line.strip() for line in code if line])
            # Highlight code to be executed
            editor_widget.show_run_cursor()
            # Ok run!
            self._run_application(
                filename=editor_widget.file_path, text=final_code)

    def execute_project(self):
        """Execute the project marked as Main Project."""
        projects_explorer = IDE.get_service("projects_explorer")
        if projects_explorer is None:
            return
        nproject = projects_explorer.current_project
        if nproject:
            main_file = nproject.main_file
            if not main_file:
                # Open project properties to specify the main file
                projects_explorer.current_tree.open_project_properties()
            else:
                # Save project files
                projects_explorer.save_project()
                # Emit a signal for plugin!
                self.projectExecuted.emit(nproject.path)

                main_file = file_manager.create_path(
                    nproject.path, nproject.main_file)
                self._run_application(
                    filename=main_file,
                    python_exec=nproject.python_exec,
                    pre_exec_script=nproject.pre_exec_script,
                    post_exec_script=nproject.post_exec_script,
                    program_params=nproject.program_params
                )

    def _run_application(self, filename='', text='', python_exec=False,
                         pre_exec_script="", post_exec_script="",
                         program_params=""):
        """Execute the process to run the application"""

        self._show(0)  # Show widget in index = 0
        self._run_widget.start_process(
            filename=filename,
            code=text,
            python_exec=python_exec,
            pre_script=pre_exec_script,
            post_script=post_exec_script,
            params=program_params
        )
        # self._run_widget.input.setFocus()

    @pyqtSlot()
    def _button_triggered(self):
        # Get ToolButton index
        button = self.sender()
        index = self.__buttons.index(button)

        if index == self.current_index() and self._is_current_visible():
            self._hide()
        else:
            self._show(index)

    def _show(self, index):
        self.show()
        self.widgets[index].setVisible(True)
        self.__current_widget = self.widgets[index]
        self.set_current_index(index)

    def _hide(self):
        self.__current_widget.setVisible(False)
        index = self.current_index()
        self.__buttons[index].setChecked(False)
        self.widgets[index].setVisible(False)
        self.hide()

    def showEvent(self, event):
        super().showEvent(event)
        self._stack.currentWidget().setFocus()

    def set_current_index(self, index):

        if self.__last_index != -1:
            self.__buttons[self.__last_index].setChecked(False)
            self.__buttons[index].setChecked(True)

        if index != -1:
            self._stack.setCurrentIndex(index)
            self._tool_stack.setCurrentIndex(index)

            tool = self.widgets[index]
            tool.setVisible(True)
        self.__last_index = index

    def current_index(self):
        return self._stack.currentIndex()

    def _is_current_visible(self):
        return self.__current_widget and self.__current_widget.isVisible()

    def _save_settings(self):
        settings = IDE.ninja_settings()
        visible_index = self.current_index()
        if not self.isVisible():
            visible_index = -1
        settings.setValue("tools_dock/tool_visible", visible_index)


class StackedWidget(QStackedWidget):

    """Handle the different widgets in the stack of tools dock."""

    def setCurrentIndex(self, index):
        """Change the current widget being displayed with an animation."""
        old_widget = self.currentWidget()
        new_widget = self.widget(index)
        if old_widget != new_widget:
            self.fader_widget = ui_tools.FaderWidget(self.currentWidget(),
                                                     self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)


_ToolsDock()

'''from PyQt5.QtWidgets import (
    QWidget,
    QToolBar,
    QPushButton,
    QToolButton,
    QStyle,
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QShortcut,
    QSizePolicy
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)
from PyQt5.QtCore import (
    QSize,
    pyqtSignal,
    Qt
)
# from PyQt4.QtWebKit import QWebPage

from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.tools_dock import actions
from ninja_ide.gui.tools_dock import console_widget
from ninja_ide.gui.tools_dock import run_widget
# from ninja_ide.gui.tools_dock import web_render
# from ninja_ide.gui.tools_dock import find_in_files
# from ninja_ide.gui.tools_dock import results
from ninja_ide.tools import ui_tools
from ninja_ide import translations
# from ninja_ide.gui.theme import COLORS
from ninja_ide.gui.theme import NTheme

# TODO: add terminal widget


class _ToolsDock(ui_tools.StyledBar):
    """Former Miscellaneous, contains all the widgets in the bottom area."""

    projectExecuted = pyqtSignal('QString')

    def __init__(self, parent=None):
        super(_ToolsDock, self).__init__(parent)
        # Register signals connections
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

        # self.__toolbar = QToolBar()
        # self.__toolbar.setContentsMargins(0, 0, 0, 0)
        # self.__toolbar.setObjectName('custom')
        self.hbox = QHBoxLayout()
        vbox.addLayout(self.hbox)

        self.stack = QStackedWidget()
        vbox.addWidget(self.stack)

        self._console = console_widget.ConsoleWidget()
        self._runWidget = run_widget.RunWidget()
        # self._web = web_render.WebRender()
        # self._findInFilesWidget = find_in_files.FindInFilesWidget(
        #    self.parent())

        # Not Configurable Shortcuts
        shortEscMisc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        shortEscMisc.activated.connect(self.hide)

        # Toolbar
        # hbox.addWidget(self.__toolbar)

        self.add_to_stack(
            self._console,
            ui_tools.colored_icon(
                ":img/console", NTheme.get_color('IconBaseColor')),
            translations.TR_CONSOLE)
        self.add_to_stack(
            self._runWidget,
            ui_tools.colored_icon(
                ":img/run", NTheme.get_color('IconBaseColor')),
            translations.TR_OUTPUT)
        # self.add_to_stack(self._web, ":img/web",
        #                  translations.TR_WEB_PREVIEW)
        # self.add_to_stack(self._findInFilesWidget, ":img/find",
        #                  translations.TR_FIND_IN_FILES)
        # Last Element in the Stacked widget
        # self._results = results.Results(self)
        # self.stack.addWidget(self._results)
        # self.__toolbar.addSeparator()

        self.hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        # btn_close = QPushButton(
        #    self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        # btn_close.setIconSize(QSize(24, 24))
        # btn_close.setObjectName('navigation_button')
        btn_close = QToolButton()
        btn_close.setIcon(
            QIcon(
                ui_tools.colored_icon(
                    ":img/close",
                    NTheme.get_color('IconBaseColor'))))
        btn_close.setToolTip('F4: ' + translations.TR_ALL_VISIBILITY)
        self.hbox.addWidget(btn_close)
        btn_close.clicked.connect(self.hide)

    def install(self):
        """ Install triggered by the ide """

        self.setup_ui()
        ninjaide = IDE.get_service('ide')
        ninjaide.place_me_on("tools_dock", self, "central")
        ui_tools.install_shortcuts(self, actions.ACTIONS, ninjaide)
        ninjaide.goingDown.connect(self.save_configuration)
        qsettings = IDE.ninja_settings()
        visible = qsettings.value("tools_dock/visible", True, type=bool)

        self.setVisible(visible)

    def save_configuration(self):
        qsettings = IDE.ninja_settings()
        qsettings.setValue("tools_dock/visible", self.isVisible())

    def change_visibility(self):
        """Change tools dock visibility."""

        # FIXME: set focus on console when is visible but not focus
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
        # self.stack.show_display(val)
        self.stack.setCurrentIndex(val)

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
        if editorWidget is not None:
            if editorWidget.is_modified:
                main_container.save_file(editorWidget)
            # emit a signal for plugin!
            # self.emit(SIGNAL("fileExecuted(QString)"),
            #          editorWidget.file_path)
            ext = file_manager.get_file_extension(editorWidget.file_path)
            # TODO: Remove the IF statment and use Handlers
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
                # emit a signal for plugin!
                self.projectExecuted.emit(nproject.path)

                main_file = file_manager.create_path(nproject.path,
                                                     nproject.main_file)
                self._run_application(
                    main_file,
                    pythonExec=nproject.python_exec_command,
                    PYTHONPATH=nproject.python_path,
                    programParams=nproject.program_params,
                    preExec=nproject.pre_exec_script,
                    postExec=nproject.post_exec_script
                )

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
        # add the widget
        self.stack.addWidget(widget)
        # create a button in the toolbar to show the widget
        # button = QPushButton(QIcon(icon_path), '')
        button = QToolButton(self)
        # button.setIconSize(QSize(18, 18))
        # button.setIcon(QIcon(icon_path))
        button.setText(description)
        button.setToolTip(description)
        index = self.stack.count() - 1
        button.clicked.connect(lambda: self._item_changed(index))
        self.hbox.addWidget(button)
        # self.__toolbar.addWidget(button)

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
'''