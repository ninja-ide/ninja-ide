import os
import sys
import re
import json
import subprocess
from collections import namedtuple

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtQuickWidgets import QQuickWidget

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint

from ninja_ide.core import settings
from ninja_ide.tools import ui_tools
from ninja_ide.gui.ide import IDE

if settings.IS_WINDOWS:
    regex = re.compile("/^python(\d+(.\d+)?)?\.exe$/")
else:
    regex = re.compile("^python(\d+(.\d+)?)?$")


PythonInfo = namedtuple("PythonInfo", "path name version")


class PyChooser(QWidget):

    def __init__(self, btn, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Popup)
        self._btn = btn
        self.setAttribute(Qt.WA_TranslucentBackground)
        box = QVBoxLayout(self)
        self.view = QQuickWidget()
        self.view.setClearColor(Qt.transparent)
        self.setFixedWidth(300)
        self.setFixedHeight(200)
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("PythonChooser.qml"))

        self._root = self.view.rootObject()
        box.addWidget(self.view)

        self._model = {}

        self._root.pythonSelected.connect(self.set_python_interpreter)

    def setVisible(self, visible):
        super().setVisible(visible)
        self._btn.setChecked(visible)

    def showEvent(self, event):
        ide = IDE.get_service("ide")
        move_to = ide.mapToGlobal(QPoint(0, 0))
        move_to -= QPoint(
            -ide.width() + self.width() - 5,
            -ide.height() + self.height() + 20)
        self.move(move_to)
        self.add_model()

    def set_python_interpreter(self, path, name):
        settings.PYTHON_EXEC = path
        p = self._model[name]
        self._btn.setText(p.name)
        self._btn.setToolTip(p.path)

    def add_model(self):
        list_of_python = suggestions()
        if not self._model:
            for p in list_of_python:
                name, path = p
                data = json.loads(get_info(path))
                version_info = data["versionInfo"]
                ver = ".".join(list(map(str, version_info))[:3])
                pinfo = PythonInfo(path, name, ver)
                self._model[name] = pinfo
        self._root.setModel(list_of_python)

    def hideEvent(self, event):
        super().hideEvent(event)
        self._root.clearModel()


def know_paths():
    if settings.IS_WINDOWS:
        return []
    paths = [
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/sbin",
        "/sbin",
        "/usr/local/sbin"
    ]
    return paths


def suggestions():
    paths = []
    append = paths.append
    for path in know_paths():
        if not os.path.exists(path):
            continue
        files = os.listdir(path)
        for f in files:
            if regex.match(f):
                append([f, os.path.join(path, f)])
    return paths


def get_info(interpreter):
    string = """import sys
import json
info = {}
info["versionInfo"] = sys.version_info[:4]
info["version"] = sys.version
print(json.dumps(info))"""
    return subprocess.check_output([interpreter, "-c", string]).decode()
