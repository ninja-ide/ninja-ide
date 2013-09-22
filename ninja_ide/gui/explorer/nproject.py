# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject, QDir

import os

from ninja_ide import translations

from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import json_manager


class NProject(QObject):
    """Project representation.
    SIGNALS:
    @projectPropertiesUpdated()
    """

    def __init__(self, path):
        super(NProject, self).__init__()
        project = json_manager.read_ninja_project(path)

        self.path = path
        self.name = project.get('name', '')
        if self.name == '':
            self.name = file_manager.get_basename(path)
        self.project_type = project.get('project-type', '')
        self.description = project.get('description', '')
        if self.description == '':
            self.description = translations.TR_NO_DESCRIPTION
        self.url = project.get('url', '')
        self.license = project.get('license', '')
        self.main_file = project.get('mainFile', '')
        self.pre_exec_script = project.get('preExecScript', '')
        self.post_exec_script = project.get('postExecScript', '')
        self.indentation = project.get('indentation', settings.INDENT)
        self.use_tabs = project.get('use-tabs', settings.USE_TABS)
        self.extensions = project.get('supported-extensions',
            settings.SUPPORTED_EXTENSIONS)
        self.python_exec = project.get('pythonPath', settings.PYTHON_EXEC)
        self.python_path = project.get('PYTHONPATH', '')
        self.additional_builtins = project.get('additional_builtins', [])
        self.program_params = project.get('programParams', '')
        self.venv = project.get('venv', '')
        self.related_projects = project.get('relatedProjects', [])
        self.added_to_console = False
        self.is_current = False
        #Model is a QFileSystemModel to be set on runtime
        self.__model = None

    @property
    def full_path(self):
        '''
        Returns the full path of the project
        '''
        project_file = json_manager.get_ninja_project_file(self.path)
        if not project_file:  # FIXME: If we dont have a project file
            project_file = ''     # we should do SOMETHING! like kill zombies!
        return os.path.join(self.path, project_file)

    @property
    def python_exec_command(self):
        '''
        Returns the python exec command of the project
        '''
        if self.venv is '':
            return self.venv
        return self.python_exec

    @property
    def model(self):
        return self.__model

    @model.setter
    def model(self, model):
        self.__model = model
        self.__model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.AllEntries)
        self.__model.setNameFilters(self.extensions)

    @model.deleter
    def model(self):
        del(self.__model)
