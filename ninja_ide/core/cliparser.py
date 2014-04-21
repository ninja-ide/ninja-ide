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


from __future__ import absolute_import

import argparse


try:
    # For Python2
    str = unicode  # lint:ok
except NameError:
    # We are in Python3
    pass

usage = "$python ninja-ide.py <option, [option3...option n]>"

epilog = ("This program comes with ABSOLUTELY NO WARRANTY."
          "This is free software, and you are welcome to redistribute "
          "it under certain conditions; for details see LICENSE.txt.")


def _get_parser():
    global usage, epilog

    parser = argparse.ArgumentParser(description=usage, epilog=epilog)

    parser.add_argument('file', metavar='file', type=str,
                        nargs='*', help='A file/s to edit', default=[])
    parser.add_argument('-f', '--files', metavar='file', type=str,
                        nargs='+', help='A file/s to edit', default=[])
    parser.add_argument('-l', '--lineno', metavar='lineno', type=int,
                        nargs='+', help='Line number for the files to open',
                        default=[])
    parser.add_argument('-p', '--project', metavar='project', type=str,
                        nargs='+', help='A project/s to edit', default=[])
    parser.add_argument('--plugin', metavar='plugin', type=str,
                        nargs='+', help='A plugin to load', default=[])
    parser.add_argument(
        '--loglevel', help="Level to use for logging, "
        "one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'",
        default=None, metavar="loglevel")
    parser.add_argument('--logfile', help="A file path to log, special "
                        "words STDOUT or STDERR are accepted",
                        default=None, metavar="logfile")
    return parser


def parse():
    filenames = projects_path = linenos = None
    extra_plugins = log_level = log_file = None

    try:
        opts = _get_parser().parse_args()

        filenames = opts.file \
            if isinstance(opts.file, list) \
            else [opts.file]
        filenames += opts.files \
            if hasattr(opts, 'files') \
            else []
        projects_path = opts.project \
            if isinstance(opts.project, list) \
            else [opts.project]
        linenos = opts.lineno \
            if hasattr(opts, 'lineno') \
            else [opts.lineno]
        extra_plugins = opts.plugin \
            if isinstance(opts.plugin, list) \
            else [opts.plugin]
        log_level = opts.loglevel
        log_file = opts.logfile

    except Exception as reason:
        print("Args couldn't be parsed.")
        print(reason)
    return (filenames, projects_path, extra_plugins, linenos, log_level,
            log_file)
