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
    QBrush,
    QFont
)
from PyQt5.QtCore import (
    Qt,
    QProcess,
    QTime,
    QObject,
    QProcessEnvironment,
    QFile,
    pyqtSlot,
    pyqtSignal,
    QTimer,
)

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide.tools.logger import NinjaLogger

# Logger
logger = NinjaLogger(__name__)


class RunProcess(QObject):

    stdoutAvailable = pyqtSignal("QString")
    errorAvailable = pyqtSignal("QString")
    processStarted = pyqtSignal("QString")
    processFinished = pyqtSignal("QString", "QString")

    @property
    def program(self):
        """Returns the current program that is running"""

        prog = self._current_process.program()
        args = " ".join(self._current_process.arguments())
        return prog + " " + args

    @property
    def python_exec(self):
        pexec = self._python_exec
        if not pexec:
            pexec = settings.PYTHON_EXEC
        return pexec

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_process = None
        # Process for execute script before project
        self._pre_exec_process = QProcess(self)
        self._pre_exec_process.started.connect(
            self._on_process_started)
        self._pre_exec_process.finished.connect(self.__main_execution)
        self._pre_exec_process.finished.connect(self._on_process_finished)
        self._pre_exec_process.errorOccurred.connect(self._on_error_occurred)
        self._pre_exec_process.readyReadStandardError.connect(
            self._error_available)
        self._pre_exec_process.readyReadStandardOutput.connect(
            self._result_available)
        # Process for execute script after project
        self._post_exec_process = QProcess(self)
        self._post_exec_process.started.connect(
            self._on_process_started)
        self._post_exec_process.finished.connect(self._on_process_finished)
        self._post_exec_process.errorOccurred.connect(self._on_error_occurred)
        self._post_exec_process.readyReadStandardError.connect(
            self._error_available)
        # Process for execute project
        self._process = QProcess(self)
        self._process.started.connect(self._on_process_started)
        self._process.finished.connect(self._on_process_finished)
        self._process.errorOccurred.connect(self._on_error_occurred)
        self._process.readyReadStandardOutput.connect(self._result_available)
        self._process.readyReadStandardError.connect(self._error_available)
        self._process.finished.connect(self.__post_execution)

    @pyqtSlot(QProcess.ProcessError)
    def _on_error_occurred(self, error):
        if error == QProcess.FailedToStart:
            # FIXME: acortar program
            message = ("Failed to start. Maybe {} is missing or you "
                       "have insufficient permissions").format(
                self.program)
        else:
            message = "Error during execution, QProcess error: '%d'" % error
        self.errorAvailable.emit(self.__add_current_time(message))
        self.kill_process()
        logger.error('Error ocurred {}'.format(error))

    @pyqtSlot(int, QProcess.ExitStatus)
    def _on_process_finished(self, code, status):
        frmt = 'normal'
        if status == QProcess.NormalExit == code:
            message = "The process exited normally with code {}".format(code)
        else:
            message = "Execution Interrupted! '{}'".format(self.program)
            frmt = 'error'
        self.processFinished.emit(self.__add_current_time(message), frmt)
        logger.debug('Process finished with {}, {}'.format(code, status))

    def __add_current_time(self, text):
        """Add current time into text"""
        current_time_str = QTime.currentTime().toString('hh:mm:ss')
        message = current_time_str + " :: " + text
        return message

    @pyqtSlot()
    def _on_process_started(self):
        message = self.__add_current_time("Running: " + self.program)
        self.processStarted.emit(message)

    @pyqtSlot()
    def _error_available(self):
        output = self._current_process.readAllStandardError().data().decode()
        for line_text in output.splitlines():
            self.errorAvailable.emit(line_text)

    @pyqtSlot()
    def _result_available(self):
        output = self._current_process.readAllStandardOutput().data().decode()
        self.stdoutAvailable.emit(output.strip())

    def start_process(self, filename, text, python_exec, pre_exec_script,
                      post_exec_script, program_params):
        self._python_exec = python_exec
        self._pre_exec_script = pre_exec_script
        self._post_exec_script = post_exec_script
        if text:
            self.__execute_text_code(text)
        else:
            self._filename = filename
            self._params = program_params
            self.__pre_execution()

    def __execute_text_code(self, code):
        self._current_process = self._process
        self._process.setProgram(self.python_exec)
        self._process.setArguments(["-c"] + [code])
        self._process.start()

    def __pre_execution(self):
        """Execute a script before executing the project"""
        self._current_process = self._pre_exec_process
        script = self._pre_exec_script
        file_pre_exec = QFile(script)
        # FIXME: el script solo existe cuando ejecuto ninja desde la carpeta
        if file_pre_exec.exists():
            ext = file_manager.get_file_extension(script)
            args = []
            if ext == "py":
                program = self.python_exec
                # -u: Force python to unbuffer stding ad stdout
                args = ['-u'] + [script]
            elif ext == "sh":
                program = "bash"
                args = [script]
            else:
                program = script
            self._pre_exec_process.setProgram(program)
            self._pre_exec_process.setArguments(args)
            self._pre_exec_process.start()
        else:
            self.__main_execution()

    def __post_execution(self):
        """Execute a script after executing the project."""
        self._current_process = self._post_exec_process
        script = self._post_exec_script
        file_post_exec = QFile(script)
        if file_post_exec.exists():
            ext = file_manager.get_file_extension(script)
            args = []
            if ext == "py":
                program = self.python_exec
                # -u: Force python to unbuffer stding ad stdout
                args = ['-u'] + [script]
            elif ext == "sh":
                program = "bash"
                args = [script]
            else:
                program = script
            self._post_exec_process.setProgram(program)
            self._post_exec_process.setArguments(args)
            self._post_exec_process.start()

    def __main_execution(self):
        self._current_process = self._process
        file_directory = file_manager.get_folder(self._filename)
        self._process.setWorkingDirectory(file_directory)
        # Force python to unbuffer stding ad stdout
        options = ['-u'] + settings.EXECUTION_OPTIONS.split()
        # Set python exec and arguments
        program_params = [param.strip()
                          for param in self._params.split(',') if param]
        self._process.setProgram(self.python_exec)
        self._process.setArguments(options + [self._filename] + program_params)
        environment = QProcessEnvironment()
        system_environemnt = self._process.systemEnvironment()
        for env in system_environemnt:
            key, value = env.split('=', 1)
            environment.insert(key, value)
        self._process.setProcessEnvironment(environment)
        # Start!
        self._process.start()

    def write(self, data):
        self._process.writeData(data)
        self._process.writeData(b'\n')

    def kill_process(self):
        self._current_process.kill()


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
        # self._btn_zoom_in.setIcon(
            # ui_tools.colored_icon(
                # ':img/plus', theme.get_color('IconBaseColor')))
        self._btn_zoom_in.setToolTip('Zoom In')
        self._btn_zoom_in.clicked.connect(self.output.zoomIn)
        self._btn_zoom_out = QToolButton()
        # self._btn_zoom_out.setIcon(
            # ui_tools.colored_icon(
                # ':img/minus', theme.get_color('IconBaseColor')))
        self._btn_zoom_out.setToolTip('Zoom Out')
        self._btn_zoom_out.clicked.connect(self.output.zoomOut)
        self._btn_clean = QToolButton()
        # self._btn_clean.setIcon(
            # ui_tools.colored_icon(
                # ':img/clean', theme.get_color('IconBaseColor')))
        self._btn_clean.setToolTip('Clear Output')
        self._btn_stop = QToolButton()
        self._btn_stop.setIcon(ui_tools.colored_icon(':img/stop', '#d74044'))
        self._btn_stop.setToolTip('Stop Running Program')
        self._btn_stop.clicked.connect(self.kill_process)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(5, 0, 0, 0)
        self.input = QLineEdit()
        self.label_input = QLabel(self.tr("Input:  "))
        self.input.hide()
        self.label_input.hide()
        vbox.addWidget(self.output)
        hbox.addWidget(self.label_input)
        hbox.addWidget(self.input)
        vbox.addLayout(hbox)

        self.set_font(settings.FONT)

        # Process
        self._process = RunProcess(self)
        self._process.processStarted.connect(self._on_process_started)
        self._process.processFinished.connect(self._on_process_finished)
        self._process.stdoutAvailable.connect(self._on_stdout_available)
        self._process.errorAvailable.connect(self._on_error_available)
        self.input.returnPressed.connect(self.insert_input)
        # self.currentProcess = None
        # self.__preScriptExecuted = False
        # self._proc = QProcess(self)
        # self._preExecScriptProc = QProcess(self)
        # self._postExecScriptProc = QProcess(self)
        # Connections
        # self._proc.readyReadStandardOutput.connect(self.output.refresh_output)
        # self._proc.readyReadStandardError.connect(self.output.refresh_error)
        # self._proc.finished.connect(self.finish_execution)
        # self._proc.error.connect(self.process_error)
        # self.input.returnPressed.connect(self.insert_input)

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

    def kill_process(self):
        self._process.kill_process()

    @pyqtSlot('QString')
    def _on_error_available(self, error_msg):
        if self.output.patLink.match(error_msg):
            frmt = 'error2'
        else:
            frmt = 'error'
        self.output.append_text(error_msg, text_format=frmt)
        self.input.hide()
        self.label_input.hide()

    @pyqtSlot('QString', 'QString')
    def _on_process_finished(self, msg, status):
        self.output.append_text(msg, text_format=status)
        self.label_input.hide()
        self.input.hide()

    @pyqtSlot('QString')
    def _on_process_started(self, message):
        self.output.append_text(message, text_format='normal')

    @pyqtSlot('QString')
    def _on_stdout_available(self, data):
        self.output.append_text(data, text_format='plain')

    def display_name(self):
        return 'Output'

    def button_widgets(self):
        return (
            self._btn_clean,
            self._btn_zoom_in,
            self._btn_zoom_out,
            self._btn_stop
        )

    def insert_input(self):
        """Take the user inut and send it to the process"""

        data = self.input.text()
        self._process.write(data.encode())
        self.output.append_message(data)  # FIXME
        self.input.clear()

    def set_font(self, font):
        """Set the font for the output widget"""
        # f = self.output.font()
        # f.setPointSize(10   )
        # self.output.document().setDefaultFont(f)
        # self.output.plain_format.setFont(f)
        # self.output.error_format.setFont(f)
        pass

    def start_process(self, filename, text, python_exec, pre_exec_script,
                      post_exec_script, program_params):
        self.label_input.show()
        self.input.show()
        self._process.start_process(
            filename,
            text,
            python_exec,
            pre_exec_script,
            post_exec_script,
            program_params
        )

    '''def process_error(self, error):
        """Listen to the error signals from the running process"""

        self.label_input.hide()
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

        self.label_input.hide()
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
        self.label_input.show()
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

        self._proc.kill()'''


class OutputWidget(QPlainTextEdit):

    """Widget to handle the output of the running process"""

    def __init__(self, parent):
        super(OutputWidget, self).__init__(parent)
        self._parent = parent

        self.setWordWrapMode(0)
        self.setReadOnly(True)
        self.setMouseTracking(True)
        self.setFrameShape(0)
        self.setUndoRedoEnabled(False)
        # Traceback pattern
        self.patLink = re.compile(r'(\s)*File "(.*?)", line \d.+')

        font = QFont(settings.FONT)
        font.setWeight(QFont.Light)
        font.setPixelSize(13)
        self.setFont(font)
        # Formats
        plain_format = QTextCharFormat()
        normal_format = QTextCharFormat()
        normal_format.setForeground(Qt.white)
        error_format = QTextCharFormat()
        error_format.setForeground(QColor('#ff6c6c'))
        error_format2 = QTextCharFormat()
        error_format2.setToolTip('Click to show the source')
        error_format2.setUnderlineStyle(QTextCharFormat.DashUnderline)
        error_format2.setForeground(QColor('#ff6c6c'))
        error_format2.setUnderlineColor(QColor('#ff6c6c'))

        self._text_formats = {
            'normal': normal_format,
            'plain': plain_format,
            'error': error_format,
            'error2': error_format2
        }

        self.blockCountChanged[int].connect(
            lambda: self.moveCursor(QTextCursor.End))

        # Style
        palette = self.palette()
        palette.setColor(
            palette.Base, QColor(resources.get_color('EditorBackground')))
        self.setPalette(palette)

    def mousePressEvent(self, event):
        """
        When the execution fail, allow to press the links in the traceback,
        to go to the line when the error occur.
        """
        QPlainTextEdit.mousePressEvent(self, event)
        self.go_to_error(event)

    def mouseMoveEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        text = cursor.block().text()
        if text:
            if self.patLink.match(text):
                self.viewport().setCursor(Qt.PointingHandCursor)
            else:
                self.viewport().setCursor(Qt.IBeamCursor)
        QPlainTextEdit.mouseMoveEvent(self, event)

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

    # def contextMenuEvent(self, event):
    #    """Show a context menu for the Plain Text widget."""
    #    popup_menu = self.createStandardContextMenu()

    #    menuOutput = QMenu(self.tr("Output"))
    #    cleanAction = menuOutput.addAction(self.tr("Clean"))
    #    popup_menu.insertSeparator(popup_menu.actions()[0])
    #    popup_menu.insertMenu(popup_menu.actions()[0], menuOutput)

        # This is a hack because if we leave the widget text empty
        # it throw a violent segmentation fault in start_process
        # self.connect(cleanAction, SIGNAL("triggered()"),
        #             lambda: self.setPlainText('\n\n'))

    #    popup_menu.exec_(event.globalPos())

    def append_text(self, text, text_format="normal"):
        cursor = self.textCursor()
        cursor.insertText(text, self._text_formats[text_format])
        cursor.insertBlock()
