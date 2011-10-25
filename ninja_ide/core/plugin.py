# -*- coding: UTF-8 -*-

from __future__ import absolute_import

import os
import sys
import logging

from PyQt4.QtCore import QObject


class Plugin(QObject):
    '''
    Base class for ALL Plugin
    All plugins should inherit from this class
    '''

    def __init__(self, locator, metadata=None):
        QObject.__init__(self)
        self.locator = locator
        if metadata is None:
            self.metadata = {}
        else:
            self.metadata = metadata
        self.logger = PluginLogger(self)
        #set the path!
        try:
            self_module = self.__module__
            path = os.path.abspath(sys.modules[self_module].__file__)
            self._path = os.path.dirname(path)
        except:
            self._path = ''

    def initialize(self):
        raise NotImplemented

    def finish(self):
        pass

    def get_preferences_widget(self):
        pass

    @property
    def path(self):
        return self._path


class PluginLogger(object):
    """
    Logger for plugins, it wrap the python logger
    to set the class name to the logger
    """

    def __init__(self, instance):
        klass = instance.__class__
        plugin_name = "%s.%s" % (klass.__module__, klass.__name__)
        self.logger = logging.getLogger('ninja_ide.plugins.%s' % plugin_name)
        self.logger.setLevel(logging.DEBUG)

    def debug(self, *a, **k):
        self.logger.debug(*a, **k)

    def info(self, *a, **k):
        self.logger.info(*a, **k)

    def warning(self, *a, **k):
        self.logger.warning(*a, **k)

    def error(self, *a, **k):
        self.logger.error(*a, **k)

    def critical(self, *a, **k):
        self.logger.critical(*a, **k)
