#!/bin/bash
:<<doc
qsub \
    -o /u/project/monti/njchiang/code/analogy/jobs/output/ \
    -e /u/project/monti/njchiang/code/analogy/jobs/output/ \
    -V -N ab-encoding \
    -l h_data=8G,h_rt=23:59:59 -pe shared 4 \
    -M ${USER} -m bea \
    /u/project/monti/njchiang/code/analogy/analogy-fmri/analysis/scripts/submit/run_ab_encoding.sh

doc

echo "Script started"
. ${HOME}/.bashrc
conda activate fmri
echo "environment activated"
python /u/project/monti/njchiang/code/analogy/analogy-fmri/analysis/run_encoding.py --phase=AB