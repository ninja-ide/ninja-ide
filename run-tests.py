#!/usr/bin/env python3
import sys
import os
import pytest
# Create dirs structure before run tests
from ninja_ide import resources
resources.create_home_dir_structure()


IN_CI = os.getenv('CI', None) is not None


def main(path):
    if path is None:
        path = 'ninja_tests'
    args = '{path} -vv'.format(path=path)
    if IN_CI:
        args += ' -x --cov=ninja_ide --no-cov-on-fail'

    errno = pytest.main(args.split())
    if errno != 0:
        raise SystemExit(errno)


if __name__ == '__main__':
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
    main(path)