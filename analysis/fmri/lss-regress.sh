#!/bin/bash
:<<doc
This file runs LSS

input args: TSV file, column name for condition, template file
doc

# Load the job environment:
. /u/local/Modules/default/init/modules.sh
module use /u/project/CCN/apps/modulefiles
module load python/3.6.1
module load fsl

export NO_FSL_JOBS=true


projectdir=/u/project/monti/Analysis/Analogy/derivatives
cd ${projectdir}


sub=${1}
run=${2}
mkdir ${sub}/misc/regressors/LSS

vol=`fslval ${sub}/func/${sub}_task-analogy_${run}_bold dim4`
python3 ~/scripts/setup-lss.py ${sub} ${run} ${vol}

# need to figure out how many
njobs=`more ${sub}/betas/${sub}_${run}_LSS-list.txt | wc -l`

# submit to grid
cd ~/job-output
qsub -cwd -N ${sub}_${run}_LSS -l h_rt=12:00:00,h_data=4G \
-pe shared 4 -m a \
-t 1:${njobs}:1 jobarray.sh feat \
/u/project/monti/Analysis/Analogy/derivatives/${sub}/betas/${sub}_${run}_LSS-list.txt

# collect when done
