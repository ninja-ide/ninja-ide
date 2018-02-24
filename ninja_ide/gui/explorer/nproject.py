# -*- coding: utf-8 -*-

from PyQt5.QtCore import (
    QObject,
    QDir,
    pyqtSignal
)

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
    projectNameUpdated = pyqtSignal('QString')

    def __init__(self, path):
        super(NProject, self).__init__()
        project = json_manager.read_ninja_project(path)
        self.path = path
        self._name = project.get('name', '')
        if not self._name:
            self._name = file_manager.get_basename(path)
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
        self.extensions = project.get(
            'supported-extensions',
            settings.get_supported_extensions()
        )
        self.python_exec = project.get('pythonExec', settings.PYTHON_EXEC)
        self.python_path = project.get('PYTHONPATH', '')
        self.additional_builtins = project.get('additional_builtins', [])
        self.program_params = project.get('programParams', '')
        self.venv = project.get('venv', '')
        self.related_projects = project.get('relatedProjects', [])
        self.added_to_console = False
        # FIXME: This is handle in tree_projects_widget._change_current_project
        # Review to maybe improve.
        self.is_current = True
        # Model is a QFileSystemModel to be set on runtime
        self.__model = None

    def _get_name(self):
        return self._name

    def _set_name(self, name):
        if name == '':
            self._name = file_manager.get_basename(self.path)
        else:
            self._name = name
        self.projectNameUpdated.emit(self._name)

    name = property(_get_name, _set_name)

    def save_project_properties(self):
        # save project properties
        project = {}
        project['name'] = self._name
        project['description'] = self.description
        project['url'] = self.url
        project['license'] = self.license
        project['mainFile'] = self.main_file
        project['project-type'] = self.project_type
        project['supported-extensions'] = self.extensions
        project['indentation'] = self.indentation
        project['use-tabs'] = self.use_tabs
        project['pythonExec'] = self.python_exec  # FIXME
        project['PYTHONPATH'] = self.python_path
        project['additional_builtins'] = self.additional_builtins
        project['preExecScript'] = self.pre_exec_script
        project['postExecScript'] = self.post_exec_script
        project['venv'] = self.venv
        project['programParams'] = self.program_params
        project['relatedProjects'] = self.related_projects
        if file_manager.file_exists(self.path, self._name + '.nja'):
            file_manager.delete_file(self.path, self._name + '.nja')
        json_manager.create_ninja_project(self.path, self._name, project)
        # TODO: update project tree on extensions changed

    @property
    def full_path(self):
        '''
        Returns the full path of the project
        '''
        project_file = json_manager.get_ninja_project_file(self.path)
        if not project_file:  # FIXME: If we dont have a project file
            project_file = ''  # we should do SOMETHING! like kill zombies!
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
        self.__model.setFilter(
            QDir.AllDirs | QDir.NoDotAndDotDot | QDir.AllEntries)
        self.__model.setNameFilters(self.extensions)

    @model.deleter
    def model(self):
        del(self.__model)
