.PHONY: help prepare-env test

.DEFAULT: help
help:
	@echo "make prepare-env: create or activate conda environment"
	@echo "make test: run tests"

prepare-env: activate.sh
	bash activate.sh

test: prepare-env run_tests.sh
	bash run_tests.sh

.PHONY: clean
clean:
	rm -f test prepare-env help