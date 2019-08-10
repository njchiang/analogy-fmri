#!/bin/bash
:<<doc
activates analogy environment, if not it creates it
doc


if conda activate analogy; then
    echo "Environment loaded"
else
    echo "Creating environment"
    conda create -n analogy python=3.7
    pip install -r requirements.txt
fi