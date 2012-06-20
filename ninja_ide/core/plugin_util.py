# -*- coding: utf-8 *-*


class ContextMenuScope(object):
    """
    This class is just a domain class for the plugin API
    it hold the info about the project explorer context menu
    """
    def __init__(self, project=False, folder=False, files=False):
        self.project = project
        self.folder = folder
        self.file = files
