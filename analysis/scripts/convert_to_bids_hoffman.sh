#!/bin/bash
:<<doc
This file converts the analogy project to BIDS format, symlinking raw data from the Data directory
doc

# which subject
s=${1}
taskname=analogy
ROOTDIR=/u/project/monti/Analysis/Analogy
cd ${ROOTDIR}

origSub=analogy0${s}  # original subject name
newSub=sub-${s}  # new subject name
echo "Moving ${origSub} to ${newSub} "

echo "creating directory in sourcedata"

mkdir -p sourcedata/${newSub}

echo "moving raw data"
mv data/${origSub}/raw/* sourcedata/${newSub}/  # in case permissions issues are a problem
mv data/${origSub}/dicom.tar.gz sourcedata/${newSub}/  # move dicom
mv sourcedata/${origSub}_behav/* sourcedata/${newSub}  # move regressors


# rm -r sourcedata/${origSub}_behav # if the transfer worked
echo "Modifying filemapping (with backup)"
cp sourcedata/${newSub}/filemapping.txt sourcedata/${newSub}/filemapping.bac  # backup filemapping because sed will run next
sed -e "s/,Run/,run-0/g" -e "s/,T1/,T1w/g" -e "s/,fieldmaps/,phasediff/g" -i sourcedata/${newSub}/filemapping.txt  #change "RunX" to "run-0X"

echo "Creating data directories"
mkdir -p data/${newSub}/anat  # create subject directories
mkdir -p data/${newSub}/func
mkdir -p data/${newSub}/fmap

echo "Linking and copying raw data"
# prepare raw data
while read line
do
	orig_name=`echo ${line} | cut -d ',' -f1`
	target=`echo ${line} | cut -d ',' -f2`
	if [ $target == "T1w" ]
	then
		echo ${target}
		ln -s sourcedata/${newSub}/${orig_name}/${orig_name}.nii.gz sourcedata/${newSub}/${newSub}_${target}.nii.gz
		ln -s sourcedata/${newSub}/${orig_name}/${orig_name}.bids sourcedata/${newSub}/${newSub}_${target}.json
		cp sourcedata/${newSub}/${orig_name}/${orig_name}.bids data/${newSub}/anat/${newSub}_${target}.json
		cp sourcedata/${newSub}/${orig_name}/${orig_name}.nii.gz data/${newSub}/anat/${newSub}_${target}.nii.gz

		#cp sourcedata/${sub}/${orig_name}/${orig_name}.nii.gz data/${sub}/anat/${sub}_${target}.nii.gz
		#cp sourcedata/${sub}/${orig_name}/${orig_name}.bids data/${sub}/anat/${sub}_${target}.json
	elif [ $target == "phasediff" ]
	then
		echo ${target}
		ln -s sourcedata/${newSub}/${orig_name}/${orig_name}_c0_2.nii.gz sourcedata/${newSub}/${newSub}_${target}.nii.gz
		ln -s sourcedata/${newSub}/${orig_name}/${orig_name}_c0_2.bids sourcedata/${newSub}/${newSub}_${target}.json
		cp sourcedata/${newSub}/${orig_name}/${orig_name}_c0_2.bids data/${newSub}/fmap/${newSub}_${target}.json
		cp sourcedata/${newSub}/${orig_name}/${orig_name}_c0_2.nii.gz data/${newSub}/fmap/${newSub}_${target}.nii.gz

	else
		echo ${target}
		r=`echo ${target} | cut -d '-' -f2`
		ln -s sourcedata/${newSub}/${orig_name}/${orig_name}.nii.gz sourcedata/${newSub}/${newSub}_task-${taskname}_${target}_bold.nii.gz
		ln -s sourcedata/${newSub}/${orig_name}/${orig_name}.bids sourcedata/${newSub}/${newSub}_task-${taskname}_${target}_bold.json
		cp sourcedata/${newSub}/${orig_name}/${orig_name}.nii.gz data/${newSub}/func/${newSub}_task-${taskname}_${target}_bold.nii.gz
		cp sourcedata/${newSub}/${orig_name}/${orig_name}.bids data/${newSub}/func/${newSub}_task-${taskname}_${target}_bold.json		
		cp sourcedata/${newSub}/from_scanner/${origSub}_0${r}.tsv data/${newSub}/func/${newSub}_task-${taskname}_${target}_events.tsv
	fi
done < sourcedata/${newSub}/filemapping.txt

echo "moving notes and misc"
mkdir -p derivatives/${newSub}
mv data/${origSub}/notes derivatives/${newSub}/misc
mv data/${origSub}/behav/regressors derivatives/${newSub}/misc/

:<<other
# derivatives folder (preprocessed and processed data)
mkdir -p derivatives/${newSub}
mv data/${origSub}/analysis/* derivatives/${newSub}/
mkdir -p derivatives/${newSub}/func
mkdir -p derivatives/${newSub}/betas
for f in derivatives/${newSub}/Run?.nii.gz
do
    r=`echo ${f} | cut -d '/' -f3 | cut -d 'n' -f2 | cut -d '.' -f1`
    mv ${f} derivatives/${newSub}/func/${newSub}_task-analogy_run-0${r}_bold.nii.gz
    cp data/${origSub}/behav/labels/Run${r}.tsv derivatives/${newSub}/func/${newSub}_task-analogy_run-0${r}_events.tsv
    mv data/${origSub}/behav/labels/Run${r}.tsv data/${newSub}/func/${newSub}_task-analogy_run-0${r}_events.tsv
done
mv derivatives/${newSub}/${origSub}_grayMatter_betas_LSA.nii.gz derivatives/${newSub}/betas/${newSub}_task-analogy_betas-pymvpa.nii.gz
mv data/${origSub}/behav/labels/${origSub}_PyMVPA_LSA_labels.tsv derivatives/${newSub}/betas/${newSub}_task-analogy_events-pymvpa.tsv




rm sourcedata/${newSub}/*_*.*
rm sourcedata/${newSub}/*.nii.gz
rm sourcedata/${newSub}/*.bids


for s in sub-*
do
for f in ${s}/func/*-??
do
echo ${f}
f1=`echo ${f} | cut -d '_' -f1`
f2=`echo ${f} | cut -d '_' -f2,3`
mv ${f} ${f1}_task-analogy_${f2}
done
done





while read line
do
    orig_name=`echo ${line} | cut -d ',' -f1`
    target_name=`echo ${line} | cut -d ',' -f2`
    for i in sourcedata/${newSub}/${orig_name}/${orig_name}*
    do
        f=`echo ${i} | rev | cut -d '/' -f1| rev`
        fpath=`echo ${i} | rev | cut -d '/' -f3-| rev`
        t=`echo ${f} | sed "s/${orig_name}/${newSub}_${target_name}/"`
        targetfile=${fpath}/${t}
        ln -s ${i} ${targetfile}
    done
done < sourcedata/${newSub}/filemapping.txt

other
