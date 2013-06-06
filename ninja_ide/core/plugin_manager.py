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

from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import shutil
import copy
import zipfile
import traceback
#lint:disable
try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import URLError
#lint:enable

from ninja_ide import resources
from ninja_ide.tools.logger import NinjaLogger
from ninja_ide.tools import json_manager

logger = NinjaLogger('ninja_ide.core.plugin_manager')
REQUIREMENTS = 'requirements.txt'
COMMAND_FOR_PIP_INSTALL = 'pip install -r %s'
try:
    # For Python2
    str = unicode  # lint:ok
except NameError:
    # We are in Python3
    pass


class ServiceLocator(object):

    '''
    Hold the services and allows the interaction between NINJA-IDE and plugins
    '''

    def __init__(self, services=None):
        self.__services = services if services else {}

    def get_service(self, name):
        return self.__services.get(name)

    def get_availables_services(self):
        return list(self.__services.keys())


'''
NINJA-IDE Plugin
my_plugin.plugin

{
  "module": "my_plugin",
  "class": "MyPluginExample",
  "authors": "Martin Alderete <malderete@gmail.com>",
  "version": "0.1",
  "description": "Este plugin es de prueba"
}

class MyPluginExample(Plugin):

    def initialize(self):
        #Configure the plugin using the NINJA-IDE API!!!
        self.editor_s = self.service_locator.get_service('editor')
        self.toolbar_s = self.service_locator.get_service('toolbar')
        self.toolbar_s.add_action(QAction(...........))
        self.appmenu_s = self.service_locator.get_service('appmenu')
        self.appmenu_s.add_menu(QMenu(......))
        #connect events!
        self.editor_s.editorKeyPressEvent.connect(self.my_plugin_key_pressed)

    def my_plugin_key_pressed(self, ...):
        print 'se apreto alguna tecla en el ide...'

'''
###############################################################################
# NINJA-IDE Plugin Manager
###############################################################################


class PluginManagerException(Exception):
    pass


#Singleton
__pluginManagerInstance = None


def PluginManager(*args, **kw):
    global __pluginManagerInstance
    if __pluginManagerInstance is None:
        __pluginManagerInstance = __PluginManager(*args, **kw)
    return __pluginManagerInstance

#Extension of the NINJA-IDE plugin
PLUGIN_EXTENSION = '.plugin'


class __PluginManager(object):
    '''
    Plugin manager allows to load, unload, initialize plugins.
    '''

    def __init__(self, plugins_dir, service_locator):
        '''
        @param plugins_dir: Path to search plugins.
        @param service_loctor: ServiceLocator object.
        '''
        self._service_locator = service_locator
        #new!
        self._plugins_by_dir = {}
        #add all the plugins paths
        for path in self.__create_list(plugins_dir):
            self.add_plugin_dir(path)
        #end new!
        #self._plugins_dir = plugins_dir
        self._errors = []
        #found plugins
        #example: ["logger", "my_plugin"]
        self._found_plugins = []
        #active plugins
        #example: {"logger": (LoggerIntance, metadata),
        #    "my_plugin": (MyPluginInstance, metadata)}
        self._active_plugins = {}

    def __create_list(self, obj):
        if isinstance(obj, (list, tuple)):
            return obj
        #string then returns a list of one item!
        return [obj]

    def add_plugin_dir(self, plugin_dir):
        '''
        Add a new directory to search plugins.

        @param plugin_dir: absolute path.
        '''
        if not plugin_dir in self._plugins_by_dir:
            self._plugins_by_dir[plugin_dir] = []

    def get_actives_plugins(self):
        import warnings
        warnings.warn("Deprecated in behalf of a TYPO free method name")
        return self.get_active_plugins()

    def get_active_plugins(self):
        '''
        Returns a list the instances
        '''
        return [plugin[0] for plugin in list(self._active_plugins.values())]

    def _get_dir_from_plugin_name(self, plugin_name):
        '''
        Returns the dir of the plugin_name
        '''
        for dir_, plug_names in list(self._plugins_by_dir.items()):
            if plugin_name in plug_names:
                return dir_

    def __getitem__(self, plugin_name):
        '''
        Magic method to get a plugin instance
        from a given name.
        @Note: This method has the logic below.
        Check if the plugin is known,
        if it is active return it,
        otherwise, active it and return it.
        If the plugin name does not exist
        raise KeyError exception.

        @param plugin_name: plugin name.

        @return: Plugin instance or None
        '''
        global PLUGIN_EXTENSION
        ext = PLUGIN_EXTENSION
        if not plugin_name.endswith(ext):
            plugin_name += ext

        if plugin_name in self._found_plugins:
            if not plugin_name in self._active_plugins:
                dir_ = self._get_dir_from_plugin_name(plugin_name)
                self.load(plugin_name, dir_)
            return self._active_plugins[plugin_name][0]
        raise KeyError(plugin_name)

    def __contains__(self, plugin_name):
        '''
        Magic method to know whether the
        PluginManager contains
        a plugin with a given name.

        @param plugin_name: plugin name.

        @return: True or False.
        '''
        return plugin_name in self._found_plugins

    def __iter__(self):
        '''
        Magic method to iterate over all
        the plugin's names.

        @return: iterator.
        '''
        return iter(self._found_plugins)

    def __len__(self):
        '''
        Magic method to know the plugins
        quantity.
        @return: length.
        '''
        return len(self._found_plugins)

    def __bool__(self):
        '''
        Magic method to indicate that any
        instance must pass the if conditional
        if x:
        '''
        return True

    def get_plugin_name(self, file_name):
        '''
        Get the plugin's name from a file name.
        @param file_name: A file object name.
        @return: A plugin name from a file.
        '''
        plugin_file_name, file_ext = os.path.splitext(file_name)
        return plugin_file_name

    def list_plugins(self, dir_name):
        '''
        Crawl a directory and collect plugins.
        @return: List with plugin names.
        '''
        global PLUGIN_EXTENSION
        ext = PLUGIN_EXTENSION
        try:
            listdir = os.listdir(dir_name)
            return [plug for plug in listdir if plug.endswith(ext)]
        except OSError:
            return ()

    def is_plugin_active(self, plugin_name):
        '''
        Check if a plugin is or not active
        @param plugin_name: Plugin name to check.
        @return: True or False
        '''
        return plugin_name in self._active_plugins

    def discover(self):
        '''
        Search all files for directory
        and get the valid plugin's names.
        '''
        for dir_name in self._plugins_by_dir:
            for file_name in self.list_plugins(dir_name):
                plugin_name = file_name
                if not plugin_name in self._found_plugins:
                    self._found_plugins.append(plugin_name)
                    self._plugins_by_dir[dir_name].append(plugin_name)

    def _load_module(self, module, klassname, metadata, dir_name):
        old_syspath = copy.copy(sys.path)
        try:
            sys.path.insert(1, dir_name)
            module = __import__(module, globals(), locals(), [])
            klass = getattr(module, klassname)
            #Instanciate the plugin
            plugin_instance = klass(self._service_locator, metadata=metadata)
            #return the plugin instance
            return plugin_instance
        except(ImportError, AttributeError) as reason:
            raise PluginManagerException('Error loading "%s": %s' %
                 (module, reason))
        finally:
            sys.path = old_syspath
        return None

    def load(self, plugin_name, dir_name):
        global PLUGIN_EXTENSION
        if plugin_name in self._active_plugins:
            return
        for dir_name, plugin_list in list(self._plugins_by_dir.items()):
            if plugin_name in plugin_list:
                ext = PLUGIN_EXTENSION
                plugin_filename = os.path.join(dir_name, plugin_name)
                plugin_structure = json_manager.read_json(plugin_filename)
                plugin_structure['name'] = plugin_name.replace(ext, '')
                module = plugin_structure.get('module', None)
                klassname = plugin_structure.get('class', None)
                if module is not None and klassname is not None:
                    try:
                        plugin_instance = self._load_module(module,
                            klassname, plugin_structure, dir_name)
                        #set a get_plugin method to get the reference to other
                        #setattr(plugin_instance,'get_plugin',self.__getitem__)
                        #call a special method *initialize* in the plugin!
                        plugin_instance.metadata = plugin_structure
                        logger.info("Calling initialize (%s)", plugin_name)
                        plugin_instance.initialize()
                        #tuple (instance, metadata)
                        plugin_metadata = (plugin_instance, plugin_structure)
                        self._active_plugins[plugin_name] = plugin_metadata
                    except (PluginManagerException, Exception) as reason:
                        logger.error("Not instanciated (%s): %s", plugin_name,
                            reason)
                        #remove the plugin because has errors
                        self._found_plugins.remove(plugin_name)
                        traceback_msg = traceback.format_exc()
                        plugin_name = plugin_name.replace(ext, '')
                        #add the traceback to errors
                        self._add_error(plugin_name, traceback_msg)
                    else:
                        logger.info("Successfuly initialized (%s)",
                            plugin_name)

    def load_all(self):
        for dir, pl in list(self._plugins_by_dir.items()):
            #Copy the list because may be we REMOVE item while iterate!
            found_plugins_aux = copy.copy(pl)
            for plugin_name in found_plugins_aux:
                self.load(plugin_name, dir)

    def load_all_external(self, plugin_path):
        #Copy the list because may be we REMOVE item while iterate!
        found_plugins_aux = copy.copy(self._found_plugins)
        for plugin_name in found_plugins_aux:
            self.load(plugin_name, plugin_path)

    def unload(self, plugin_name):
        try:
            plugin_object = self._active_plugins[plugin_name][0]
            #call a special method *finish* in the plugin!
            plugin_object.finish()
            del self._active_plugins[plugin_name]
        except Exception as reason:
            logger.error("Finishing plugin (%s): %s", plugin_name, reason)
        else:
            logger.info("Successfuly finished (%s)", plugin_name)

    def unload_all(self):
        #Copy the list because may be we REMOVE item while iterate!
        active_plugins_aux = copy.copy(self._active_plugins)
        for plugin_name in active_plugins_aux:
            self.unload(plugin_name)

    def shutdown(self):
        self.unload_all()

    def get_availables_services(self):
        """
        Returns all services availables
        """
        self._service_locator.get_availables_services()

    def _add_error(self, plugin_name, traceback_msg):
        self._errors.append((plugin_name, traceback_msg))

    @property
    def errors(self):
        """
        Returns a comma separated values of errors
        """
        return self._errors


def _availables_plugins(url):
    """
    Return the availables plugins from an url in NINJA-IDE web page
    """
    try:
        descriptor = urlopen(url)
        plugins = json_manager.read_json_from_stream(descriptor)
        return plugins
    except URLError:
        return {}


def available_oficial_plugins():
    '''
    Returns a dict with OFICIAL availables plugins in NINJA-IDE web page
    '''
    return _availables_plugins(resources.PLUGINS_WEB)


def available_community_plugins():
    '''
    Returns a dict with COMMUNITY availables plugins in NINJA-IDE web page
    '''
    return _availables_plugins(resources.PLUGINS_COMMUNITY)


def local_plugins():
    '''
    Returns the local plugins
    '''
    if not os.path.isfile(resources.PLUGINS_DESCRIPTOR):
        return []
    plugins = json_manager.read_json(resources.PLUGINS_DESCRIPTOR)
    return plugins


def __get_all_plugin_descriptors():
    '''
    Returns all the .plugin files
    '''
    global PLUGIN_EXTENSION
    return [pf for pf in os.listdir(resources.PLUGINS)
        if pf.endswith(PLUGIN_EXTENSION)]


def download_plugin(file_):
    '''
    Download a plugin specified by file_
    '''
    global PLUGIN_EXTENSION
    #get all the .plugin files in local filesystem
    plugins_installed_before = set(__get_all_plugin_descriptors())
    #download the plugin
    fileName = os.path.join(resources.PLUGINS, os.path.basename(file_))
    content = urlopen(file_)
    f = open(fileName, 'wb')
    f.write(content.read())
    f.close()
    #create the zip
    zipFile = zipfile.ZipFile(fileName, 'r')
    zipFile.extractall(resources.PLUGINS)
    zipFile.close()
    #clean up the enviroment
    os.remove(fileName)
    #get the name of the last installed plugin
    plugins_installed_after = set(__get_all_plugin_descriptors())
    #using set operations get the difference that is the new plugin
    new_plugin = (plugins_installed_after - plugins_installed_before).pop()
    return new_plugin


def manual_install(file_):
    """Copy zip file and install."""
    global PLUGIN_EXTENSION
    #get all the .plugin files in local filesystem
    plugins_installed_before = set(__get_all_plugin_descriptors())
    #copy the plugin
    fileName = os.path.join(resources.PLUGINS, os.path.basename(file_))
    shutil.copyfile(file_, fileName)
    #extract the zip
    zipFile = zipfile.ZipFile(fileName, 'r')
    zipFile.extractall(resources.PLUGINS)
    zipFile.close()
    #clean up the enviroment
    os.remove(fileName)
    #get the name of the last installed plugin
    plugins_installed_after = set(__get_all_plugin_descriptors())
    #using set operations get the difference that is the new plugin
    new_plugin = (plugins_installed_after - plugins_installed_before).pop()
    return new_plugin


def has_dependencies(plug):
    global REQUIREMENTS, COMMAND_FOR_PIP_INSTALL

    plugin_name = plug[0]
    structure = []
    if os.path.isfile(resources.PLUGINS_DESCRIPTOR):
        structure = json_manager.read_json(resources.PLUGINS_DESCRIPTOR)
    PLUGINS = resources.PLUGINS
    for p in structure:
        if p['name'] == plugin_name:
            pd_file = os.path.join(PLUGINS, p['plugin-descriptor'])
            p_json = json_manager.read_json(pd_file)
            module = p_json.get('module')
            #plugin_module/requirements.txt
            req_file = os.path.join(os.path.join(PLUGINS, module),
                REQUIREMENTS)
            if os.path.isfile(req_file):
                return (True, COMMAND_FOR_PIP_INSTALL % req_file)
            #the plugin was found but no requirement then break!
            break
    return (False, None)


def update_local_plugin_descriptor(plugins):
    '''
    updates the local plugin description
    The description.json file holds the information about the plugins
    downloaded with NINJA-IDE
    This is a way to track the versions of the plugins
    '''
    structure = []
    if os.path.isfile(resources.PLUGINS_DESCRIPTOR):
        structure = json_manager.read_json(resources.PLUGINS_DESCRIPTOR)
    for plug_list in plugins:
        #create the plugin data
        plug = {}
        plug['name'] = plug_list[0]
        plug['version'] = plug_list[1]
        plug['description'] = plug_list[2]
        plug['authors'] = plug_list[3]
        plug['home'] = plug_list[4]
        plug['download'] = plug_list[5]
        plug['plugin-descriptor'] = plug_list[6]
        #append the plugin data
        structure.append(plug)
    json_manager.write_json(structure, resources.PLUGINS_DESCRIPTOR)


def uninstall_plugin(plug):
    """
    Uninstall the given plugin
    """
    plugin_name = plug[0]
    structure = []
    if os.path.isfile(resources.PLUGINS_DESCRIPTOR):
        structure = json_manager.read_json(resources.PLUGINS_DESCRIPTOR)
    #copy the strcuture we iterate and remove at the same time
    structure_aux = copy.copy(structure)
    for plugin in structure_aux:
        if plugin["name"] == plugin_name:
            fileName = plugin["plugin-descriptor"]
            structure.remove(plugin)
            break
    #open <plugin>.plugin file and get the module to remove
    fileName = os.path.join(resources.PLUGINS, fileName)
    plugin = json_manager.read_json(fileName)
    module = plugin.get('module')
    if module:
        pluginDir = os.path.join(resources.PLUGINS, module)
        folders = [pluginDir]
        for root, dirs, files in os.walk(pluginDir):
            pluginFiles = [os.path.join(root, f) for f in files]
            #remove all files
            list(map(os.remove, pluginFiles))
            #collect subfolders
            folders += [os.path.join(root, d) for d in dirs]
        folders.reverse()
        for f in folders:
            if os.path.isdir(f):
                os.removedirs(f)
        #remove ths plugin_name.plugin file
        os.remove(fileName)
    #write the new info
    json_manager.write_json(structure, resources.PLUGINS_DESCRIPTOR)


###############################################################################
# Module Test
###############################################################################

if __name__ == '__main__':
    folders = resources.PLUGINS
    services = {}
    sl = ServiceLocator(services)
    pm = PluginManager(folders, sl)
    #There are not plugins yet...lets discover
    pm.discover()
    logger.info("listing plugins names...")
    for p in pm:
        print(p)
    logger.info("Activating plugins...")
    pm.load_all()
    logger.info("Plugins already actives...")
    logger.info(pm.get_active_plugins())
