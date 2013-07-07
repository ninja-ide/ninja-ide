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

import os
import re
try:
    import Queue
except:
    import queue as Queue  # lint:ok

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QDir
from PyQt4.QtCore import QFile
from PyQt4.QtCore import QTextStream
from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL

from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QRadioButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFileDialog

from ninja_ide import resources
from ninja_ide.core import file_manager
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.explorer import explorer_container


class FindInFilesThread(QThread):
    '''
    Emit the signal
    found_pattern(PyQt_PyObject)
    '''

    def find_in_files(self, dir_name, filters, reg_exp, recursive, by_phrase):
        self._cancel = False
        self.recursive = recursive
        self.search_pattern = reg_exp
        self.by_phrase = by_phrase
        self.filters = filters
        self.queue = Queue.Queue()
        self.queue.put(dir_name)
        self.root_dir = dir_name
        #Start!
        self.start()

    def run(self):
        file_filter = QDir.Files | QDir.NoDotAndDotDot | QDir.Readable
        dir_filter = QDir.Dirs | QDir.NoDotAndDotDot | QDir.Readable
        while not self._cancel and not self.queue.empty():
            current_dir = QDir(self.queue.get())
            #Skip not readable dirs!
            if not current_dir.isReadable():
                continue

            #Collect all sub dirs!
            if self.recursive:
                current_sub_dirs = current_dir.entryInfoList(dir_filter)
                for one_dir in current_sub_dirs:
                    self.queue.put(one_dir.absoluteFilePath())

            #all files in sub_dir first apply the filters
            current_files = current_dir.entryInfoList(
                self.filters, file_filter)
            #process all files in current dir!
            for one_file in current_files:
                self._grep_file(one_file.absoluteFilePath(),
                    one_file.fileName())

    def _grep_file(self, file_path, file_name):
        if not self.by_phrase:
            with open(file_path, 'r') as f:
                content = f.read()
            words = [word for word in
                self.search_pattern.pattern().split('|')]
            words.insert(0, True)

            def check_whole_words(result, word):
                return result and content.find(word) != -1
            if not reduce(check_whole_words, words):
                return
        file_object = QFile(file_path)
        if not file_object.open(QFile.ReadOnly):
            return

        stream = QTextStream(file_object)
        lines = []
        line_index = 0
        line = stream.readLine()
        while not self._cancel and not (stream.atEnd() and not line):
            column = self.search_pattern.indexIn(line)
            if column != -1:
                lines.append((line_index, line))
            #take the next line!
            line = stream.readLine()
            line_index += 1
        #emit a signal!
        relative_file_name = file_manager.convert_to_relative(
            self.root_dir, file_path)
        self.emit(SIGNAL("found_pattern(PyQt_PyObject)"),
            (relative_file_name, lines))

    def cancel(self):
        self._cancel = True


class FindInFilesResult(QTreeWidget):

    def __init__(self):
        QTreeWidget.__init__(self)
        self.setHeaderLabels((self.tr('File'), self.tr('Line')))
        self.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.sortByColumn(0, Qt.AscendingOrder)

    def update_result(self, dir_name_root, file_name, items):
        if items:
            root_item = FindInFilesRootItem(self, (file_name, ''),
                dir_name_root)
            root_item.setExpanded(True)
            for line, content in items:
                QTreeWidgetItem(root_item, (content, str(line + 1)))


class FindInFilesRootItem(QTreeWidgetItem):

    def __init__(self, parent, names, dir_name_root):
        QTreeWidgetItem.__init__(self, parent, names)
        self.dir_name_root = dir_name_root


class FindInFilesDialog(QDialog):

    def __init__(self, result_widget, parent):
        QDialog.__init__(self, parent)
        self._find_thread = FindInFilesThread()
        self.setWindowTitle("Find in files")
        self.resize(400, 300)
        #MAIN LAYOUT
        main_vbox = QVBoxLayout(self)

        self.pattern_line_edit = QLineEdit()
        self.dir_name_root = None
        self.user_home = os.path.expanduser('~')
        self.dir_combo = QComboBox()
        self.dir_combo.addItem(self.user_home)
        self.dir_combo.setEditable(True)
        self.open_button = QPushButton(QIcon(resources.IMAGES['find']),
            self.tr("Open"))
        self.filters_line_edit = QLineEdit("*.py")
        self.replace_line = QLineEdit()
        self.replace_line.setEnabled(False)
        self.check_replace = QCheckBox(self.tr("Replace: "))
        self.case_checkbox = QCheckBox(self.tr("C&ase sensitive"))
        self.type_checkbox = QCheckBox(self.tr("R&egular Expression"))
        self.recursive_checkbox = QCheckBox(self.tr("Rec&ursive"))
        self.recursive_checkbox.setCheckState(Qt.Checked)
        self.phrase_radio = QRadioButton(
            self.tr("Search by Phrase (Exact Match)."))
        self.phrase_radio.setChecked(True)
        self.words_radio = QRadioButton(
            self.tr("Search for all the words "
                    "(anywhere in the document, not together)."))
        self.find_button = QPushButton(self.tr("Find!"))
        self.find_button.setMaximumWidth(150)
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.setMaximumWidth(150)
        self.result_widget = result_widget

        hbox = QHBoxLayout()
        hbox.addWidget(self.find_button)
        hbox.addWidget(self.cancel_button)

        #main section
        find_group_box = QGroupBox(self.tr("Main"))
        grid = QGridLayout()
        grid.addWidget(QLabel(self.tr("Text: ")), 0, 0)
        grid.addWidget(self.pattern_line_edit, 0, 1)
        grid.addWidget(QLabel(self.tr("Directory: ")), 1, 0)
        grid.addWidget(self.dir_combo, 1, 1)
        grid.addWidget(self.open_button, 1, 2)
        grid.addWidget(QLabel(self.tr("Filter: ")), 2, 0)
        grid.addWidget(self.filters_line_edit, 2, 1)
        grid.addWidget(self.check_replace, 3, 0)
        grid.addWidget(self.replace_line, 3, 1)

        find_group_box.setLayout(grid)
        #add main section to MAIN LAYOUT
        main_vbox.addWidget(find_group_box)

        #options sections
        options_group_box = QGroupBox(self.tr("Options"))
        gridOptions = QGridLayout()
        gridOptions.addWidget(self.case_checkbox, 0, 0)
        gridOptions.addWidget(self.type_checkbox, 1, 0)
        gridOptions.addWidget(self.recursive_checkbox, 2, 0)
        gridOptions.addWidget(self.phrase_radio, 0, 1)
        gridOptions.addWidget(self.words_radio, 1, 1)

        options_group_box.setLayout(gridOptions)
        #add options sections to MAIN LAYOUT
        main_vbox.addWidget(options_group_box)

        #add buttons to MAIN LAYOUT
        main_vbox.addLayout(hbox)

        #Focus
        self.pattern_line_edit.setFocus()
        self.open_button.setFocusPolicy(Qt.NoFocus)

        #signal
        self.connect(self.open_button, SIGNAL("clicked()"), self._select_dir)
        self.connect(self.find_button, SIGNAL("clicked()"),
            self._find_in_files)
        self.connect(self.cancel_button, SIGNAL("clicked()"),
            self._kill_thread)
        self.connect(self._find_thread, SIGNAL("found_pattern(PyQt_PyObject)"),
            self._found_match)
        self.connect(self._find_thread, SIGNAL("finished()"),
            self._find_thread_finished)
        self.connect(self.type_checkbox, SIGNAL("stateChanged(int)"),
            self._change_radio_enabled)
        self.connect(self.check_replace, SIGNAL("stateChanged(int)"),
            self._replace_activated)
        self.connect(self.words_radio, SIGNAL("clicked(bool)"),
            self._words_radio_pressed)

    def _replace_activated(self):
        self.replace_line.setEnabled(self.check_replace.isChecked())
        self.phrase_radio.setChecked(True)

    def _words_radio_pressed(self, value):
        self.replace_line.setEnabled(not value)
        self.check_replace.setChecked(not value)
        self.words_radio.setChecked(True)

    def _change_radio_enabled(self, val):
        enabled = not self.type_checkbox.isChecked()
        self.phrase_radio.setEnabled(enabled)
        self.words_radio.setEnabled(enabled)

    def show(self, actual_project=None, actual=None):
        self.dir_combo.clear()
        self.dir_name_root = actual_project if \
            actual_project else [self.user_home]
        self.dir_combo.addItems(self.dir_name_root)
        if actual:
            index = self.dir_combo.findText(actual)
            self.dir_combo.setCurrentIndex(index)
        super(FindInFilesDialog, self).show()
        self.pattern_line_edit.setFocus()

    def reject(self):
        self._kill_thread()
        # Crazy hack to avoid circular imports
        self.result_widget.parent().parent().parent().hide()
        super(FindInFilesDialog, self).reject()

    def _find_thread_finished(self):
        self.emit(SIGNAL("finished()"))
        self._find_thread.wait()

    def _select_dir(self):
        dir_name = QFileDialog.getExistingDirectory(self,
            self.tr("Open Directory"),
            self.dir_combo.currentText(),
            QFileDialog.ShowDirsOnly)
        index = self.dir_combo.findText(dir_name)
        if index >= 0:
            self.dir_combo.setCurrentIndex(index)
        else:
            self.dir_combo.insertItem(0, dir_name)
            self.dir_combo.setCurrentIndex(0)

    def _found_match(self, result):
        file_name = result[0]
        items = result[1]
        self.result_widget.update_result(
            self.dir_combo.currentText(), file_name, items)

    def _kill_thread(self):
        if self._find_thread.isRunning():
            self._find_thread.cancel()
        self.accept()

    def _find_in_files(self):
        self.emit(SIGNAL("findStarted()"))
        self._kill_thread()
        self.result_widget.clear()
        pattern = self.pattern_line_edit.text()
        dir_name = self.dir_combo.currentText()

        filters = re.split("[,;]", self.filters_line_edit.text())

        # Version of PyQt API 1
        # filters = self.filters_line_edit.text().split(QRegExp("[,;]"),
        #     QString.SkipEmptyParts)

        #remove the spaces in the words Ex. (" *.foo"--> "*.foo")
        filters = [f.strip() for f in filters]
        case_sensitive = self.case_checkbox.isChecked()
        type_ = QRegExp.RegExp if \
            self.type_checkbox.isChecked() else QRegExp.FixedString
        recursive = self.recursive_checkbox.isChecked()
        by_phrase = True
        if self.phrase_radio.isChecked() or self.type_checkbox.isChecked():
            regExp = QRegExp(pattern, case_sensitive, type_)
        elif self.words_radio.isChecked():
            by_phrase = False
            type_ = QRegExp.RegExp
            pattern = '|'.join(
                [word.strip() for word in pattern.split()])
            regExp = QRegExp(pattern, case_sensitive, type_)
        #save a reference to the root directory where we find
        self.dir_name_root = dir_name
        self._find_thread.find_in_files(dir_name, filters, regExp, recursive,
            by_phrase)


class FindInFilesWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self._main_container = main_container.MainContainer()
        self._explorer_container = explorer_container.ExplorerContainer()
        self._result_widget = FindInFilesResult()
        self._open_find_button = QPushButton(self.tr("Find!"))
        self._stop_button = QPushButton(self.tr("Stop"))
        self._clear_button = QPushButton(self.tr("Clear!"))
        self._replace_button = QPushButton(self.tr("Replace"))
        self._find_widget = FindInFilesDialog(self._result_widget, self)
        self._error_label = QLabel(self.tr("No Results"))
        self._error_label.setVisible(False)
        #Replace Area
        self.replace_widget = QWidget()
        hbox_replace = QHBoxLayout(self.replace_widget)
        hbox_replace.setContentsMargins(0, 0, 0, 0)
        self.lbl_replace = QLabel(self.tr("Replace results with:"))
        self.lbl_replace.setTextFormat(Qt.PlainText)
        self.replace_edit = QLineEdit()
        hbox_replace.addWidget(self.lbl_replace)
        hbox_replace.addWidget(self.replace_edit)
        self.replace_widget.setVisible(False)
        #Main Layout
        main_hbox = QHBoxLayout(self)
        #Result Layout
        tree_vbox = QVBoxLayout()
        tree_vbox.addWidget(self._result_widget)
        tree_vbox.addWidget(self._error_label)
        tree_vbox.addWidget(self.replace_widget)

        main_hbox.addLayout(tree_vbox)
        #Buttons Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self._open_find_button)
        vbox.addWidget(self._stop_button)
        vbox.addWidget(self._clear_button)
        vbox.addSpacerItem(QSpacerItem(0, 50,
            QSizePolicy.Fixed, QSizePolicy.Expanding))
        vbox.addWidget(self._replace_button)
        main_hbox.addLayout(vbox)

        self._open_find_button.setFocus()
        #signals
        self.connect(self._open_find_button, SIGNAL("clicked()"),
            self.open)
        self.connect(self._stop_button, SIGNAL("clicked()"), self._find_stop)
        self.connect(self._clear_button, SIGNAL("clicked()"),
            self._clear_results)
        self.connect(self._result_widget, SIGNAL(
            "itemActivated(QTreeWidgetItem *, int)"), self._go_to)
        self.connect(self._result_widget, SIGNAL(
            "itemClicked(QTreeWidgetItem *, int)"), self._go_to)
        self.connect(self._find_widget, SIGNAL("finished()"),
            self._find_finished)
        self.connect(self._find_widget, SIGNAL("findStarted()"),
            self._find_started)
        self.connect(self._replace_button, SIGNAL("clicked()"),
            self._replace_results)

    def _find_finished(self):
        self._stop_button.setEnabled(False)
        self._open_find_button.setEnabled(True)
        self._error_label.setVisible(False)
        if not self._result_widget.topLevelItemCount():
            self._error_label.setVisible(True)
        if self._find_widget.check_replace.isChecked():
            self.replace_widget.setVisible(True)
            self._replace_button.setEnabled(True)
            self.replace_edit.setText(self._find_widget.replace_line.text())
        else:
            self._replace_button.setEnabled(False)
            self.replace_widget.setVisible(False)
        self._result_widget.setFocus()

    def _find_stop(self):
        self._find_widget._kill_thread()

    def _find_started(self):
        self._open_find_button.setEnabled(False)
        self._stop_button.setEnabled(True)

    def _clear_results(self):
        self._result_widget.clear()

    def _go_to(self, item, val):
        if item.text(1):
            parent = item.parent()
            file_name = parent.text(0)
            lineno = item.text(1)
            root_dir_name = parent.dir_name_root
            file_path = file_manager.create_path(root_dir_name, file_name)
            #open the file and jump_to_line
            self._main_container.open_file(file_path)
            self._main_container.editor_jump_to_line(lineno=int(lineno) - 1)

    def open(self):
        if not self._find_widget.isVisible():
            actual_projects_obj = \
                self._explorer_container.get_opened_projects()
            actual_projects = [p.path for p in actual_projects_obj]
            actual = self._explorer_container.get_actual_project()
            self._find_widget.show(actual_project=actual_projects,
                actual=actual)

    def find_occurrences(self, word):
        self._find_widget.pattern_line_edit.setText(word)
        editorWidget = main_container.MainContainer().get_actual_editor()
        explorerContainer = explorer_container.ExplorerContainer()
        projects_obj = explorerContainer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        project = explorerContainer.get_actual_project()
        for p in projects:
            if file_manager.belongs_to_folder(p, editorWidget.ID):
                project = p
                break
        self._find_widget.dir_combo.clear()
        self._find_widget.dir_combo.addItem(project)
        self._find_widget.case_checkbox.setChecked(True)
        self._find_widget._find_in_files()

    def _replace_results(self):
        result = QMessageBox.question(self, self.tr("Replace Files Contents"),
            self.tr("Are you sure you want to replace the content in "
                    "this files?\n(The change is not reversible)"),
            buttons=QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            for index in range(self._result_widget.topLevelItemCount()):
                parent = self._result_widget.topLevelItem(index)
                root_dir_name = parent.dir_name_root
                file_name = parent.text(0)
                file_path = file_manager.create_path(root_dir_name, file_name)
                try:
                    content = file_manager.read_file_content(file_path)
                    pattern = self._find_widget.pattern_line_edit.text()
                    flags = 0
                    if not self._find_widget.case_checkbox.isChecked():
                        flags |= re.IGNORECASE
                    if self._find_widget.type_checkbox.isChecked():
                        pattern = r'\b%s\b' % pattern

                    new_content = re.sub(pattern,
                        self._find_widget.replace_line.text(),
                        content, flags=flags)
                    file_manager.store_file_content(file_path,
                        new_content, False)
                except:
                    print('File: %s content, could not be replaced' %
                          file_path)
