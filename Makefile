.PHONY: help prepare-env test preprocess searchlight-mvpa searchlight-rsa dummy-setup

# ROOT?=/u/project/monti/Analysis/Analogy
SHELL=/bin/bash
CONDAROOT=/u/local/apps/anaconda3/bin/activate
ROOT?=/tmp/Analogy
# DATA?=${ROOT}/data
# DERIVATIVES?=${ROOT}/derivatives
# ANALYSIS?=${ROOT}/analysis

DATA=$(wildcard ${ROOT}/data/sub-??)
# replace data with derivatives
DERIVATIVES=$(DATA:$(ROOT)/data/%=$(ROOT)/derivatives/%)
ANALYSIS=$(DERIVATIVES:$(ROOT)/derivatives/%=$(ROOT)/analysis/%)


.DEFAULT: help
help:
	@echo "make prepare-env: create or activate conda environment"
	@echo "make test: run tests"
	@echo "make searchlight-mvpa: run searchlight classification"
	@echo "make preprocess: run preprocessing"
	@echo "make dummy-setup: set up dummy environment for testing paths"

prepare-env:
	. activate.sh
	touch prepare-env

test: prepare-env
	conda info --envs
	. run_tests.sh

# searchlight-mvpa: prepare-env scripts/run_ab_searchlight.py

#####################
preprocess: prepare-env

test-searchlight-mvpa: prepare-env
	python analysis/run_searchlight.py -m graymatter-bin_mask -s sub-01 -d

test-searchlight-rsa: prepare-env
	python analysis/run_searchlight.py -m graymatter-bin_mask -s sub-01 -a rsa -d

.PHONY: clean
clean:
	rm -f test prepare-env preprocess dummy-setup dummy-files searchlight-mvpa help

### DUMMY TESTING ###

.PHONY: echo
echo:
	@echo "here"

.PHONY: dummy-setup
dummy-setup:
	mkdir -p ${ROOT}/data/sub-00
	mkdir -p ${ROOT}/data/sub-01
	mkdir -p ${ROOT}/derivatives
	mkdir -p ${ROOT}/analysis

# get this to work...
dummy-files: $(DERIVATIVES)
# dummy-files: dummy-setup $(DERIVATIVES)
# 	make dummy-setup
# 	make $(DERIVATIVES)

.PHONY: dummy-run
dummy-run:
	make dummy-setup
	make dummy-files

# Preprocessing can probably go here
$(ROOT)/derivatives/%: $(ROOT)/data/%
	cp -r ${ROOT}/data/$* ${ROOT}/derivatives/$*
	make echo
	# PREPROCESSING SCRIPT
	mkdir -p ${ROOT}/analysis/$*
	make echo

$(ROOT)/analysis/%: $(ROOT)/derivatives/%
	cp -r ${ROOT}/data/$* ${ROOT}/derivatives/$*
	make echo
	# ANALYSIS SCRIPT
	mkdir -p ${ROOT}/analysis/$*
	make echo

######################
#