#!/bin/bash
:<<doc
temporary script for registering masks from standard to subject directories
doc

mask=${1}
name=${2}
cd /u/project/monti/Analysis/Analogy/derivatives

for s in sub-*
do
echo "Registering ${mask} to ${s}"
flirt -in standard/masks/${mask}.nii.gz -ref ${s}/reg/BOLD_template -out ${s}/masks/${name} -applyxfm -init ${s}/reg/standard_to_BOLD_template.mat
fslmaths ${s}/masks/${name} -bin ${s}/masks/${name}
done
