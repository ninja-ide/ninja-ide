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

import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedLayout,
    QFileDialog,
    QMessageBox,
    QShortcut
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    Qt
)
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide.gui.main_panel import actions
from ninja_ide.gui.main_panel import combo_editor
from ninja_ide.gui import dynamic_splitter
from ninja_ide.gui.main_panel import start_page
from ninja_ide.gui.editor import editor
from ninja_ide import translations
from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.gui.editor import editor
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools.locator import locator_widget
from ninja_ide.gui.main_panel import add_file_folder
from ninja_ide.gui.main_panel.helpers import split_orientation
from ninja_ide.gui import indicator

logger = NinjaLogger(__name__)


class _MainContainer(QWidget):

    currentEditorChanged = pyqtSignal("QString")
    fileOpened = pyqtSignal("QString")
    fileSaved = pyqtSignal("QString")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vbox = QVBoxLayout(self)
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(0)
        self.stack = QStackedLayout()
        self.stack.setStackingMode(QStackedLayout.StackAll)
        self._vbox.addLayout(self.stack)
        self.splitter = dynamic_splitter.DynamicSplitter()
        self.setAcceptDrops(True)
        # QML UI
        self._add_file_folder = add_file_folder.AddFileFolderWidget(self)

        if settings.SHOW_START_PAGE:
            self.show_start_page()

        IDE.register_service("main_container", self)
        # Register signals connections
        connections = (
            {
                "target": "main_container",
                "signal_name": "updateLocator",
                "slot": self._explore_code
            },
            {
                "target": "filesystem",
                "signal_name": "projectOpened",
                "slot": self._explore_code
            },
            {
                "target": "projects_explore",
                "signal_name": "updateLocator",
                "slot": self._explore_code
            }
        )

        IDE.register_signals("main_container", connections)

        esc_sort = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc_sort.activated.connect(self._set_focus_to_editor)

    def install(self):
        ninjaide = IDE.get_service("ide")
        ninjaide.place_me_on("main_container", self, "central", top=True)

        self.combo_area = combo_editor.ComboEditor(original=True)
        self.combo_area.allFilesClosed.connect(self._files_closed)
        self.splitter.add_widget(self.combo_area)
        self.add_widget(self.splitter)
        # self.current_widget = self.combo_area
        # Code Locator
        self._code_locator = locator_widget.LocatorWidget(ninjaide)

        ui_tools.install_shortcuts(self, actions.ACTIONS, ninjaide)

    def _set_focus_to_editor(self):
        status_bar = IDE.get_service("status_bar")
        tools_doock = IDE.get_service("tools_dock")
        editor_widget = self.get_current_editor()
        if status_bar.isVisible() and tools_doock.isVisible():
            status_bar.hide_status_bar()
        elif tools_doock.isVisible():
            tools_doock._hide()
        elif status_bar.isVisible():
            status_bar.hide_status_bar()
        if editor_widget is not None:
            editor_widget.clear_extra_selections('searchs')

    def split_assistance(self):
        split_widget = split_orientation.SplitOrientation(self)
        split_widget.show()

    def show_dialog(self, widget):
        self.add_widget(widget)
        self.stack.setCurrentWidget(widget)

    def show_split(self, orientation_vertical=False):
        orientation = Qt.Horizontal
        if orientation_vertical:
            orientation = Qt.Vertical
        self.combo_area.split_editor(orientation)

    def show_locator(self):
        """Show the Locator Widget"""

        if not self._code_locator.isVisible():
            self._code_locator.show()

    def _explore_code(self):
        """Update locator metadata for the current projects"""

        self._code_locator.explore_code()

    def current_editor_changed(self, filename):
        """Notify the new filename of the current editor"""

        if filename is None:
            filename = translations.TR_NEW_DOCUMENT
        self.currentEditorChanged.emit(filename)

    def get_current_editor(self):
        current_widget = self.combo_area.current_editor()
        if isinstance(current_widget, editor.NEditor):
            return current_widget
        return None

    def open_file(self, filename='', line=-1, col=0):
        logger.debug("Will try to open %s" % filename)
        if not filename:
            logger.debug("Has no filename")
            if settings.WORKSPACE:
                directory = settings.WORKSPACE
            else:
                directory = os.path.expanduser("~")
                editor_widget = self.get_current_editor()
                ninjaide = IDE.get_service("ide")
                current_project = ninjaide.get_current_project()
                # TODO: handle current project in NProject
                if current_project is not None:
                    directory = current_project.full_path
                elif editor_widget is not None and editor_widget.file_path:
                    directory = file_manager.get_folder(
                        editor_widget.file_path)
            extensions = ";;".join(
                ["{}(*{})".format(e.upper()[1:], e)
                    for e in settings.SUPPORTED_EXTENSIONS + [".*", ""]])
            filenames = QFileDialog.getOpenFileNames(
                self,
                "Open File",  # FIXME: translations
                directory,
                extensions
            )[0]
        else:
            logger.debug("Has filename")
            filenames = [filename]
        if not filenames:
            return
        for filename in filenames:
            logger.debug("Will try to open: %s" % filename)
            self.__open_file(filename, line, col)

    def __open_file(self, filename, line, col):
        try:
            editor_widget = self.add_editor(filename)
            if line != -1:
                editor_widget.go_to_line(line, col)
            self.currentEditorChanged.emit(filename)
        except file_manager.NinjaIOException as reason:
            QMessageBox.information(
                self,
                "The file couldn't be open",  # FIXME: translations
                str(reason))
            logger.error("The file %s couldn't be open" % filename)

    def save_file(self, editor_widget=None):
        if editor_widget is None:
            # This may return None if there is not editor present
            editor_widget = self.get_current_editor()
        if editor_widget is None:
            return False
        # Ok, we have an editor instance
        # Save to file only if editor really was modified
        if editor_widget.is_modified:
            try:
                if editor_widget.nfile.is_new_file or \
                        not editor_widget.nfile.has_write_permission():
                    return self.save_file_as(editor_widget)
                # FIXME: beforeFileSaved.emit
                if settings.REMOVE_TRAILING_SPACES:
                    pass
                # FIXME: new line at end
                # Save content
                editor_widget.neditable.save_content()
                # FIXME: encoding
                # FIXME: translations
                self.fileSaved.emit("File Saved: %s" % editor_widget.file_path)
                return True
            except Exception as reason:
                logger.error("Save file error: %s" % reason)
                QMessageBox.information(
                    self,
                    "Save Error",
                    "The file could't be saved!"
                )
            return False

    def save_file_as(self, editor_widget=None):
        force = False
        if editor_widget is None:
            # We invoque from menu
            editor_widget = self.get_current_editor()
            if editor_widget is None:
                # We haven't editor in main container
                return False
            force = True
        try:
            filters = "(*.py);;(*.*)"
            if editor_widget.file_path is not None:  # Existing file
                extension = file_manager.get_file_extension(
                    editor_widget.file_path)
                if extension != 'py':
                    filters = "(*.%s);;(*.py);;(*.*)" % extension
            save_folder = self._get_save_folder(editor_widget.file_path)
            filename = QFileDialog.getSaveFileName(
                self, "Save File", save_folder, filters
            )[0]
            if not filename:
                return False
            # FIXME: remove trailing spaces
            extension = file_manager.get_file_extension(filename)
            if not extension:
                filename = "%s.%s" % (filename, "py")
            editor_widget.neditable.save_content(path=filename, force=force)

            self.fileSaved.emit("File Saved: {}".format(filename))
            self.currentEditorChanged.emit(filename)
            return True
        except file_manager.NinjaFileExistsException as reason:
            QMessageBox.information(
                self, "File Already Exists",
                "Invalid Path: the file '%s' already exists." % reason.filename
            )
        except Exception as reason:
            logger.error("save_file_as: %s", reason)
            QMessageBox.information(
                self, "Save Error",
                "The file couldn't be saved!"
            )
        return False

    def _get_save_folder(self, filename):
        """Returns the root directory of the 'Main Project'
        or the home folder"""

        ninjaide = IDE.get_service("ide")
        current_project = ninjaide.get_current_project()
        if current_project is not None:
            return current_project.path
        return os.path.expanduser("~")

    def close_file(self):
        self.combo_area.close_current_file()

    def add_editor(self, filename=None):
        ninjaide = IDE.get_service("ide")
        editable = ninjaide.get_or_create_editable(filename)
        if editable.editor:
            # If already open
            logger.debug("%s is already open" % filename)
            self.combo_area.set_current(editable)
            return self.combo_area.current_editor()
        else:
            pass

        editor_widget = self.create_editor_from_editable(editable)
        # editor_widget.set_language()
        # Add the tab
        keep_index = (self.splitter.count() > 1 and
                      self.combo_area.stacked.count() > 0)
        self.combo_area.add_editor(editable, keep_index)
        # Emit a signal about the file open
        self.fileOpened.emit(filename)

        if not keep_index:
            self.combo_area.set_current(editable)

        self.stack.setCurrentWidget(self.splitter)
        editor_widget.setFocus()
        return editor_widget

    def create_editor_from_editable(self, editable):
        neditor = editor.create_editor(editable)
        neditor.zoomChanged.connect(self._show_zoom_indicator)
        neditor.destroyed.connect(self.__on_editor_destroyed)
        # editable.fileSaved.connect(self._editor_tab)
        return neditor

    def _show_zoom_indicator(self, zoom):
        neditor = self.get_current_editor()
        indicator.Indicator.show_text(
            neditor, "Zoom: {} %".format(str(zoom)))

    @pyqtSlot()
    def __on_editor_destroyed(self):
        indicator.Indicator.instance = None

    def add_widget(self, widget):
        self.stack.addWidget(widget)

    def show_start_page(self):
        """Show Start Page widget in main container"""

        startp = self.stack.widget(0)
        if isinstance(startp, start_page.StartPage):
            self.stack.setCurrentIndex(0)
        else:
            startp = start_page.StartPage(parent=self)
            startp.newFile.connect(self.add_editor)
            self.stack.insertWidget(0, startp)
            self.stack.setCurrentIndex(0)

    def _files_closed(self):
        if settings.SHOW_START_PAGE:
            self.show_start_page()

    def add_status_bar(self, status_bar):
        self._vbox.addWidget(status_bar)

    def create_file(self, base_path, project_path):
        self._add_file_folder.create_file(base_path, project_path)

    def create_folder(self, base_path, project_path):
        self._add_file_folder.create_folder(base_path, project_path)

    def zoom_in_editor(self):
        """Increase the font size in the current editor"""

        editor_widget = self.get_current_editor()
        if editor_widget is not None:
            editor_widget.zoom(1.)

    def zoom_out_editor(self):
        """Decrease the font size in the current editor"""

        editor_widget = self.get_current_editor()
        if editor_widget is not None:
            editor_widget.zoom(-1.)

    def reset_zoom_editor(self):
        """Reset the to original font size in the current editor"""

        editor_widget = self.get_current_editor()
        if editor_widget is not None:
            editor_widget.reset_zoom()

    def editor_move_up(self):
        editor_widget = self.get_current_editor()
        if editor_widget is not None:
            editor_widget.move_up_down(up=True)

    def editor_move_down(self):
        editor_widget = self.get_current_editor()
        if editor_widget is not None:
            editor_widget.move_up_down()

    def editor_duplicate_line(self):
        editor_widget = self.get_current_editor()
        if editor_widget is not None:
            editor_widget.duplicate_line()

    def editor_comment(self):
        editor_widget = self.get_current_editor()
        if editor_widget is not None:
            editor_widget.comment()


# Register Main Container
_MainContainer()
