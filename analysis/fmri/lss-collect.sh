#!/bin/bash
:<<doc
This file collects LSS and cleans up

input args: TSV file, column name for condition, template file
doc

# Load the job environment:
# module load fsl

# export NO_FSL_JOBS=true


projectdir=/u/project/monti/Analysis/Analogy/derivatives
sub=${1}
run=${2}

cd ${projectdir}/${sub}


### CUSTOM FOR THIS PROJECT ###
# create registration using first beta
cp betas/LSS/${sub}_${run}_AB-1.feat/example_func.nii.gz reg/${run}_middle-template.nii.gz
flirt -in reg/${run}_middle-template.nii.gz -ref reg/BOLD_template.nii.gz \
-omat reg/${run}_middle-to-template.nii.gz

for t in {1..36}
do
  for tt in AB CD Probe
  do
      for c in cope varcope tstat
      do
        if [ ! -f betas/LSS/${sub}_${run}_${tt}-${t}_${c}.nii.gz ]
        then
          # register cope, tstat, varcope
           flirt -in betas/LSS/${sub}_${run}_${tt}-${t}.feat/stats/${c}1 \
            -out betas/LSS/${sub}_${run}_${tt}-${t}_${c} \
            -ref reg/BOLD_template \
            -applyxfm -init reg/${run}_middle-to-template.nii.gz
        fi
      done

      # delete original folder
      if [ -d betas/LSS/${sub}_${run}_${tt}-${t}.feat ] && \
      [ -f betas/LSS/${sub}_${run}_${tt}-${t}_cope.nii.gz ] && \
      [ -f betas/LSS/${sub}_${run}_${tt}-${t}_varcope.nii.gz ] && \
      [ -f betas/LSS/${sub}_${run}_${tt}-${t}_tstat.nii.gz ]
      then
        rm -rf betas/LSS/${sub}_${run}_${tt}-${t}.feat
      fi

  done
  copelist="${copelist} ${sub}_${run}_AB-${t}_cope ${sub}_${run}_CD-${t}_cope ${sub}_${run}_Probe-${t}_cope"
  varcopelist="${varcopelist} ${sub}_${run}_AB-${t}_varcope ${sub}_${run}_CD-${t}_varcope ${sub}_${run}_Probe-${t}_varcope"
  tstatlist="${tstatlist} ${sub}_${run}_AB-${t}_tstat ${sub}_${run}_CD-${t}_tstat ${sub}_${run}_Probe-${t}_tstat"

done

# merge
cd betas/LSS
fslmerge -t ../${sub}_task-analogy_${run}_betas-cope-LSS ${copelist}
fslmerge -t ../${sub}_task-analogy_${run}_betas-tstat-LSS ${tstatlist}
fslmerge -t ../${sub}_task-analogy_${run}_betas-varcope-LSS ${varcopelist}
