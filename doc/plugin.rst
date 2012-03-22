3:``_
=====

How to create plugins``_
========================

We recommend that you install and use a oficial plugin called
**pluginProject**. That plugin helps you to create the skeleton of all
plugin for NINJA-IDE, also that plugin allow to test your plugin on
NINJA-IDE and packages your plugin to share it. You can install
**pluginProject** from thge Plugin Manager inside NINJA-IDE (Go to the
Plugins menu and Manage Plugins).

.. figure:: http://plugins.ninja-ide.googlecode.com/hg/ninja_img/install_pluginProject.png
   :align: center
   :alt: 

3.1``_
------

Plugin Descriptor file``_
-------------------------

This is just a JSON notation file with the extension “.plugin”. This
file helps NINJA-IDE to detect and manage your plugin. The following
information about the plugin should be inside it.

::

    {
      "module": "my_plugin",
      "class": "MyPluginExample",
      "authors": "Martin Alderete <malderete@gmail.com>",
      "version": "0.1",
      "url": "http://code.google.com/p/ninja-ide",
      "description": "Este plugin es de prueba"
    }

-  module: Indicates the name of the module where the Plugin class
   resides which will be instantiated by NINJA-IDE.
-  class: Indicates the name of the class which implements the Plugin.
-  authors: String with the author(s).
-  version: Indicates the Plugin version.
-  url: Indicates the url of the plugin may be where is the doc.
-  description: Plugin description

3.2``_
------

Service locator class``_
------------------------

This class provide a easy way to request and get the NINJA-IDE services
from your plugin. This class has two methods one for get a service and
other for get all services names.

To get a service:

::

       one_service = service_locator.get_service("name_of_the_Service")

To check all the possible services:

::

       for service_name in service_locator.get_availables_services():
          print service_name

3.3``_
------

Plugin class``_
---------------

All plugins must inherits from this class. This is the base class that
NINJA-IDE provides to creates plugins. This class also inherits from
`QObject`_ because of that your plugins are compatibles with
`signals/slots`_ of the Qt library.

3.3.1``_
--------

Attributes``_
-------------

-  self.metadata: A Python Dictionary with the content of the plugin
   descriptor file.
-  self.locator: A instance of ServiceLocator class
-  self.path: A string with the plugin directory
-  self.logger: a Instance of `PluginLogger`_.

3.3.1.1``_
----------

PluginLogger``_
---------------

This is the logger for plugins, allows to record events occured on
plugins. This is a wrapper over logging.Logger class of `logging`_
module.

3.3.2``_
--------

Methods``_
----------

initialize``_
~~~~~~~~~~~~~

This method is called for NINJA-IDE when your plugin is ready to start.
This is the recommended place to request/get the NINJA-IDE services for
your plugin.

finish``_
~~~~~~~~~

This method is called when NINJA-IDE is shutting down.

get\_preferences\_widget``_
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method is called for NINJA-IDE when the user open the preferences
dialog. This method allows us to integrate a custom configuration widget
in NINJA-IDE preferences. Is important that this m TRUNCATED! Please
download pandoc if you want to convert large files.

.. _: #3:
.. _: #How_to_create_plugins
.. _: #3.1
.. _: #Plugin_Descriptor_file
.. _: #3.2
.. _: #Service_locator_class
.. _: #3.3
.. _: #Plugin_class
.. _QObject: http://doc.qt.nokia.com/latest/qobject.html
.. _signals/slots: http://doc.qt.nokia.com/latest/signalsandslots.html
.. _: #3.3.1
.. _: #Attributes
.. _PluginLogger: /p/ninja-ide/wiki/APIDetails#3.3.1.1
.. _: #3.3.1.1
.. _: #PluginLogger
.. _logging: http://docs.python.org/library/logging.html#logger-objects
.. _: #3.3.2
.. _: #Methods
.. _: #initialize
.. _: #finish
.. _: #get_preferences_widget
