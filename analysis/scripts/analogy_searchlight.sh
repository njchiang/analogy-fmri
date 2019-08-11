#!/bin/bash
:<<doc
wrapper for searchlight script
doc

opts=${1}

module load python/3.6.1
source /u/home/n/njchiang/virtualenvs/py36/bin/activate

runme="python /u/project/monti/Analysis/Analogy/code/analogy/fmri/run_searchlight.py ${opts}"

${runme}
