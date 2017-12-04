# -*- coding: utf-8 -*-
from PyQt5.QtCore import (
    QObject,
    QTimer
)


class SignalFlowControl(QObject):
    def __init__(self):
        self.__stop = False

    def stop(self):
        self.__stop = True

    def stopped(self):
        return self.__stop


class Runner(object):
    """Useful class for running jobs with a delay"""

    def __init__(self, delay=2000):
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._execute_job)
        self._delay = delay

        self._job = None
        self._args = []
        self._kw = {}

    def cancel(self):
        """Cancel the current job"""
        self._timer.stop()
        self._job = None
        self._args = []
        self._kw = {}

    def run(self, job, *args, **kw):
        """Request a job run. If there is a job, cancel and run the new job
        with a delay specified in __init__"""
        self.cancel()
        self._job = job
        self._args = args
        self._kw = kw
        self._timer.start(self._delay)

    def _execute_job(self):
        """Execute job after the timer has timeout"""
        self._timer.stop()
        self._job(*self._args, **self._kw)
