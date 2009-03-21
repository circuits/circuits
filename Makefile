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
	@rm -rf docs/html/
	@epydoc -v -n circuits -o docs/html/ \
		-u http://trac.softcircuit.com.au/circuits/ \
		--check --html --src-code-tab-width=4 --no-frames \
		--no-private --exclude=circuits.web._httpauth \
		--exclude=.*\.tests.* \
		--exclude=circuits\.__version__ \
		--exclude=circuits\.version \
		--no-sourcecode circuits

tests:
	@nosetests \
		--with-coverage \
		--cover-package=circuits \
		--cover-erase \
		--cover-inclusive \
		--with-doctest
