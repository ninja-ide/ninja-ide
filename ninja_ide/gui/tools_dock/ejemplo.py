from PyQt5.QtWidgets import *
from ninja_ide.gui.tools_dock import itool_dock
from ninja_ide.gui.tools_dock.tools_dock_manager import ToolsDockManager
from ninja_ide.gui.ide import IDE


class Ejemplo(itool_dock.IToolDock):

    def __init__(self):
        super().__init__()
        self._widget = QPlainTextEdit()

        ToolsDockManager.register_tooldock(self)

    def display_name(self):
        return 'Mi Ejemplo'

    def widget(self):
        return self._widget


e = Ejemplo()
