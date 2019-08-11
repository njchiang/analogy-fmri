#!/bin/bash
cd /u/project/monti/Analysis/Analogy/
m=graymatter-bin_mask
echo ${m}
mkdir analysis/group/multivariate/rsa/split
for s in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16
do
  echo sub-${s}
  flirt -in analysis/sub-${s}/multivariate/rsa/sub-${s}_${m}_CD_corr_rsaSearchlight.nii.gz \
  -out analysis/group/multivariate/rsa/sub-${s}_${m}_CD_rsaSearchlight.nii.gz \
  -ref derivatives/standard/MNI152_T1_2mm_brain.nii.gz \
  -applyxfm -init derivatives/sub-${s}/reg/BOLD_template_to_standard.mat
  fslsplit analysis/group/multivariate/rsa/sub-${s}_${m}_CD_rsaSearchlight.nii.gz analysis/group/multivariate/rsa/split/sub-${s}_
done
# fslmerge -t analysis/group/multivariate/rsa/group_${m}_AB.nii.gz analysis/group/multivariate/rsa/sub*_${m}_AB_rsaSearchlight.nii.gz

fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_design analysis/group/multivariate/rsa/split/*0000.nii.gz 
fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_nChars analysis/group/multivariate/rsa/split/*0001.nii.gz 
fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_w2vDiff analysis/group/multivariate/rsa/split/*0002.nii.gz 
fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_w2vConcat analysis/group/multivariate/rsa/split/*0003.nii.gz 
fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_BART9 analysis/group/multivariate/rsa/split/*0004.nii.gz 
fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_BART79 analysis/group/multivariate/rsa/split/*0005.nii.gz 
# fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_designAndBART9 analysis/group/multivariate/rsa/split/*0006.nii.gz 
# fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_designAndw2vDiff analysis/group/multivariate/rsa/split/*0007.nii.gz 
# fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_designAndw2vConcat analysis/group/multivariate/rsa/split/*0008.nii.gz 
# fslmerge -t analysis/group/multivariate/rsa/group_gm_CDMatch_BART9Andw2vConcat analysis/group/multivariate/rsa/split/*0009.nii.gz 

rm analysis/group/multivariate/rsa/sub*_${m}_CD_rsaSearchlight.nii.gz
rm -r analysis/group/multivariate/rsa/split

