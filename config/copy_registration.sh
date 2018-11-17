#!/bin/bash
:<<doc
just copies Run1_template_to_standard to BOLD_to_standard.mat for easy postprocessing

doc

projectdir=~/data/fmri/Analogy/
cd ${projectdir}/data
for s in analogy*
do
cp ${s}/analysis/reg/Run1_template_to_standard.mat ${s}/analysis/reg/BOLD_template_to_standard.mat

done