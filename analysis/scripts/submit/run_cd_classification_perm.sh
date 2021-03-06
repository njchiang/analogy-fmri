#!/bin/bash
:<<doc
qsub \
    -o /u/project/monti/njchiang/code/analogy/jobs/output/ \
    -e /u/project/monti/njchiang/code/analogy/jobs/output/ \
    -V -N ab-encoding \
    -l h_data=8G,h_rt=23:59:59 -pe shared 2 \
    -M ${USER} -m bea \
    /u/project/monti/njchiang/code/analogy/analogy-fmri/analysis/scripts/submit/run_ab_classification.sh

doc

echo "Script started"
. /u/home/n/njchiang/.bashrc
conda activate fmri
echo "environment activated"
returnHere=${PWD}
cd /u/project/monti/njchiang/code/analogy/analogy-fmri

python analysis/run_searchlight.py \
    --analysis=cvsl \
    --phase=CD \
    --mask=graymatter-bin_mask \
    --sub=${1} \
    --permutations=30

cd ${returnHere}