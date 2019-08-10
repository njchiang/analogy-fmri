#!/bin/bash
:<<doc
activates analogy environment, if not it creates it
doc



if source /u/local/apps/anaconda3/bin/activate analogy; then
    echo "Environment loaded"
else
    echo "Creating environment"
    # conda create -n analogy python=3.7
    # /u/local/apps/anaconda3/bin/activate analogy
    # pip install -r requirements.txt
fi