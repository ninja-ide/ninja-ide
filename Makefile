PYTEST = pytest -v -s
cleanUpList = *.pyc *.pyo *.qmlc *.jsc

help:
	@echo "unittest		-- run unit tests"
	@echo "pep8		-- run pycodestyle"
	@echo "flake8		-- run flake8"
	@echo "lint		-- run pycodestyle and flake8"
	@echo "rc		-- build resources"


unittest:
	$(PYTEST) ninja_tests/unit

pep8:
	pycodestyle ninja_ide

flake8:
	flake8 ninja_ide

lint: pep8 flake8

rc:
	pyrcc5 ninja_ide/nresources.qrc -o ninja_ide/nresources.py

clean:
	for i in $(cleanUpList); do find . -name "$$i" -delete; done