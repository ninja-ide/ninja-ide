# *-* coding: UTF-8 *-*

import os
import logging
try:
    import json
except ImportError:
    import simplejson as json

from ninja_ide import resources
from ninja_ide.core import settings


logger = logging.getLogger('ninja_ide.tools.json_manager')


def parse(descriptor):
    try:
        return json.load(descriptor)
    except:
        logger.error("The file couldn't be parsed'")
        logger.error(descriptor)
    return {}


def load_syntax():
    files = os.listdir(resources.SYNTAX_FILES)
    for f in files:
        if f.endswith('.json'):
            structure = None
            fileName = os.path.join(resources.SYNTAX_FILES, f)
            read = open(fileName, 'r')
            structure = json.load(read)
            read.close()
            name = f[:-5]
            settings.SYNTAX[name] = structure
            for ext in structure.get('extension'):
                if ext is not None:
                    settings.EXTENSIONS[ext] = name


def create_ninja_project(path, project, structure):
    fileName = os.path.join(path, project.replace(' ', '_') + '.nja')
    f = open(fileName, mode='w')
    json.dump(structure, f, indent=2)
    f.close()


def read_ninja_project(path):
    files = os.listdir(path)
    nja = filter(lambda y: y.endswith('.nja'), files)
    if len(nja) == 0:
        return {}
    structure = None
    fileName = os.path.join(path, nja[0])
    read = open(fileName, 'r')
    structure = json.load(read)
    read.close()
    return structure


def get_ninja_project_file(path):
    files = os.listdir(path)
    nja = filter(lambda y: y.endswith('.nja'), files)
    return nja[0] if nja else ''


def read_ninja_plugin(path):
    files = os.listdir(path)
    plugins = filter(lambda y: y.endswith('.plugin'), files)
    if len(plugins) == 0:
        return {}
    structure = None
    fileName = os.path.join(path, plugins[0])
    read = open(fileName, 'r')
    structure = json.load(read)
    read.close()
    return structure


def read_json(path):
    files = os.listdir(path)
    jsons = filter(lambda y: y.endswith('.json'), files)
    if len(jsons) == 0:
        return {}
    structure = None
    fileName = os.path.join(path, jsons[0])
    read = open(fileName, 'r')
    structure = json.load(read)
    read.close()
    return structure


def json_to_dict(fileName):
    structure = None
    if os.path.exists(fileName):
        read = open(fileName, 'r')
        structure = json.load(read)
        read.close()
    return structure


def load_editor_skins():
    files = os.listdir(resources.EDITOR_SKINS)
    skins = {}
    for f in files:
        if f.endswith('.color'):
            structure = None
            fileName = os.path.join(resources.EDITOR_SKINS, f)
            read = open(fileName, 'r')
            structure = json.load(read)
            read.close()
            name = unicode(f[:-6])
            skins[name] = structure
    return skins


def save_editor_skins(filename, scheme):
    f = open(filename, mode='w')
    json.dump(scheme, f, indent=2)
    f.close()
