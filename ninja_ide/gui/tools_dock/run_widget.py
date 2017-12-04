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
import re

from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMenu,
    QToolButton
)
from PyQt5.QtGui import (
    QTextCursor,
    QTextCharFormat,
    QColor,
    QBrush
)
from PyQt5.QtCore import (
    Qt,
    QProcess,
    QTime,
    QProcessEnvironment,
    QFile
)

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide.gui.theme import NTheme


class RunWidget(QWidget):

    """Widget that show the execution output in the Tool Dock."""

    def __init__(self):
        super(RunWidget, self).__init__()

        vbox = QVBoxLayout(self)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.output = OutputWidget(self)
        # Button Widgets
        self._btn_zoom_in = QToolButton()
        self._btn_zoom_in.setIcon(
            ui_tools.colored_icon(
                ':img/plus', NTheme.get_color('IconBaseColor')))
        self._btn_zoom_in.clicked.connect(self.output.zoomIn)
        self._btn_zoom_out = QToolButton()
        self._btn_zoom_out.setIcon(
            ui_tools.colored_icon(
                ':img/minus', NTheme.get_color('IconBaseColor')))
        self._btn_zoom_out.clicked.connect(self.output.zoomOut)
        self._btn_clean = QToolButton()
        self._btn_clean.setIcon(
            ui_tools.colored_icon(
                ':img/clean', NTheme.get_color('IconBaseColor')))
        self._btn_stop = QToolButton()
        self._btn_stop.setIcon(ui_tools.colored_icon(':img/stop', '#d74044'))
        self._btn_stop.clicked.connect(self.kill_process)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(5, 0, 0, 0)
        self.input = QLineEdit()
        self.lblInput = QLabel(self.tr("Input:  "))
        self.input.hide()
        self.lblInput.hide()
        vbox.addWidget(self.output)
        hbox.addWidget(self.lblInput)
        hbox.addWidget(self.input)
        vbox.addLayout(hbox)

        self.set_font(settings.FONT)

        # Process
        self.currentProcess = None
        self.__preScriptExecuted = False
        self._proc = QProcess(self)
        self._preExecScriptProc = QProcess(self)
        self._postExecScriptProc = QProcess(self)
        # Connections
        self._proc.readyReadStandardOutput.connect(self.output.refresh_output)
        self._proc.readyReadStandardError.connect(self.output.refresh_error)
        self._proc.finished.connect(self.finish_execution)
        self._proc.error.connect(self.process_error)
        self.input.returnPressed.connect(self.insert_input)

        # self.connect(self._preExecScriptProc,
        #             SIGNAL("finished(int, QProcess::ExitStatus)"),
        #             self.__main_execution)
        # self.connect(self._preExecScriptProc,
        #             SIGNAL("readyReadStandardOutput()"),
        #             self.output.refresh_output)
        # self.connect(self._preExecScriptProc,
        #             SIGNAL("readyReadStandardError()"),
        #             self.output.refresh_error)
        # self.connect(self._postExecScriptProc,
        #             SIGNAL("finished(int, QProcess::ExitStatus)"),
        #             self.__post_execution_message)
        # self.connect(self._postExecScriptProc,
        #             SIGNAL("readyReadStandardOutput()"),
        #             self.output.refresh_output)
        # self.connect(self._postExecScriptProc,
        #             SIGNAL("readyReadStandardError()"),
        #             self.output.refresh_error)

    def button_widgets(self):
        return [self._btn_clean, self._btn_zoom_in, self._btn_zoom_out, self._btn_stop]

    def set_font(self, font):
        """Set the font for the output widget"""
        # f = self.output.font()
        # f.setPointSize(10   )
        # self.output.document().setDefaultFont(f)
        # self.output.plain_format.setFont(f)
        # self.output.error_format.setFont(f)
        pass

    def process_error(self, error):
        """Listen to the error signals from the running process"""

        self.lblInput.hide()
        self.input.hide()
        self._proc.kill()
        format_ = QTextCharFormat()
        format_.setAnchor(True)
        font = settings.FONT
        # format_.setFont(font)
        format_.setForeground(QBrush(QColor(resources.CUSTOM_SCHEME.get(
            "ErrorUnderline", resources.COLOR_SCHEME["ErrorUnderline"]))))
        if error == 0:
            # self.output.textCursor().insertText(self.tr('Failed to start'),
            #
            # pass                                 format_)

            print('ERROR')
        else:
            print('ERRoR2')
            # self.output.textCursor().insertText(
            #    (self.tr('Error during execution, QProcess error: %d') % error),
            #    format_)

    def finish_execution(self, exitCode, exitStatus):
        """Print a message and hide the input line when the execution ends"""

        self.lblInput.hide()
        self.input.hide()
        format_ = QTextCharFormat()
        format_.setAnchor(True)
        font = settings.FONT
        # format_.setFont(font)
        # self.output.textCursor().insertText('\n\n')
        if exitStatus == QProcess.NormalExit:
            format_.setForeground(QBrush(QColor(resources.CUSTOM_SCHEME.get(
                "Keyword", resources.COLOR_SCHEME["Keyword"]))))
            # self.output.appendPlainText('Execution Successful!')
            self.output.textCursor().insertText(
                self.tr("Execution Successful!"), format_)
            # self.output.append_message('Execution Successful!', format_)
        else:
            format_.setForeground(
                QBrush(QColor(
                    resources.CUSTOM_SCHEME.get(
                        "ErrorUnderline",
                        resources.COLOR_SCHEME["ErrorUnderline"]))))
            self.output.textCursor().insertText(
                self.tr("Execution Interrupted"), format_)
        self.__post_execution()

    def insert_input(self):
        """Take the user input and send it to the process"""
        text = self.input.text() + '\n'
        self._proc.writeData(text.encode())
        # self.output.textCursor().insertText("Input: " + text,
        #                                    self.output.plain_format)
        # self.output.append_message(text)
        self.input.clear()

    def display_name(self):
        return 'Output'

    def start_process(self, fileName, pythonExec=False, PYTHONPATH=None,
                      programParams='', preExec='', postExec=''):
        """Prepare the output widget and start the process"""
        print('start process')
        self.lblInput.show()
        self.input.show()
        self.fileName = fileName
        self.pythonExec = pythonExec  # FIXME, this is python interpreter
        self.programParams = programParams
        self.preExec = preExec
        self.postExec = postExec
        self.PYTHONPATH = PYTHONPATH

        self.__pre_execution()

    def __main_execution(self):
        """Execute the project"""
        self.output.setCurrentCharFormat(self.output.plain_format)
        self.output.clear()
        message = ''
        if self.__preScriptExecuted:
            self.__preScriptExecuted = False
            message = self.tr(
                "Pre Execution Script Successfully executed.\n\n")
        self.output.append_message(
            QTime.currentTime().toString('hh:mm:ss') + ': Running: ' +
            self.fileName + '\n')
        # self.output.setPlainText(
        #    QTime.currentTime().toString('hh:mm:ss') + ': Running: ' +
        #    self.fileName + '\n')
        # self.output.setPlainText(message + 'Running: %s (%s)\n' %
        #                         (self.fileName, time.ctime()))
        # self.output.setPlainText(
            # QTime.currentTime().toString('hh:mm:ss') + ': Running: ' +
            # self.fileName + '\n')
        # self.output.moveCursor(QTextCursor.Down)
        # self.output.moveCursor(QTextCursor.Down)
        # self.output.moveCursor(QTextCursor.Down)

        if not self.pythonExec:
            self.pythonExec = settings.PYTHON_EXEC
        # Change the working directory to the fileName dir
        file_directory = file_manager.get_folder(self.fileName)
        self._proc.setWorkingDirectory(file_directory)
        # Force python to unbuffer stdin and stdout
        options = ['-u'] + settings.EXECUTION_OPTIONS.split()
        self.currentProcess = self._proc

        # env = QProcessEnvironment()
        # system_environemnt = self._proc.systemEnvironment()
        # for e in system_environemnt:
        #    key, value = e.split('=', 1)
        #    env.insert(key, value)
        # if self.PYTHONPATH:
        #    envpaths = [path for path in self.PYTHONPATH.splitlines()]
        #    for path in envpaths:
        #        env.insert('PYTHONPATH', path)
        # env.insert('PYTHONIOENCODING', 'utf-8')
        # env.insert('PYTHONPATH', ':'.join(sys.path))
        # self._proc.setProcessEnvironment(env)

        self._proc.start(self.pythonExec, options + [self.fileName] +
                         [p.strip()
                          for p in self.programParams.split(',') if p])

    def __pre_execution(self):
        """Execute a script before executing the project"""

        filePreExec = QFile(self.preExec)
        if filePreExec.exists() and \
                bool(QFile.ExeUser & filePreExec.permissions()):
            ext = file_manager.get_file_extension(self.preExec)
            if not self.pythonExec:
                self.pythonExec = settings.PYTHON_PATH
            self.currentProcess = self._preExecScriptProc
            self.__preScriptExecuted = True
            if ext == 'py':
                self._preExecScriptProc.start(self.pythonExec, [self.preExec])
            else:
                self._preExecScriptProc.start(self.preExec)
        else:
            self.__main_execution()

    def __post_execution(self):
        """Execute a script after executing the project."""
        filePostExec = QFile(self.postExec)
        if filePostExec.exists() and \
                bool(QFile.ExeUser & filePostExec.permissions()):
            ext = file_manager.get_file_extension(self.postExec)
            if not self.pythonExec:
                self.pythonExec = settings.PYTHON_PATH
            self.currentProcess = self._postExecScriptProc
            if ext == 'py':
                self._postExecScriptProc.start(self.pythonExec,
                                               [self.postExec])
            else:
                self._postExecScriptProc.start(self.postExec)

    def __post_execution_message(self):
        """Print post execution message"""

        # self.output.textCursor().insertText('\n\n')
        format_ = QTextCharFormat()
        format_.setAnchor(True)
        format_.setForeground(Qt.green)
        # self.output.textCursor().insertText(
        #    self.tr("Post Execution Script Successfully executed."), format_)

    def kill_process(self):
        """Kill the running process"""

        self._proc.kill()


class OutputWidget(QPlainTextEdit):

    """Widget to handle the output of the running process"""

    def __init__(self, parent):
        super(OutputWidget, self).__init__(parent)
        self._parent = parent

        self.setReadOnly(True)
        self.setFrameShape(0)
        self.setUndoRedoEnabled(False)
        # Traceback pattern
        self.patLink = re.compile(r'(\s)*File "(.*?)", line \d.+')
        # Formats
        font = settings.FONT
        self.setFont(font)
        self.plain_format = QTextCharFormat()
        # self.plain_format.setFont(font)
        # self.plain_format.setForeground(
        #    QBrush(QColor(resources.CUSTOM_SCHEME.get(
        #        "Default", resources.COLOR_SCHEME["Default"]))))
        self.error_format = QTextCharFormat()
        # self.error_format.setFont(font)
        self.error_format.setAnchor(True)
        # self.error_format.setForeground(QColor(resources.CUSTOM_SCHEME.get(
        #    "Pep8Underline", resources.COLOR_SCHEME["Pep8Underline"])))
        # self.error_format.setBackground(QColor(resources.CUSTOM_SCHEME.get(
        #    "ErrorUnderline", resources.COLOR_SCHEME["ErrorUnderline"])))
        self.error_format.setToolTip(self.tr("Click to show the source"))
        self.error_format2 = QTextCharFormat()
        self.error_format2.setAnchor(True)
        # self.error_format2.setFont(font)
        # self.error_format2.setForeground(
        #    QBrush(
        #        QColor(resources.get_color('ErrorUnderline'))))

        self.blockCountChanged[int].connect(
            lambda: self.moveCursor(QTextCursor.End))

        # Style
        palette = self.palette()
        palette.setColor(palette.Base, QColor(resources.get_color('EditorBackground')))
        palette.setColor(palette.Text, QColor(resources.get_color('Default')))
        self.setPalette(palette)
        # css = 'QPlainTextEdit {color: %s; background-color: %s;' \
        #    'selection-color: %s; selection-background-color: %s;}' \
        #    % (resources.CUSTOM_SCHEME.get('editor-text',
        #       resources.COLOR_SCHEME['Default']),
        #       resources.CUSTOM_SCHEME.get('EditorBackground',
        #       resources.COLOR_SCHEME['EditorBackground']),
        #       resources.CUSTOM_SCHEME.get('EditorSelectionColor',
        #       resources.COLOR_SCHEME['EditorSelectionColor']),
        #       resources.CUSTOM_SCHEME.get('EditorSelectionBackground',
        #       resources.COLOR_SCHEME['EditorSelectionBackground']))
        # self.setStyleSheet(css)

    def mousePressEvent(self, event):
        """
        When the execution fail, allow to press the links in the traceback,
        to go to the line when the error occur.
        """
        QPlainTextEdit.mousePressEvent(self, event)
        self.go_to_error(event)

    def refresh_output(self):
        """Read the output buffer from the process and append the text."""
        # We should decode the bytes!
        currentProcess = self._parent.currentProcess
        text = currentProcess.readAllStandardOutput().data().decode('utf8')
        self.textCursor().insertText(text)
        # self.append_message(text)

    def refresh_error(self):
        """Read the error buffer from the process and append the text."""
        # We should decode the bytes!
        currentProcess = self._parent.currentProcess
        text = currentProcess.readAllStandardError().data().decode('utf8')
        for txt in text.splitlines():
            if self.patLink.match(txt):
                self.append_message(txt, self.error_format)
            else:
                self.append_message(txt, self.error_format2)

    def go_to_error(self, event):
        """Resolve the link and take the user to the error line."""
        cursor = self.cursorForPosition(event.pos())
        text = cursor.block().text()
        if self.patLink.match(text):
            file_path, lineno = self._parse_traceback(text)
            main_container = IDE.get_service('main_container')
            if main_container:
                main_container.open_file(file_path, line=int(lineno) - 1)

    def _parse_traceback(self, text):
        """
        Parse a line of python traceback and returns
        a tuple with (file_name, lineno)
        """
        file_word_index = text.find('File')
        comma_min_index = text.find(',')
        comma_max_index = text.rfind(',')
        file_name = text[file_word_index + 6:comma_min_index - 1]
        lineno = text[comma_min_index + 7:comma_max_index]
        return (file_name, lineno)

    def contextMenuEvent(self, event):
        """Show a context menu for the Plain Text widget."""
        popup_menu = self.createStandardContextMenu()

        menuOutput = QMenu(self.tr("Output"))
        cleanAction = menuOutput.addAction(self.tr("Clean"))
        popup_menu.insertSeparator(popup_menu.actions()[0])
        popup_menu.insertMenu(popup_menu.actions()[0], menuOutput)

        # This is a hack because if we leave the widget text empty
        # it throw a violent segmentation fault in start_process
        # self.connect(cleanAction, SIGNAL("triggered()"),
        #             lambda: self.setPlainText('\n\n'))

        popup_menu.exec_(event.globalPos())

    def append_message(self, text, frmt=None):
        cursor = self.textCursor()
        if frmt is None:
            frmt = self.plain_format
        cursor.insertText(text + '\n')
