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


def parse(descriptor):
    try:
        return json.load(descriptor)
    except:
        logger.error("The file couldn't be parsed'")
        logger.error(descriptor)
    return {}


def read_json(arg_):

    structure = dict()
    fileName = None

    if os.path.isdir(arg_):
        path = arg_
        json_file = get_ninja_json_file(path)
        fileName = os.path.join(path, json_file)

    if os.path.isfile(arg_):
        fileName = arg_

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


def load_syntax():

    empty = dict()
    files = os.listdir(resources.SYNTAX_FILES)

    for f in files:

        if not f.endswith('.json'):
            continue

        fname = os.path.join(resources.SYNTAX_FILES, f)
        structure = read_json(fname)
        if structure == empty:
            continue

        name = f[:-5]
        settings.SYNTAX[name] = structure
        for ext in structure.get('extension'):
            if ext is not None:
                settings.EXTENSIONS[ext] = name


def create_ninja_project(path, project, structure):
    projectName = project.lower().strip().replace(' ', '_') + '.nja'
    fileName = os.path.join(path, projectName)
    with open(fileName, mode='w') as fp:
        json.dump(structure, fp, indent=2)


def get_ninja_file(path, extension, only_first=False):
    files = os.listdir(path)
    if not extension.startswith('.'):
        extension = '.'.join(extension)

    nja = list([y for y in files if y.endswith(extension)])

    if only_first:
        nja = nja[0] if nja else None

    return nja if nja else []


def get_ninja_json_file(path):

    extension = '.json'
    return get_ninja_file(path, extension, only_first=True)


def get_ninja_plugin_file(path):

    extension = '.plugin'
    return get_ninja_file(path, extension, only_first=True)


def get_ninja_project_file(path):

    extension = '.nja'
    return get_ninja_file(path, extension, only_first=True)


def get_ninja_editor_skins_files(path):

    extension = '.color'
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


def load_editor_skins():

    skins = dict()
    files = get_ninja_editor_skins_files(resources.EDITOR_SKINS)

    for fname in files:
        file_name = os.path.join(resources.EDITOR_SKINS, fname)
        structure = read_json(file_name)
        if structure is None:
            continue
        name = fname[:-6]
        skins[name] = structure

    return skins


def save_editor_skins(filename, scheme):

    with open(filename, 'w') as fp:
        try:
            json.dump(scheme, fp, indent=2)
        except Exception as exc:
            logger.error('Error writing file %s' % filename)
            logger.error(exc)
