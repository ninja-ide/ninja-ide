# -*- coding: utf-8 -*-
from __future__ import absolute_import

import time
import re

from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QTextCharFormat
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import SIGNAL

from ninja_ide.core import settings
from ninja_ide.core import file_manager
from ninja_ide.tools import styles
from ninja_ide.gui.main_panel import main_container


class RunWidget(QWidget):

    """Widget that show the execution output in the MiscContainer."""

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.output = OutputWidget(self)
        hbox = QHBoxLayout()
        self.input = QLineEdit()
        self.lblInput = QLabel(self.tr("Input:"))
        vbox.addWidget(self.output)
        hbox.addWidget(self.lblInput)
        hbox.addWidget(self.input)
        vbox.addLayout(hbox)

        #process
        self._proc = QProcess(self)
        self.connect(self._proc, SIGNAL("readyReadStandardOutput()"),
            self.output._refresh_output)
        self.connect(self._proc, SIGNAL("readyReadStandardError()"),
            self.output._refresh_error)
        self.connect(self._proc, SIGNAL("finished(int, QProcess::ExitStatus)"),
            self.finish_execution)
        self.connect(self._proc, SIGNAL("error(QProcess::ProcessError)"),
            self.process_error)
        self.connect(self.input, SIGNAL("returnPressed()"), self.insert_input)

    def process_error(self, error):
        """Listen to the error signals from the running process."""
        self.lblInput.hide()
        self.input.hide()
        self._proc.kill()
        format = QTextCharFormat()
        format.setAnchor(True)
        format.setForeground(Qt.red)
        if error == 0:
            self.output.textCursor().insertText(self.tr('Failed to start'),
                format)
        else:
            self.output.textCursor().insertText(
                self.tr('Error during execution, QProcess error: %d' % error),
                format)

    def finish_execution(self, exitCode, exitStatus):
        """Print a message and hide the input line when the execution ends."""
        self.lblInput.hide()
        self.input.hide()
        format = QTextCharFormat()
        format.setAnchor(True)
        self.output.textCursor().insertText('\n\n')
        if exitStatus == QProcess.NormalExit:
            format.setForeground(Qt.green)
            self.output.textCursor().insertText(
                self.tr("Execution Successful!"), format)
        else:
            format.setForeground(Qt.red)
            self.output.textCursor().insertText(
                self.tr("Execution Interrupted"), format)

    def insert_input(self):
        """Take the user input and send it to the process."""
        text = self.input.text() + '\n'
        self._proc.writeData(text)
        self.input.setText("")

    def start_process(self, fileName, pythonPath=False, programParams=''):
        """Prepare the output widget and start the process."""
        self.lblInput.show()
        self.input.show()
        self.output.setCurrentCharFormat(self.output.plain_format)
        self.output.setPlainText('Running: %s (%s)\n\n' % (fileName,
            unicode(time.ctime())))
        self.output.moveCursor(QTextCursor.Down)
        self.output.moveCursor(QTextCursor.Down)
        self.output.moveCursor(QTextCursor.Down)

        #runner.run_code_from_file(fileName)
        if not pythonPath:
            pythonPath = settings.PYTHON_PATH
        #change the working directory to the fileName dir
        file_directory = file_manager.get_folder(fileName)
        self._proc.setWorkingDirectory(file_directory)
        #force python to unbuffer stdin and stdout
        options = ['-u'] + settings.EXECUTION_OPTIONS.split()
        self._proc.start(pythonPath, options + [fileName] + \
            [p.strip() for p in programParams.split(',') if p])

    def kill_process(self):
        """Kill the running process."""
        self._proc.kill()


class OutputWidget(QPlainTextEdit):

    def __init__(self, parent):
        QPlainTextEdit.__init__(self, parent)
        self._parent = parent
        self.setReadOnly(True)
        styles.set_style(self, 'editor')
        self.maxValue = 0
        self.actualValue = 0
        #traceback pattern
        self.patLink = re.compile(r'(\s)*File "(.*?)", line \d.+')
        #formats
        self.plain_format = QTextCharFormat()
        self.error_format = QTextCharFormat()
        self.error_format.setAnchor(True)
        self.error_format.setFontUnderline(True)
        self.error_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        self.error_format.setUnderlineColor(Qt.red)
        self.error_format.setForeground(Qt.blue)
        self.error_format.setToolTip(self.tr("Click to show the source"))

        self.connect(self, SIGNAL("blockCountChanged(int)"), self._scroll_area)

    def _scroll_area(self):
        """When new text is added to the widget, move the scroll to the end."""
        if self.actualValue == self.maxValue:
            self.moveCursor(QTextCursor.End)

    def mousePressEvent(self, event):
        """
        When the execution fail, allow to press the links in the traceback,
        to go to the line when the error occur.
        """
        QPlainTextEdit.mousePressEvent(self, event)
        self.go_to_error(event)

    def _refresh_output(self):
        """Read the output buffer from the process and append the text."""
        #we should decode the bytes!
        text = self._parent._proc.readAllStandardOutput().data().decode('utf8')
        verticalScroll = self.verticalScrollBar()
        self.actualValue = verticalScroll.value()
        self.maxValue = verticalScroll.maximum()
        self.textCursor().insertText(text)

    def _refresh_error(self):
        """Read the error buffer from the process and append the text."""
        #we should decode the bytes!
        cursor = self.textCursor()
        text = self._parent._proc.readAllStandardError().data().decode('utf8')
        text_lines = text.split('\n')
        verticalScroll = self.verticalScrollBar()
        self.actualValue = verticalScroll.value()
        self.maxValue = verticalScroll.maximum()
        for t in text_lines:
            cursor.insertBlock()
            if self.patLink.match(t):
                cursor.insertText(t, self.error_format)
            else:
                cursor.insertText(t, self.plain_format)

    def go_to_error(self, event):
        """Resolve the link and take the user to the error line."""
        cursor = self.cursorForPosition(event.pos())
        text = cursor.block().text()
        if self.patLink.match(text):
            file_path, lineno = self._parse_traceback(unicode(text))
            main = main_container.MainContainer()
            main.open_file(file_path)
            main.editor_jump_to_line(lineno=int(lineno) - 1)

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
        self.connect(cleanAction, SIGNAL("triggered()"),
            lambda: self.setPlainText('\n\n'))

        popup_menu.exec_(event.globalPos())
