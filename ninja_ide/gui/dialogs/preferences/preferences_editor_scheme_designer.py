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

import copy
from getpass import getuser
from string import ascii_letters

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QColorDialog
from PyQt4.QtGui import QGroupBox
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import json_manager
from ninja_ide.gui.ide import IDE


class EditorSchemeDesigner(QDialog):
    """Editor Scheme Designer Class Widget"""

    def __init__(self, scheme, parent):
        super(EditorSchemeDesigner, self).__init__(parent, Qt.Dialog)
        self.original_style = copy.copy(resources.CUSTOM_SCHEME)
        self._avoid_on_loading, self.saved, self._components = True, False, {}
        self.setWindowTitle(translations.TR_PREFERENCES_EDITOR_SCHEME_DESIGNER)
        self.setMinimumSize(450, 480)
        self.setMaximumSize(500, 900)
        self.resize(450, 600)

        # all layouts and groupboxes
        group0 = QGroupBox(translations.TR_PROJECT_NAME)  # scheme filename
        group1 = QGroupBox(translations.TR_PROJECT_PROPERTIES)  # properties
        group2 = QGroupBox(translations.TR_PREVIEW)       # quick preview thingy
        group0_hbox, group1_vbox = QHBoxLayout(group0), QVBoxLayout(group1)
        this_dialog_vbox, group2_vbox = QVBoxLayout(self), QVBoxLayout(group2)
        self._grid, scrollArea, frame = QGridLayout(), QScrollArea(), QFrame()

        # widgets
        self.line_name, btnSave = QLineEdit(), QPushButton(translations.TR_SAVE)
        self.line_name.setPlaceholderText(getuser().capitalize() + "s_scheme")
        group0_hbox.addWidget(self.line_name)
        group0_hbox.addWidget(btnSave)
        self.connect(btnSave, SIGNAL("clicked()"), self.save_scheme)
        _demo = "<center>" + ascii_letters  # demo text for preview
        self.preview_label1, self.preview_label2 = QLabel(_demo), QLabel(_demo)
        group2_vbox.addWidget(self.preview_label1)
        group2_vbox.addWidget(self.preview_label2)

        # rows titles
        self._grid.addWidget(QLabel("<b>" + translations.TR_PROJECT_NAME), 0, 0)
        self._grid.addWidget(QLabel("<b>" + translations.TR_CODE), 0, 1)
        self._grid.addWidget(
            QLabel("<b>" + translations.TR_EDITOR_SCHEME_PICK_COLOR), 0, 2)

        # fill rows
        for key in sorted(tuple(resources.COLOR_SCHEME.keys())):
            self.add_item(key, scheme)
        self.preview_label1.setStyleSheet('background:transparent')
        self.preview_label2.setStyleSheet('color:     transparent')

        # fill the scroll area
        frame.setLayout(self._grid)
        scrollArea.setWidget(frame)
        group1_vbox.addWidget(scrollArea)

        # put groups on the dialog
        this_dialog_vbox.addWidget(group1)
        this_dialog_vbox.addWidget(group2)
        this_dialog_vbox.addWidget(group0)
        self._avoid_on_loading = self._modified = False

    def add_item(self, key, scheme):
        """Take key and scheme arguments and fill up the grid with widgets."""
        row = self._grid.rowCount()
        self._grid.addWidget(QLabel(key), row, 0)
        isnum = isinstance(scheme[key], int)
        text = QLineEdit(str(scheme[key]))
        self._grid.addWidget(text, row, 1)
        if not isnum:
            btn = QPushButton()
            btn.setToolTip(translations.TR_EDITOR_SCHEME_PICK_COLOR)
            self.apply_button_style(btn, scheme[key])
            self._grid.addWidget(btn, row, 2)

            self.connect(text, SIGNAL("textChanged(QString)"),
                         lambda: self.apply_button_style(btn, text.text()))
            self.connect(btn, SIGNAL("clicked()"),
                         lambda: self._pick_color(text, btn))
        else:
            self.connect(text, SIGNAL("textChanged(QString)"),
                         self._preview_style)
        self._components[key] = (text, isnum)

    def apply_button_style(self, btn, color_name):
        """Take a button widget and color name and apply as stylesheet."""
        if QColor(color_name).isValid():
            self._modified = True
            btn.setStyleSheet('background:' + color_name)
            self.preview_label1.setStyleSheet('background:' + color_name)
            self.preview_label2.setStyleSheet('color:' + color_name)
            self._preview_style()

    def _pick_color(self, lineedit, btn):
        """Pick a color name using lineedit and button data."""
        color = QColorDialog.getColor(
            QColor(lineedit.text()), self,
            translations.TR_EDITOR_SCHEME_PICK_COLOR)
        if color.isValid():
            lineedit.setText(str(color.name()))
            self.apply_button_style(btn, color.name())

    def _preview_style(self):
        """Live preview style on editor."""
        if self._avoid_on_loading:
            return
        scheme = {}
        keys = sorted(tuple(resources.COLOR_SCHEME.keys()))
        for key in keys:
            isnum = self._components[key][1]
            if isnum:
                num = self._components[key][0].text()
                if num.isdigit():
                    scheme[key] = int(num)
                else:
                    scheme[key] = 0
            else:
                scheme[key] = self._components[key][0].text()
        resources.CUSTOM_SCHEME = scheme
        editorWidget = self._get_editor()
        if editorWidget is not None:
            editorWidget.restyle(editorWidget.lang)
            editorWidget.highlight_current_line()
        return scheme

    def _get_editor(self):
        """Return current Editor."""
        main_container = IDE.get_service("main_container")
        editorWidget = main_container.get_current_editor()
        return editorWidget

    def reject(self):
        """Reject this dialog."""
        if self._modified:
            answer = QMessageBox.No
            answer = QMessageBox.question(
                self, translations.TR_PREFERENCES_EDITOR_SCHEME_DESIGNER,
                (translations.TR_IDE_CONFIRM_EXIT_TITLE + ".\n" +
                 translations.TR_PREFERENCES_GENERAL_CONFIRM_EXIT + "?"),
                QMessageBox.Yes, QMessageBox.No)
            if answer == QMessageBox.No:
                return
        super(EditorSchemeDesigner, self).reject()

    def hideEvent(self, event):
        """Handle Hide event on this dialog."""
        super(EditorSchemeDesigner, self).hideEvent(event)
        resources.CUSTOM_SCHEME = self.original_style
        editorWidget = self._get_editor()
        if editorWidget is not None:
            editorWidget.restyle(editorWidget.lang)

    def _is_valid_scheme_name(self, name):
        """Check if a given name is a valid name for an editor scheme.
        Params:
            name := the name to check
        Returns:
            True if and only if the name is okay to use for a scheme. """
        return name not in ('', 'default')

    def save_scheme(self):
        """Save current scheme."""
        name = self.line_name.text().strip()
        if not self._is_valid_scheme_name(name):
            QMessageBox.information(
                self, translations.TR_PREFERENCES_EDITOR_SCHEME_DESIGNER,
                translations.TR_SCHEME_INVALID_NAME)
            return
        fileName = ('{0}.color'.format(
            file_manager.create_path(resources.EDITOR_SKINS, name)))
        answer = True
        if file_manager.file_exists(fileName):
            answer = QMessageBox.question(
                self, translations.TR_PREFERENCES_EDITOR_SCHEME_DESIGNER,
                translations.TR_WANT_OVERWRITE_FILE + ": {0}?".format(fileName),
                QMessageBox.Yes, QMessageBox.No)

        if answer in (QMessageBox.Yes, True):
            scheme = self._preview_style()
            self.original_style = copy.copy(scheme)
            json_manager.save_editor_skins(fileName, scheme)
            self._modified = False
            self.saved = True
            qsettings = IDE.ninja_settings()
            qsettings.setValue('preferences/editor/scheme', name)
            QMessageBox.information(
                self, translations.TR_PREFERENCES_EDITOR_SCHEME_DESIGNER,
                translations.TR_SCHEME_SAVED + ": {0}.".format(fileName))
            self.close()
        elif answer == QMessageBox.Yes:
            QMessageBox.information(
                self, translations.TR_PREFERENCES_EDITOR_SCHEME_DESIGNER,
                translations.TR_INVALID_FILENAME)
