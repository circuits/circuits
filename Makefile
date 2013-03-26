.PHONY: help clean docs graph packages tests

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean     to cleanup build and temporary files"
	@echo "  docs      to build the documentation"
	@echo "  graph     to generate dependency graph"
	@echo "  packages  to build python source and egg packages"
	@echo "  tests     to run the test suite"

clean:
	@rm -rf build dist circuits.egg-info
	@rm -rf .coverage coverage
	@rm -rf docs/build
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete
	@rm -f *.xml

docs:
	@make -C docs html

graph:
	@sfood circuits -i -I tests -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > circuits.pdf

release:
	@python2.6 setup.py clean bdist_egg upload
	@python2.7 setup.py clean bdist_egg upload
	@python3.2 setup.py clean bdist_egg upload
	@python3.3 setup.py clean bdist_egg upload
	@python setup.py clean build_sphinx upload_sphinx
	@python setup.py clean sdist --formats=bztar,gztar,zip upload

tests:
	@python -m tests.main
