# -*- coding: utf-8 -*-


###############################################################################
# ABSTRACT CLASSES (This file contains useful interfaces for plugins)

#We know, Python does not need interfaces, but this file is useful as
#documentation. Is not mandatory inherit from these interfaces but you SHOULD
#implement the methods inside them.
###############################################################################


class MethodNotImplemented(Exception):
    pass


class IProjectTypeHandler:

    """
    Interface to create a Project type handler
    """

    #mandatory
    def get_pages(self):
        """
        Returns a collection of QWizardPage
        """
        raise MethodNotImplemented("Method not implemented")

    #mandatory
    def on_wizard_finish(self, wizard):
        """
        Called when the user finish the wizard
        @wizard: QWizard instance
        """
        raise MethodNotImplemented("Method not implemented")

    def get_context_menus(self):
        """"
        Returns a iterable of QMenu
        """
        return ()


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
        raise MethodNotImplemented("Method not implemented")


class IPluginPreferences:
    """
    Interface for plugin preferences widget
    """
    #mandatory
    def save(self):
        """
        Save the plugin data as NINJA-IDE settings
        """
        raise MethodNotImplemented("Method not implemented")
