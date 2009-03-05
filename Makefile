.PHONY: all clean checks tests docs

all: clean checks tests docs

clean:
	@rm -rf build dist circuits.egg-info
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete

checks:
	@find . -name "*.py" -exec pyflakes {} +

docs:
	@epydoc -v -n circuits -o docs/html/ \
		--check --html --graph=classtree \
		--src-code-tab-width=4 --no-frames \
		--no-private --exclude=.*\.tests.* \
		--no-sourcecode circuits

tests:
	@nosetests \
		--with-coverage \
		--cover-package=circuits \
		--cover-erase \
		--cover-inclusive \
		--with-doctest
