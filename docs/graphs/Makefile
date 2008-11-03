.PHONY: all graphs

all: graphs

graphs:
	@sfood ../../circuits -i -I tests -I lib -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > circuits.pdf
	@sfood ../../circuits/lib/ -i -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > lib.pdf
	@sfood ../../circuits/tests/ -i -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > tests.pdf
