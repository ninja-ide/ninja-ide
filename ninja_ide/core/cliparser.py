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
"""
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute
it under certain conditions; for details see LICENSE.txt.
"""

import argparse

USAGE = "$python ninja-ide.py <option, [option3...option n]>"


def _get_parser():
    parser = argparse.ArgumentParser(description=__doc__)

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
        '-v',
        '--verbose',
        action='count',
        default=1,
        help='Level to use for logging (-v -vv -vvvv)'
    )
    parser.add_argument('--logfile', help="A file path to log, special "
                        "words STDOUT or STDERR are accepted",
                        default=None, metavar="logfile")
    return parser


def parse():
    filenames = projects_path = linenos = None
    extra_plugins = log_level = log_file = None

    try:
        args = _get_parser().parse_args()

        filenames = args.file \
            if isinstance(args.file, list) \
            else [args.file]
        filenames += args.files \
            if hasattr(args, 'files') \
            else []
        projects_path = args.project \
            if isinstance(args.project, list) \
            else [args.project]
        linenos = args.lineno \
            if hasattr(args, 'lineno') \
            else [args.lineno]
        extra_plugins = args.plugin \
            if isinstance(args.plugin, list) \
            else [args.plugin]
        log_level = 40 - (10 * args.verbose) if args.verbose > 0 else 0
        log_file = args.logfile

    except Exception as reason:
        print("Args couldn't be parsed.")
        print(reason)
    return (filenames, projects_path, extra_plugins, linenos, log_level,
            log_file)
