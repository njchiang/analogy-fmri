#!/bin/bash
:<<doc
cp raw TS and remove sourcedata
doc
sub=${1}
cd ~/data/fmri/Analogy

while read line
do
	orig_name=`echo ${line} | cut -d ',' -f1`
	target=`echo ${line} | cut -d ',' -f2`
	if [ $target == "T1w" ]
	then
		echo ${target}
		rm data/${sub}/anat/${sub}_T1w.nii.gz
		cp sourcedata/${sub}/${orig_name}/${orig_name}.nii.gz data/${sub}/anat/${sub}_${target}.nii.gz
		cp sourcedata/${sub}/${orig_name}/${orig_name}.bids data/${sub}/anat/${sub}_${target}.json
	elif [ $target == "gre" ]
	then
		echo ${target}
		rm data/${sub}/fmap/${sub}_gre.nii.gz
		cp sourcedata/${sub}/${orig_name}/${orig_name}_c0_2.nii.gz data/${sub}/fmap/${sub}_${target}.nii.gz
		cp sourcedata/${sub}/${orig_name}/${orig_name}_c0_2.bids data/${sub}/fmap/${sub}_${target}.json
	else
		echo ${target}
		rm data/${sub}/func/${sub}_task-analogy_${target}_bold.nii.gz
		cp sourcedata/${sub}/${orig_name}/${orig_name}.nii.gz data/${sub}/func/${sub}_task-analogy_${target}_bold.nii.gz
		cp sourcedata/${sub}/${orig_name}/${orig_name}.bids data/${sub}/func/${sub}_task-analogy_${target}_bold.json
	fi
done < sourcedata/${sub}/filemapping.txt	

