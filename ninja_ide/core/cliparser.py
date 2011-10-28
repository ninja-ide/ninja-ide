# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys

import ninja_ide


usage = "$python ninja-ide.py <option, [option3...option n]>"

epilog = "This program comes with ABSOLUTELY NO WARRANTY." + \
    "This is free software, and you are welcome to redistribute " + \
    "it under certain conditions; for details see LICENSE.txt."

try:
    import argparse

    new_parser = True

    def _get_parser():
        global usage
        global epilog

        parser = argparse.ArgumentParser(description=usage, epilog=epilog)

        parser.add_argument('file', metavar='file', type=unicode,
            nargs='*', help='A file/s to edit', default=[])
        parser.add_argument('-f', '--files', metavar='file', type=unicode,
            nargs='+', help='A file/s to edit', default=[])
        parser.add_argument('-p', '--project', metavar='project', type=unicode,
            nargs='+', help='A project/s to edit', default=[])
        parser.add_argument('--plugin',
            metavar='plugin', type=unicode,
            nargs='+', help='A plugin to load', default=[])

        return parser

except:
    import optparse

    new_parser = False

    def _resolve_nargs(*opts):
        final_nargs = 1
        for opt in opts:
            nargs = 0
            try:
                start = sys.argv.index(opt) + 1
                for idx, arg in enumerate(sys.argv[start:]):
                    if str(arg).startswith("-"):
                        break
                    nargs += 1
                return nargs
            except ValueError:
                nargs = 1
            if final_nargs < nargs:
                final_nargs = nargs
        return final_nargs

    def _get_parser():
        global usage
        global epilog

        parser = optparse.OptionParser(usage, version=ninja_ide.__version__,
            epilog=epilog)

        parser.add_option("-f", "--file",
            type="string",
            action="store",
            dest="file",
            default=[],
            help="A file/s to edit",
            nargs=_resolve_nargs("-f", "--file"))

        parser.add_option("-p", "--project",
            type="string",
            action="store",
            dest="project",
            default=[],
            help="A project/s to edit",
            nargs=_resolve_nargs("-p", "--project"))

        parser.add_option("--plugin",
            type="string",
            action="store",
            dest="plugin",
            default=[],
            help="A plugin to load",
            nargs=_resolve_nargs("--plugin"))

        return parser


def parse():
    filenames = None
    projects_path = None
    extra_plugins = None
    try:
        if new_parser:
            opts = _get_parser().parse_args()
        else:
            opts = _get_parser().parse_args()[0]

        filenames = opts.file \
            if isinstance(opts.file, list) \
            else [opts.file]
        filenames += opts.files \
            if hasattr(opts, 'files') \
            else []
        projects_path = opts.project \
            if isinstance(opts.project, list) \
            else  [opts.project]
        extra_plugins = opts.plugin \
            if isinstance(opts.plugin, list) \
            else  [opts.plugin]
    except Exception, reason:
        print "Args couldn't be parsed."
        print reason
    return filenames, projects_path, extra_plugins
