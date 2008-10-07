.PHONY: all clean checks tests docs

all: clean checks tests docs

clean:
	@rm -rf build dist circuits.egg-info
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete

checks:
	@find . -name "*.py" -exec pyflakes {} +

tests:
	@nosetests

docs:
	@sfood circuits -i -I tests -I lib -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > docs/graphs/circuits.pdf
	@sfood circuits/lib/ -i -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > docs/graphs/lib.pdf
