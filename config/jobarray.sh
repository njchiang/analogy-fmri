#!/bin/bash
:<<doc
script template for job array
reads in subject list
doc

cmdfile=${1}
sublist=${2}

# load job environment
. /u/local/Modules/default/init/modules.sh
module use /u/project/CCN/apps/modulefiles

# Setup FSL
module load fsl
export NO_FSL_JOBS=true

# set up array list
readarray -t subjects < $sublist
(( i=$SGE_TASK_ID - 1 ))

echo "This is sub-job $SGE_TASK_ID"
echo "This is subject ${subjects[$i]}"

${cmdfile} ${subjects[$i]}



