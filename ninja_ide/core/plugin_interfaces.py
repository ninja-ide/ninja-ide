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
# ABSTRACT CLASSES (This file contains useful interfaces for plugins)

#We know, Python does not need interfaces, but this file is useful as
#documentation. Is not mandatory inherit from these interfaces but you SHOULD
#implement the methods inside them.
###############################################################################


class MethodNotImplemented(Exception):
    pass


def implements(iface):
    """
    A decorator to check if interfaces are correctly implmented
    #TODO: check if functions parameters are correct
    """

    def implementsIA(cls, *args, **kwargs):
        """
        Find out which methods should be and are not in the implementation
        of the interface, raise errors if class is not correctly implementing.
        """
        should_implement = set(dir(iface)).difference(set(dir(object)))
        should_implement = set(should for should in should_implement if
                                not should.startswith("_"))
        not_implemented = should_implement.difference(set(dir(cls)))
        if len(not_implemented) > 0:
            raise MethodNotImplemented("Methods %s not implemented" %
                                         ", ".join(not_implemented))
        if cls.__name__ not in globals():
            #if decorated a class is not in globals
            globals()[cls.__name__] = cls
        return cls
    return implementsIA


class IProjectTypeHandler(object):

    """
    Interface to create a Project type handler
    """

    #mandatory
    def get_pages(self):
        """
        Returns a collection of QWizardPage
        """
        pass

    #mandatory
    def on_wizard_finish(self, wizard):
        """
        Called when the user finish the wizard
        @wizard: QWizard instance
        """
        pass

    def get_context_menus(self):
        """"
        Returns a iterable of QMenu
        """
        pass


class ISymbolsHandler:
    """
    Interface to create a symbol handler
    EXAMPLE:
    {
     'attributes':
         {name: line, name: line},
     'functions':
         {name: line, name: line},
     'classes':
         {
         name: (line, {
                     'attributes': {name: line},
                     'function': {name: line}}
             )
         }
     }
    """

    #mandatory
    def obtain_symbols(self, source):
        """
        Returns the dict needed by the tree
        @source: Source code in plain text
        """
        pass


class IPluginPreferences:
    """
    Interface for plugin preferences widget
    """
    #mandatory
    def save(self):
        """
        Save the plugin data as NINJA-IDE settings
        """
        pass
