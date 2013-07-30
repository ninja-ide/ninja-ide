# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject

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