#!/bin/bash
:<<doc
qsub \
    -o /u/project/monti/njchiang/code/analogy/jobs/output/ \
    -e /u/project/monti/njchiang/code/analogy/jobs/output/ \
    -V -N ab-encoding \
    -l h_data=8G,h_rt=23:59:59 -pe shared 2 \
    -M ${USER} -m bea \
    /u/project/monti/njchiang/code/analogy/analogy-fmri/analysis/scripts/submit/run_ab_encoding.sh

doc

echo "Script started"
. /u/home/n/njchiang/.bashrc
conda activate fmri
echo "environment activated"
returnHere=${PWD}
cd /u/project/monti/njchiang/code/analogy/analogy-fmri
python analysis/run_encoding.py \
  --phase=AB \
  --cv=relation \
  --n_folds=4 \
  --permutations=500 \
  --average
  # --threads=16
  # --n_folds=4 \
cd ${returnHere}