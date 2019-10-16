#!/bin/bash
:<<doc
qsub \
    -o /u/project/monti/njchiang/code/analogy/jobs/output/ \
    -e /u/project/monti/njchiang/code/analogy/jobs/output/ \
    -V -N ab-encoding \
    -l h_data=8G,h_rt=23:59:59 -pe shared 2 \
    -M ${USER} -m bea \
    /u/project/monti/njchiang/code/analogy/analogy-fmri/analysis/scripts/submit/run_cd_rsa.sh

doc

echo "Script started"
. /u/home/n/njchiang/.bashrc
conda activate fmri
echo "environment activated"
returnHere=${PWD}
cd /u/project/monti/njchiang/code/analogy/analogy-fmri

for s in sub-01 sub-02 sub-03 sub-04 sub-05 sub-06 sub-07 sub-08 sub-09 sub-10 sub-11 sub-12 sub-13 sub-14 sub-15 sub-16
do
    python analysis/run_searchlight.py \
        --analysis=rsa \
        --phase=CD \
        --mask=graymatter-bin_mask \
        --sub=${s}
done

cd ${returnHere}