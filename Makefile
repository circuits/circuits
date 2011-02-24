.PHONY: help clean docs graph packages tests

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean     to cleanup build and temporary files"
	@echo "  docs      to build the documentation"
	@echo "  graph     to generate dependency graph"
	@echo "  packages  to build python source and egg packages"
	@echo "  tests     to run the test suite"

clean:
	@rm -rf build dist circuits.egg-info circuits/__version__.py
	@rm -rf .coverage coverage
	@rm -rf docs/build
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete

docs:
	@make -C docs html

graph:
	@sfood circuits -i -I tests -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > circuits.pdf

packages:
	@tools/mkpkgs -p python2.5
	@tools/mkpkgs -p python2.6

tests:
	@tools/runtests
