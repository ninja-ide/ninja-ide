from PyQt5.QtCore import QObject


class IToolDock(QObject):

    def __init__(self):
        QObject.__init__(self)

    def display_name(self):
        pass

    def widget(self):
        pass
