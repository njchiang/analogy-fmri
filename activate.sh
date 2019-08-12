#!/bin/bash
:<<doc
activates analogy environment, if not it creates it
doc

. /u/local/Modules/default/init/modules.sh
module load python/anaconda3
. /u/local/apps/anaconda3/etc/profile.d/conda.sh

if conda activate /u/home/n/njchiang/.conda/envs/analogy; then
    echo "Environment loaded"
else
    echo "Creating environment"
    conda create -n analogy python=3.7
    conda activate analogy
    pip install -r requirements.txt
fi