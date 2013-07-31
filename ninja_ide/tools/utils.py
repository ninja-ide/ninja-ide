# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject


class SignalFlowControl(QObject):
    def __init__(self):
        self.__stop = False

    def stop(self):
        self.__stop = True

    def stopped(self):
        return self.__stop
