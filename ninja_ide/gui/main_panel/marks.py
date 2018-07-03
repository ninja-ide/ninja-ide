from PyQt5.QtGui import QIcon

from PyQt5.QtCore import Qt

from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import ui_tools


class Mark(object):

    def __init__(self, filename, lineno):
        self.__icon = None
        self.filename = filename
        self.lineno = lineno
        self.tooltip = filename
        self.note = ""

    @property
    def display_name(self):
        return file_manager.get_basename(self.filename)

    @property
    def icon(self):
        return self.__icon

    def set_icon(self, icon):
        if isinstance(icon, QIcon):
            self.__icon = icon
        else:
            self.__icon = QIcon(":img/{}".format(icon))

    def paint_icon(self, painter, rect):
        self.__icon.paint(painter, rect, Qt.AlignCenter)


class Bookmark(Mark):

    def __init__(self, filename, lineno):
        super().__init__(filename, lineno)
        self.set_icon(ui_tools.get_icon("bookmark", "#8080ff"))
        self._linetext = ""

    @property
    def linetext(self):
        return self._linetext.strip()

    @linetext.setter
    def linetext(self, text):
        self._linetext = text

    def __str__(self):
        return "<Bookmark: {} at {}".format(self.filename, self.lineno)
