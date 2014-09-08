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

from getpass import getuser

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager


class ThemeEditor(QDialog):
    """ThemeEditor Scheme Designer Class Widget"""

    def __init__(self, parent):
        super(ThemeEditor, self).__init__(parent, Qt.Dialog)
        vbox = QVBoxLayout(self)

        hbox = QHBoxLayout()
        self.line_name = QLineEdit()
        self.btn_save = QPushButton(translations.TR_SAVE)
        self.line_name.setPlaceholderText(getuser().capitalize() + "s_theme")
        hbox.addWidget(self.line_name)
        hbox.addWidget(self.btn_save)

        self.edit_qss = QPlainTextEdit()
        css = 'QPlainTextEdit {color: %s; background-color: %s;' \
            'selection-color: %s; selection-background-color: %s;}' \
            % (resources.CUSTOM_SCHEME.get(
                'editor-text', resources.COLOR_SCHEME['Default']),
                resources.CUSTOM_SCHEME.get(
                    'EditorBackground',
                    resources.COLOR_SCHEME['EditorBackground']),
                resources.CUSTOM_SCHEME.get(
                    'EditorSelectionColor',
                    resources.COLOR_SCHEME['EditorSelectionColor']),
                resources.CUSTOM_SCHEME.get(
                    'EditorSelectionBackground',
                    resources.COLOR_SCHEME['EditorSelectionBackground']))
        self.edit_qss.setStyleSheet(css)

        self.btn_apply = QPushButton(self.tr("Apply Style Sheet"))
        hbox2 = QHBoxLayout()
        hbox2.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Expanding,
                            QSizePolicy.Fixed))
        hbox2.addWidget(self.btn_apply)
        hbox2.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Expanding,
                            QSizePolicy.Fixed))

        vbox.addWidget(self.edit_qss)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)

        self.connect(self.btn_apply, SIGNAL("clicked()"), self.apply_stylesheet)
        self.connect(self.btn_save, SIGNAL("clicked()"), self.save_stylesheet)

    def apply_stylesheet(self):
        qss = self.edit_qss.toPlainText()
        QApplication.instance().setStyleSheet(qss)

    def save_stylesheet(self):
        try:
            file_name = "%s.qss" % self.line_name.text()
            if not self._is_valid_scheme_name(file_name):
                QMessageBox.information(
                    self, translations.TR_PREFERENCES_THEME,
                    translations.TR_SCHEME_INVALID_NAME)
            file_name = ('{0}.qss'.format(
                file_manager.create_path(
                    resources.NINJA_THEME_DOWNLOAD, file_name)))
            content = self.edit_qss.toPlainText()
            answer = True
            if file_manager.file_exists(file_name):
                answer = QMessageBox.question(
                    self, translations.TR_PREFERENCES_THEME,
                    translations.TR_WANT_OVERWRITE_FILE + ": {0}?".format(
                        file_name),
                    QMessageBox.Yes, QMessageBox.No)

            if answer in (QMessageBox.Yes, True):
                self.apply_stylesheet()
                file_manager.store_file_content(
                    file_name, content, newFile=True)
                self.close()
        except file_manager.NinjaFileExistsException as ex:
            QMessageBox.information(
                self, self.tr("File Already Exists"),
                (self.tr("Invalid File Name: the file '%s' already exists.") %
                    ex.filename))

    def _is_valid_scheme_name(self, name):
        """Check if a given name is a valid name for an editor scheme.
        Params:
            name := the name to check
        Returns:
            True if and only if the name is okay to use for a scheme. """
        return name not in ('', 'Default')