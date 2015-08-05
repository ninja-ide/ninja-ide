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

###############################################################################
# Virtualenv bootstraping
###############################################################################

import os
import sys

from virtualenv import create_environment

#This is here only for reference purposes
#def create_environment(home_dir, site_packages=False, clear=False,
#                       unzip_setuptools=False,
#                       prompt=None, search_dirs=None, never_download=False,
#                       no_setuptools=False, no_pip=False, symlink=True):

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.core.encapsulated_env.nenvironement')
#FIXME: Nothing is being printed, idk why
DEBUG = logger.debug


def debug(x):
    print(x)
DEBUG = debug

from ninja_ide.resources import HOME_NINJA_PATH
NINJA_ENV_NAME = "venv"
NINJA_ENV = os.path.join(HOME_NINJA_PATH, NINJA_ENV_NAME)
NINJA_ENV_BIN = os.path.join(NINJA_ENV, "bin")

if not os.path.isdir(NINJA_ENV):
    create_environment(NINJA_ENV)
if not os.path.isdir(NINJA_ENV_BIN):
    NINJA_ENV_BIN = os.path.join(NINJA_ENV, "Scripts")


NINJA_ENV_ACTIVATE = os.path.join(NINJA_ENV_BIN, "activate_this.py")


exec(compile(open(NINJA_ENV_ACTIVATE).read(), NINJA_ENV_ACTIVATE, 'exec'),
     dict(__file__=NINJA_ENV_ACTIVATE))

###############################################################################
from pip import main as pipmain
#lint:disable
try:
    from pip.backwardcompat import xmlrpclib
except:
    if sys.version_info[0] >= 3:
        import xmlrpc
    else:
        import xmlrpclib
try:
    from pip.util import get_installed_distributions
except:
    from pip.utils import get_installed_distributions
#lint:enable
from PyQt4.QtCore import QObject, SIGNAL, QThread


PLUGIN_QUERY = {"keywords": "ninja_ide plugin"}


class AsyncRunner(QThread):
    """
    Run in a QThread the given callable.
    SIGNALS:
    @threadEnded()
    @threadFailed(const QString&)
    @threadFinished(PyQt_PyObject)
    """

    def __init__(self, runable):
        self.__runable = runable
        self.__args = []
        self.__kwargs = {}
        self.__finished = False
        self.__iserror = False
        self.__errmsg = ""
        super(AsyncRunner, self).__init__()
        self.connect(self, SIGNAL("threadEnded()"), self._success_finish)
        self.connect(self, SIGNAL("threadFailed(const QString&)"),
                     self._fail_finish)

    def _success_finish(self):
        self.__finished = True
        self.wait()
        self.emit(SIGNAL("threadFinished(PyQt_PyObject)"), self.status)

    def _fail_finish(self, errmsg):
        self.__finished = True
        self.__iserror = True
        self.__errmsg = errmsg
        self.wait()
        self.emit(SIGNAL("threadFinished(PyQt_PyObject)"), self.status)

    def status(self):
        """
        Return status of running process.
        finished: this indicates if running or not, no result info
        exit_state: 0 success, 1 error
        exit_msg: only populated on error
        """
        return {"finished": self.__finished,
                "exit_state": self.__iserror,
                "exit_msg": self.__errmsg}

    def __call__(self, *args, **kwargs):
        """
        Usually called as a decorator, it is interesting to return a reference
        to this runner so the caller can check on status or at least subscribe
        """
        self.__args = args
        self.__kwargs = kwargs
        self.start()
        return self

    def run(self):
        try:
            self.__runable(*self.__args, **self.__kwargs)
            self.emit(SIGNAL("threadEnded()"))
        except Exception as e:
            if hasattr(e, "message"):
                errmsg = e.message
            else:  # Python 3
                errmsg = str(e)
            self.emit(SIGNAL("threadFailed(QString)"), errmsg)


def make_async(func):
    """Decorate methods to be run as Qthreads"""
    def make_me_async(*args, **kwargs):
        async_func = AsyncRunner(func)
        async_func(*args, **kwargs)
        return async_func

    return make_me_async


class NenvEggSearcher(QObject):
    """
    SIGNALS:
    @searchTriggered()
    @searchCompleted(PyQt_PyObject)
    """

    def __init__(self):
        super(NenvEggSearcher, self).__init__()
        self.search_url = "https://pypi.python.org/pypi"
        self.__pypi = None

    @property
    def pypi(self):
        """I want to delay doing this, since might not be necessary"""
        if self.__pypi is None:
            self.__pypi = xmlrpclib.ServerProxy(self.search_url)
        return self.__pypi

    @make_async
    def do_search(self):
        self.emit(SIGNAL("searchTriggered()"))
        plugins_found = self.pypi.search(PLUGIN_QUERY, "and")
        self.emit(SIGNAL("searchCompleted(PyQt_PyObject)"),
                  self.__iterate_results(plugins_found))

    def __iterate_results(self, result_list):
        for each_plugin in result_list:
            yield PluginMetadata.from_result(each_plugin, self.pypi)

    def export_env(self):
        """
        This should wrap pip freeze in the future
        iterates over pip installed packages, local and not local
        returns tuples version, name
        """
        for each_distribution in get_installed_distributions():
            yield each_distribution.version, each_distribution.key


class PluginMetadata(QObject):
    """
    Hold all available metadata for a given plugin, default instance is
    created by from_result factory which returns a shallow instance, only
    holding the data from a result (name, summary, version).
    To obtain full data call inflate.

    SIGNALS:
    @willInflatePluginMetadata()
    @pluginMetadataInflated()
    @pluginInstalled(PyQt_PyObject)
    """

    @classmethod
    def from_result(cls, r, pypi):
        return cls(name=r["name"],
                   summary=r["summary"],
                   version=r["version"],
                   pypi=pypi)

    def __init__(self, name, summary, version, pypi, shallow=True, **kwargs):
        #shallow attributes
        self.name = name
        self.summary = summary
        self.version = version
        self.pypi = pypi

        #Set manually to bind in the ui after inflate
        self.identifier = 0
        #Inflated attributes (zeroed, declared here just for doc purposes)
        self.stable_version = ""
        self.author = ""  # used by store
        self.author_email = ""  # used by store
        self.maintainer = ""
        self.maintainer_email = ""
        self.home_page = ""  # used by store
        self.license = ""  # used by store
        self.description = ""  # used by store
        self.keywords = ""  # used by store
        self.platform = ""
        self.download_url = ""  # used by store
        #(list of classifier strings)
        self.classifiers = []  # used by store
        self.requires = ""
        self.requires_dist = ""
        self.provides = ""
        self.provides_dist = ""
        self.requires_external = ""
        self.requires_python = ""
        self.obsoletes = ""
        self.obsoletes_dist = ""
        self.project_url = ""
        #(URL of the packages.python.org docs if they've been supplied)
        self.docs_url = ""

        #internal attributes
        self.shallow = shallow
        super(PluginMetadata, self).__init__()
        if kwargs:
            for each_kwarg, each_value in kwargs:
                setattr(self, each_kwarg, each_value)
            self.shallow = False

    def activate(self):
        imported_plugin = __import__(self.name)
        imported_plugin.activate()

    @make_async
    def inflate(self):
        """
        Fill extra attributes of a shallow object
        """
        if self.shallow:
            self.emit(SIGNAL("willInflatePluginMetadata()"))
            rdata = self.pypi.release_data(self.name, self.version)
            for each_arg, each_value in rdata.items():
                setattr(self, each_arg, each_value)
            self.emit(SIGNAL("pluginMetadataInflated(PyQt_PyObject)"), self)
            self.shallow = False

    @make_async
    def install(self):
        """
        Install this package in the current env.
        We always specify the version, we cant be sure we are the latest one
        or that the user wants to install any other available.
        """
        pkg_string = "%s==%s" % (self.name, self.version)
        pipmain(["install", "-q", pkg_string])
        self.emit(SIGNAL("pluginInstalled(PyQt_PyObject)"), self)

    @make_async
    def reinstall(self):
        pipmain(["install", "-q", "--force-reinstall", self.name])
        self.emit(SIGNAL("pluginInstalled(PyQt_PyObject)"), self)

    @make_async
    def upgrade(self):
        pipmain(["install", "-q", "--ugprade", self.name])
        self.emit(SIGNAL("pluginInstalled(PyQt_PyObject)"), self)

    @make_async
    def remove(self):
        pipmain(["uninstall", "-q", "-y", self.name])


class BasePlugin(QObject):
    """
    A base from which every plugin should inherit
    """

    def __init__(self, name):
        super(BasePlugin, self).__init__()

    def activate(self):
        pass


#This is how the directory structure should look
"""
ninja_ide/
    __init__.py
    contrib/
        __init__.py
        plugins/
            __init__.py
            yourpluginname/
                __init__.py
                yourcode.py
"""
