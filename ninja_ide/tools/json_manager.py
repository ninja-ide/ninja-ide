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

import os
import json

from ninja_ide import resources
from ninja_ide.core import settings

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.tools.json_manager')


def load_syntax():
    """Load all the syntax files."""

    files = os.listdir(resources.SYNTAX_FILES)
    for _file in files:
        name, file_extension = os.path.splitext(_file)
        if file_extension != ".json":
            continue
        filename = os.path.join(resources.SYNTAX_FILES, _file)
        structure = read_json(filename)
        if structure:
            settings.SYNTAX[name] = structure


def parse(descriptor):
    """Read the content of a json file and return a dict."""
    try:
        return json.loads(descriptor)
    except:
        logger.error("The file couldn't be parsed'")
        logger.error(descriptor)
    return {}


def read_json(path):
    """Read a json file if path is a file, or search for a .nja if folder."""
    structure = dict()
    fileName = None

    if os.path.isdir(path):
        json_file = get_ninja_json_file(path)
        fileName = os.path.join(path, json_file)

    if os.path.isfile(path):
        fileName = path

    if fileName is None:
        return structure

    with open(fileName, 'r') as fp:
        try:
            structure = json.load(fp)
        except Exception as exc:
            logger.error('Error reading Ninja File %s' % fileName)
            logger.error(exc)
            return structure

    return structure


def read_json_from_stream(stream):
    structure = json.load(stream)
    return structure


def write_json(structure, filename, indent=2):
    with open(filename, 'w') as fp:
        json.dump(structure, fp, indent)


def create_ninja_project(path, project, structure):
    projectName = project.lower().strip().replace(' ', '_') + '.nja'
    fileName = os.path.join(path, projectName)
    with open(fileName, mode='w') as fp:
        json.dump(structure, fp, indent=2)


def get_ninja_file(path, extension, only_first=False):
    """Search and return the files with extension in the folder: path."""
    files = os.listdir(path)
    if not extension.startswith('.'):
        extension = '.'.join(extension)

    found = list([y for y in files if y.endswith(extension)])

    if only_first:
        found = found[0] if found else []

    return found


def get_ninja_json_file(path):
    """Return the list of json files inside the directory: path."""
    extension = '.json'
    return get_ninja_file(path, extension, only_first=True)


def get_ninja_plugin_file(path):
    """Return the list of plugin files inside the directory: path."""
    extension = '.plugin'
    return get_ninja_file(path, extension, only_first=True)


def get_ninja_project_file(path):
    """Return the first nja file found inside: path."""
    extension = '.nja'
    return get_ninja_file(path, extension, only_first=True)


def get_ninja_editor_skins_files(path):
    """Return the list of json files inside the directory: path."""
    extension = '.json'
    return get_ninja_file(path, extension)


def read_ninja_project(path):
    empty = dict()
    project_file = get_ninja_project_file(path)

    if not project_file:
        return empty

    return read_json(os.path.join(path, project_file))


def read_ninja_plugin(path):
    empty = dict()
    plugin_file = get_ninja_plugin_file(path)

    if plugin_file is None:
        return empty

    return read_json(os.path.join(path, plugin_file))


def load_editor_schemes():
    skins = {}
    files = get_ninja_editor_skins_files(resources.EDITOR_SCHEMES)
    for fname in files:
        file_name = os.path.join(resources.EDITOR_SCHEMES, fname)
        structure = read_json(file_name)
        name = structure['name']
        skins[name] = structure

    return skins


def save_editor_skins(filename, scheme):
    with open(filename, 'w') as fp:
        try:
            json.dump(scheme, fp, indent=2)
        except Exception as exc:
            logger.error('Error writing file %s' % filename)
            logger.error(exc)
