.PHONY: help clean docs tests packages

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean     to cleanup build and temporary files"
	@echo "  docs      to build the documentation"
	@echo "  tests     to run the test suite"
	@echo "  packages  to build python source and egg packages"

clean:
	@rm -rf build dist circuits.egg-info circuits/__version__.py
	@rm -rf .coverage coverage
	@rm -rf docs/build
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete

docs:
	@rm -rf docs/*
	@epydoc -v -n circuits -o docs/ \
		-u http://trac.softcircuit.com.au/circuits/ \
		--check --html --src-code-tab-width=4 --no-frames \
		--no-private --exclude=circuits.web._httpauth \
		--exclude=.*\.tests.* \
		--exclude=circuits\.__version__ \
		--exclude=circuits\.version \
		--no-sourcecode circuits

packages:
	@tools/mkpkgs -p python2.5
	@tools/mkpkgs -p python2.6

tests:
	@py.test -x --ignore=tmp \
		--pastebin=all \
		--report=skipped \
		--cover=circuits \
		--cover-report=html \
		--cover-directory=coverage \
		--cover-show-missing
