#!/bin/bash
:<<doc
runs sed on univariate analysis
doc

module load fsl
for s in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16
do
  sub=sub-${s}
  for r in 01 02 03 04 05 06 07 08
  do

    run=run-${r}
    vol=`fslval /u/project/monti/Analysis/Analogy/data/${sub}/func/${sub}_task-analogy_${run}_bold dim4`
    echo ${sub} ${run} ${vol}
    sed -e "s/###SUB###/${sub}/g" -e "s/###RUN###/${run}/g" -e "s/###VOL###/${vol}/g"  /u/project/monti/Analysis/Analogy/derivatives/standard/templates/univariate_mainrel_sep.fsf > /u/project/monti/Analysis/Analogy/derivatives/${sub}/misc/des/${sub}_${run}_univariate_mainrel_sep.fsf
  done
done

