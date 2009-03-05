.PHONY: all graphs

all: graphs

graphs:
	@sfood ../../circuits -I tests -I lib/web/tests -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > all.pdf
	@sfood ../../circuits -i -I tests -I lib -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > circuits.pdf
	@sfood ../../circuits/lib/drivers/ -i -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > drivers.pdf
	@sfood ../../circuits/lib/ -i -I drivers -I web -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > lib.pdf
	@sfood ../../circuits/lib/web/ -i -I tests -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > web.pdf
