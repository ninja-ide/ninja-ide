#-*- coding: utf-8 -*-
from __future__ import absolute_import

import socket

from PyQt4.QtCore import QThread
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QSharedMemory
from PyQt4.QtCore import SIGNAL


sharedMemory = QSharedMemory('shared_ninja')
file_delimiter = '<-nf>'
project_delimiter = '<-np>'


class SessionListener(QThread):

###############################################################################
# SessionListener SIGNALS
###############################################################################
    """
    fileOpenRequested(QString)
    projectOpenRequested(QString)
    """
###############################################################################

    def __init__(self):
        QThread.__init__(self)
        self.s_listener = socket.socket()
        self.execute = True

    def run(self):
        port = 9990
        while port < 11000:
            try:
                self.s_listener.bind(("localhost", port))
                qsettings = QSettings('NINJA-IDE', 'NINJA-IDE')
                qsettings.setValue('port-settings', port)
                break
            except:
                port += 1
        self.s_listener.listen(1)
        while self.execute:
            client, (host, port) = self.s_listener.accept()
            length = client.recv(1024)
            client.send('ack')
            files = client.recv(int(length))
            length = client.recv(1024)
            client.send('ack')
            projects = client.recv(int(length))
            files = files.split(file_delimiter)
            projects = projects.split(project_delimiter)
            client.close()
            for file in files:
                self.emit(SIGNAL("fileOpenRequested(QString)"), file)
            for project in projects:
                self.emit(SIGNAL("projectOpenRequested(QString)"), project)


def is_running():
    global sharedMemory
    running = sharedMemory.attach()
    if not running:
        sharedMemory.create(1024)
    return running


def send_data(filenames, projects_path):
    global file_delimiter
    global project_delimiter
    qsettings = QSettings('NINJA-IDE', 'NINJA-IDE')
    port = qsettings.value('port-settings', 9990).toInt()[0]
    files = file_delimiter.join(filenames)
    projects = project_delimiter.join(projects_path)
    files_length = len(files)
    projects_length = len(projects)
    client = socket.socket()
    client.connect(("localhost", port))
    client.send(str(files_length))
    client.recv(3)
    client.send(files)
    client.send(str(projects_length))
    client.recv(3)
    client.send(projects)
    client.close()


def close_listener(thread):
    global sharedMemory
    sharedMemory.detach()
    thread.execute = False
    thread.s_listener.close()
