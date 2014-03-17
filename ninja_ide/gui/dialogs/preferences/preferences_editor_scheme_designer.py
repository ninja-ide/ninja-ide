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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QColorDialog
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import json_manager
from ninja_ide.gui.ide import IDE


class EditorSchemeDesigner(QDialog):

    def __init__(self, scheme, parent):
        super(EditorSchemeDesigner, self).__init__(parent, Qt.Dialog)
        self.original_style = copy.copy(resources.CUSTOM_SCHEME)
        self._avoid_on_loading = True
        self.saved = False
        self._components = {}

        self.setWindowTitle(translations.TR_PREFERENCES_EDITOR_SCHEME_DESIGNER)
        self.setMinimumWidth(500)
        vbox = QVBoxLayout(self)
        scrollArea = QScrollArea()
        vbox.addWidget(scrollArea)

        frame = QFrame()
        vbox = QVBoxLayout()
        self._grid = QGridLayout()

        self._grid.addWidget(QLabel('Scheme Name:'), 0, 0)
        self.line_name = QLineEdit()
        self._grid.addWidget(self.line_name, 0, 1)
        btnSave = QPushButton('Save Scheme')
        self._grid.addWidget(btnSave, 0, 2)
        self._grid.addWidget(QLabel('Properties:'), 1, 0)
        self.connect(btnSave, SIGNAL("clicked()"), self.save_scheme)

        keys = sorted(list(resources.COLOR_SCHEME.keys()))
        for key in keys:
            self.add_item(key, scheme)

        vbox.addLayout(self._grid)
        frame.setLayout(vbox)
        scrollArea.setWidget(frame)
        self._avoid_on_loading = False
        self._modified = False

    def add_item(self, key, scheme):
        row = self._grid.rowCount()
        self._grid.addWidget(QLabel(key), row, 0)
        isnum = isinstance(scheme[key], int)
        text = QLineEdit(str(scheme[key]))
        self._grid.addWidget(text, row, 1)
        if not isnum:
            btn = QPushButton(translations.TR_EDITOR_SCHEME_PICK_COLOR)
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
        if QColor(color_name).isValid():
            self._modified = True
            btn.setAutoFillBackground(True)
            style = ('background: %s; border-radius: 5px; '
                     'padding: 5px;' % color_name)
            btn.setStyleSheet(style)
            self._preview_style()

    def _pick_color(self, lineedit, btn):
        color = QColorDialog.getColor(QColor(lineedit.text()),
            self, self.tr("Choose Color for: "))
        if color.isValid():
            lineedit.setText(str(color.name()))
            self.apply_button_style(btn, color.name())

    def _preview_style(self):
        if self._avoid_on_loading:
            return
        scheme = {}
        keys = sorted(list(resources.COLOR_SCHEME.keys()))
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
        main_container = IDE.get_service("main_container")
        editorWidget = main_container.get_current_editor()
        return editorWidget

    def reject(self):
        if self._modified:
            answer = QMessageBox.No
            answer = QMessageBox.question(self,
                self.tr("Scheme Modified"),
                self.tr("Changes has not been saved, exit anyway?"),
                QMessageBox.Yes, QMessageBox.No)
            if answer == QMessageBox.No:
                return
        super(EditorSchemeDesigner, self).reject()

    def hideEvent(self, event):
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
            True if and only if the name is okay to use for a scheme

        """
        return name not in ('', 'default')

    def save_scheme(self):
        name = self.line_name.text().strip()
        if not self._is_valid_scheme_name(name):
            QMessageBox.information(self, self.tr("Invalid Scheme Name"),
                self.tr("The scheme name you have chosen is invalid.\nPlease "
                    "pick a different name."))
            return
        fileName = ('{0}.color'.format(
            file_manager.create_path(resources.EDITOR_SKINS, name)))
        answer = True
        if file_manager.file_exists(fileName):
            answer = QMessageBox.question(self,
                self.tr("Scheme already exists"),
                (self.tr("Do you want to override the file: %s?") % fileName),
                QMessageBox.Yes, QMessageBox.No)

        if answer in (QMessageBox.Yes, True):
            scheme = self._preview_style()
            self.original_style = copy.copy(scheme)
            json_manager.save_editor_skins(fileName, scheme)
            self._modified = False
            self.saved = True
            qsettings = IDE.ninja_settings()
            qsettings.setValue('preferences/editor/scheme', name)
            QMessageBox.information(self, self.tr("Scheme Saved"),
                    (self.tr("The scheme has been saved at: %s.") % fileName))
            self.close()
        elif answer == QMessageBox.Yes:
            QMessageBox.information(self, self.tr("Scheme Not Saved"),
                self.tr("The name probably is invalid."))