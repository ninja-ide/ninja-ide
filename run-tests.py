#!/usr/bin/python3
import sys
import pytest
# Create dirs structure before run tests
from ninja_ide import resources
resources.create_home_dir_structure()


def main(path):
    if path is None:
        # Run all tests
        path = 'ninja_tests'
    errno = pytest.main(['-x', path, '-vv'])
    if errno != 0:
        raise SystemExit(errno)


if __name__ == '__main__':
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
    main(path)