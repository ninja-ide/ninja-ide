PYTEST = pytest tests

help:
	@echo "pep8		-- run pycodestyle"
	@echo "flake8		-- run flake8"
	@echo "lint		-- run pycodestyle and flake8"
	@echo "rc		-- build resources"


pep8:
	pycodestyle ninja_ide

flake8:
	flake8 ninja_ide

lint: pep8 flake8

rc:
	pyrcc5 ninja_ide/nresources.qrc -o ninja_ide/nresources.py
