#!/bin/bash
cd /u/project/monti/Analysis/Analogy/analysis

chance=0.50  # 0.34
betatype=lss

for m in CD-Match-cvsl # ABMainRel-cvsl
do
  echo ${m}
  for s in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16
  do
    echo sub-${s}
    flirt -in sub-${s}/multivariate/searchlight/lss/sub-${s}_${m}.nii.gz -out group/multivariate/searchlight/${betatype}/sub-${s}-${m}.nii.gz -ref ../derivatives/standard/MNI152_T1_2mm_brain.nii.gz -applyxfm -init ../derivatives/sub-${s}/reg/BOLD_template_to_standard.mat
    fslmaths group/multivariate/searchlight/${betatype}/sub-${s}-${m} -bin -mul ${chance} group/multivariate/searchlight/${betatype}/chance
    fslmaths group/multivariate/searchlight/${betatype}/sub-${s}-${m} -sub group/multivariate/searchlight/${betatype}/chance group/multivariate/searchlight/${betatype}/sub-${s}-${m}
    rm group/multivariate/searchlight/${betatype}/chance.nii.gz
  done
  fslmerge -t group/multivariate/searchlight/${betatype}/group-${m}.nii.gz group/multivariate/searchlight/${betatype}/sub*-${m}.nii.gz
#   fslmaths analysis/multivariate/searchlight/lss/group-${m}.nii.gz -sub 0.3334 analysis/multivariate/searchlight/lss/group-${m}.nii.gz
  rm group/multivariate/searchlight/${betatype}/sub*-${m}.nii.gz
done
