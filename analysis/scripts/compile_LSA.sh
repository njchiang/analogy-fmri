#!/bin/bash
:<<doc
This file takes outputs from a FEAT directory and concatenates them into a beta file.
doc

projectdir=/u/project/monti/Analysis/Analogy/derivatives
cd $projectdir

while read line
do
  copelist="${copelist} ${line}.nii.gz"
done < ${projectdir}/standard/misc/copelist.txt

while read line
do
  tstatlist="${tstatlist} ${line}.nii.gz"
done < i${projectdir}/standard/misc/tstatlist.txt

for s in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16
do
  for r in 01 02 03 04 05 06 07 08
  do
    cd $projectdir/sub-${s}/betas/sub-${s}_task-analogy_run-${r}_LSA.feat/stats
    fslmerge -t $projectdir/sub-${s}/func/sub-${s}_task-analogy_run-${r}_betas-LSA-cope.nii.gz ${copelist}
    fslmerge -t $projectdir/sub-${s}/func/sub-${s}_task-analogy_run-${r}_betas-LSA-tstat.nii.gz ${tstatlist}
    ln -s ${projectdir}/sub-${s}/betas/sub-${s}_task-analogy_run-${r}_LSA.feat/resids.nii.gz ${projectdir}/sub-${s}/betas/sub-${s}_task-analogy_run-${r}_resids-LSA.nii.gz
    ln -s ${projectidr}/sub-${s}/betas/sub-${s}_task-analogy_run-${r}_LSA.feat/resids.nii.gz ${projectdir}/sub-${s}/func/sub-${s}_task-analogy_run-${r}_resids-LSA.nii.gz
    # cp ../resids.nii.gz $projectdir/sub-${s}/func/sub-${s}_task-analogy_run-${r}_resids-LSA.nii.gz
  done
  # fslmerge betas per run to betas
done

