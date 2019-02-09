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

import collections

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QStyleOption
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QShortcut

from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QCursor

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize

from ninja_ide.core import settings
from ninja_ide.tools import ui_tools
from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.tools_dock import actions
from ninja_ide.gui.tools_dock import python_selector

logger = NinjaLogger(__name__)
DEBUG = logger.debug


class _ToolsDock(QWidget):

    __WIDGETS = {}
    __created = False
    __index = 0

    # Signals
    executeFile = pyqtSignal()
    executeProject = pyqtSignal()
    executeSelection = pyqtSignal()
    stopApplication = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Register signals connections
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.__buttons = []
        self.__action_number = 1
        self.__buttons_visibility = {}
        self.__current_widget = None
        self.__last_index = -1

        self._stack_widgets = QStackedWidget()
        layout.addWidget(self._stack_widgets)

        # Buttons Widget
        self.buttons_widget = QWidget()
        self.buttons_widget.setObjectName("tools_dock")
        self.buttons_widget.setFixedHeight(26)
        self.buttons_widget.setLayout(QHBoxLayout())
        self.buttons_widget.layout().setContentsMargins(2, 2, 5, 2)
        self.buttons_widget.layout().setSpacing(10)

        IDE.register_service("tools_dock", self)
        _ToolsDock.__created = True

    @classmethod
    def register_widget(cls, display_name, obj):
        """Register a widget providing the service name and the instance"""

        cls.__WIDGETS[cls.__index] = (obj, display_name)
        cls.__index += 1

    def install(self):
        self._load_ui()
        ninjaide = IDE.get_service("ide")
        ninjaide.place_me_on("tools_dock", self, "central")
        ui_tools.install_shortcuts(self, actions.ACTIONS, ninjaide)
        ninjaide.goingDown.connect(self._save_settings)
        ninja_settings = IDE.ninja_settings()
        index = int(ninja_settings.value("tools_dock/widgetVisible", -1))
        if index == -1:
            self.hide()
        else:
            self._show(index)

    def _load_ui(self):
        ninjaide = IDE.get_service("ide")

        shortcut_number = 1

        for index, (obj, name) in _ToolsDock.__WIDGETS.items():
            button = ToolButton(name, index + 1)
            button.setCheckable(True)
            button.clicked.connect(self.on_button_triggered)
            self.__buttons.append(button)
            self.buttons_widget.layout().addWidget(button)
            self.add_widget(name, obj)
            self.__buttons_visibility[button] = True
            # Shortcut action
            ksequence = self._get_shortcut(shortcut_number)
            short = QShortcut(ksequence, ninjaide)
            button.setToolTip(
                ui_tools.tooltip_with_shortcut(button._text, ksequence))
            short.activated.connect(self._shortcut_triggered)
            shortcut_number += 1

        self.buttons_widget.layout().addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding))

        # Python Selector
        btn_selector = ui_tools.FancyButton("Loading...")
        btn_selector.setIcon(ui_tools.get_icon("python"))
        btn_selector.setCheckable(True)
        btn_selector.setEnabled(False)
        self.buttons_widget.layout().addWidget(btn_selector)

        # QML Interface
        self._python_selector = python_selector.PythonSelector(btn_selector)

        interpreter_srv = IDE.get_service("interpreter")
        interpreter_srv.foundInterpreters.connect(
            self._python_selector.add_model)

        btn_selector.toggled[bool].connect(
            lambda v: self._python_selector.setVisible(v))

        # Popup for show/hide tools widget
        button_toggle_widgets = ToggleButton()
        self.buttons_widget.layout().addWidget(button_toggle_widgets)
        button_toggle_widgets.clicked.connect(self._show_menu)

    def _get_shortcut(self, short_number: int):
        """Return shortcut as ALT + number"""

        if short_number < 1 or short_number > 9:
            return QKeySequence()
        modifier = Qt.ALT if not settings.IS_MAC_OS else Qt.CTRL
        return QKeySequence(modifier + (Qt.Key_0 + short_number))

    def _shortcut_triggered(self):
        short = self.sender()
        widget_index = int(short.key().toString()[-1]) - 1
        widget = self.widget(widget_index)
        if widget.isVisible():
            self._hide()
        else:
            self._show(widget_index)

    def _show_menu(self):
        menu = QMenu()
        for n, (obj, display_name) in _ToolsDock.__WIDGETS.items():
            action = menu.addAction(display_name)
            action.setCheckable(True)
            action.setData(n)

            button = self.__buttons[n]
            visible = self.__buttons_visibility.get(button)
            action.setChecked(visible)

        result = menu.exec_(QCursor.pos())

        if not result:
            return
        index = result.data()
        btn = self.__buttons[index]
        visible = self.__buttons_visibility.get(btn, False)
        self.__buttons_visibility[btn] = not visible
        if visible:
            btn.hide()
        else:
            btn.show()

    def get_widget_index_by_instance(self, instance):
        index = -1
        for i, (obj, _) in self.__WIDGETS.items():
            if instance == obj:
                index = i
                break
        return index

    def execute_file(self):
        run_widget = IDE.get_service("run_widget")
        index = self.get_widget_index_by_instance(run_widget)
        self._show(index)
        self.executeFile.emit()

    def execute_project(self):
        run_widget = IDE.get_service("run_widget")
        index = self.get_widget_index_by_instance(run_widget)
        self._show(index)
        self.executeProject.emit()

    def execute_selection(self):
        run_widget = IDE.get_service("run_widget")
        index = self.get_widget_index_by_instance(run_widget)
        self._show(index)
        self.executeSelection.emit()

    def kill_application(self):
        self.stopApplication.emit()

    def add_widget(self, display_name, obj):
        self._stack_widgets.addWidget(obj)
        func = getattr(obj, "install_widget", None)
        if isinstance(func, collections.Callable):
            func()

    def on_button_triggered(self):
        # Get button index
        button = self.sender()
        index = self.__buttons.index(button)
        if index == self.current_index() and self._is_current_visible():
            self._hide()
        else:
            self._show(index)

    def widget(self, index):
        return self.__WIDGETS[index][0]

    def _hide(self):
        self.__current_widget.setVisible(False)
        index = self.current_index()
        self.__buttons[index].setChecked(False)
        self.widget(index).setVisible(False)
        self.hide()

    def hide_widget(self, obj):
        index = self.get_widget_index_by_instance(obj)
        self.set_current_index(index)
        self._hide()

    def _show(self, index):
        widget = self.widget(index)
        self.__current_widget = widget
        widget.setVisible(True)
        widget.setFocus()
        self.set_current_index(index)
        self.show()

    def set_current_index(self, index):
        if self.__last_index != -1:
            self.__buttons[self.__last_index].setChecked(False)
        self.__buttons[index].setChecked(True)
        if index != -1:
            self._stack_widgets.setCurrentIndex(index)
            widget = self.widget(index)
            widget.setVisible(True)
        self.__last_index = index

    def current_index(self):
        return self._stack_widgets.currentIndex()

    def _is_current_visible(self):
        return self.__current_widget and self.__current_widget.isVisible()

    def _save_settings(self):
        ninja_settings = IDE.ninja_settings()
        visible_widget = self.current_index()
        if not self.isVisible():
            visible_widget = -1
        ninja_settings.setValue("tools_dock/widgetVisible", visible_widget)


class ToggleButton(QToolButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toggle_button")
        self.setFocusPolicy(Qt.NoFocus)
        self.setAutoRaise(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def sizeHint(self):
        self.ensurePolished()
        return QSize(20, 20)

    def paintEvent(self, event):
        QToolButton.paintEvent(self, event)
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        opt.rect = QRect(6, self.rect().center().y() - 3, 8, 8)
        opt.rect.translate(0, -3)
        style = self.style()
        style.drawPrimitive(QStyle.PE_IndicatorArrowUp, opt, painter, self)
        opt.rect.translate(0, 6)
        style.drawPrimitive(QStyle.PE_IndicatorArrowDown, opt, painter, self)


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


class ToolButton(QPushButton):

    def __init__(self, text, number=None, parent=None):
        super().__init__(parent)
        self.setObjectName("button_tooldock")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.setFlat(True)
        if number is None:
            self._number = None
        else:
            self._number = str(number)
        self._text = text

    def setText(self, text):
        super().setText(text)
        self._text = text

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._number is None:
            painter = QPainter(self)
            fm = self.fontMetrics()
            base_line = (self.height() - fm.height()) / 2 + fm.ascent()
            painter.drawText(event.rect(), Qt.AlignCenter, self._text)
        else:
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


tools_dock = _ToolsDock()

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