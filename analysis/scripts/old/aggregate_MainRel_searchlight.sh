#!/bin/bash
cd /u/project/monti/Analysis/Analogy/analysis

chance=0.334
betatype=lss

for m in AB-cvsl CDMatch-MainRel-cvsl
do
  echo ${m}
  for s in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16
  do
    echo sub-${s}
    fslmaths sub-${s}/multivariate/searchlight/${betatype}/sub-${s}_${m} -Tmean group/multivariate/searchlight/${betatype}/sub-${s}-${m}
    flirt -in group/multivariate/searchlight/${betatype}/sub-${s}-${m}.nii.gz -out group/multivariate/searchlight/${betatype}/sub-${s}-${m}.nii.gz -ref ../derivatives/standard/MNI152_T1_2mm_brain.nii.gz -applyxfm -init ../derivatives/sub-${s}/reg/BOLD_template_to_standard.mat
    fslmaths group/multivariate/searchlight/${betatype}/sub-${s}-${m} -bin -mul ${chance} group/multivariate/searchlight/${betatype}/chance
    fslmaths group/multivariate/searchlight/${betatype}/sub-${s}-${m} -sub group/multivariate/searchlight/${betatype}/chance group/multivariate/searchlight/${betatype}/sub-${s}-${m}
    rm group/multivariate/searchlight/${betatype}/chance.nii.gz
  done
  fslmerge -t group/multivariate/searchlight/${betatype}/group-${m}.nii.gz group/multivariate/searchlight/${betatype}/sub*-${m}.nii.gz
#   fslmaths analysis/multivariate/searchlight/lss/group-${m}.nii.gz -sub 0.3334 analysis/multivariate/searchlight/lss/group-${m}.nii.gz
  rm group/multivariate/searchlight/${betatype}/sub*-${m}.nii.gz
done
