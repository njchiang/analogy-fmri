#!/bin/bash
:<<plan
# current structure:
project
-analysis
--univariate
--multivariate
-data
--analogy*
--standard
--log
-behav
--labels
--from_scanner
--regressors
-notes
-raw --> sourcedata
-dicom

naming: analogyXXX_RunX
to sub-XX_task-analogy_run-XX_bold.nii.gz

# desired
project
-sourcedata (raw + filemapping (hoffman only))
-data (functional data)
--sub-*
---anat
---func
---behav
---fmap
-code
-derivatives (analysis results)
--sub-*
---masks
---behav
---reg
---searchlight
---univariate

-stimuli
plan

s=${1}

mkdir -p derivatives

ROOTDIR=~/data/fmri/Analogy
cd ${ROOTDIR}

origSub=analogy0${s}
newSub=sub-${s}
mkdir -p sourcedata/${newSub}
mv data/${origSub}/raw/* sourcedata/${newSub}/
mv data/${origSub}/dicom.tar.gz sourcedata/${newSub}/
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
done < data/${origSub}/behav/filemapping.txt
mv data/${origSub}/behav/filemapping.txt sourcedata/${newSub}/filemapping.txt
mkdir -p sourcedata/${newSub}/behav
mv data/${origSub}/behav/from_scanner/* sourcedata/${newSub}/behav/

mkdir -p data/${newSub}/anat
mkdir -p data/${newSub}/func
mkdir -p data/${newSub}/fmap
mv sourcedata/${newSub}/${newSub}_T1w.nii.gz data/${newSub}/anat/
mv sourcedata/${newSub}/${newSub}_T1w.bids data/${newSub}/anat/${newSub}_T1w.json
for f in sourcedata/${newSub}/*run-??.nii.gz
do
fn=`echo ${f} | cut -d '.' -f1 | cut -d '/' -f3`
f1=`echo ${fn} | cut -d '_' -f1
f2=`echo ${fn} | cut -d '_' -f2
mv ${f} data/${newSub}/func/${f1}_task-analogy_${f2}_bold.nii.gz
mv sourcedata/${newSub}/${fn}.bids data/${newSub}/func/${f1}_task-analogy_${f2}_bold.json
done
mv sourcedata/${newSub}/${newSub}_gre*.nii.gz data/${newSub}/fmap/
mv sourcedata/${newSub}/${newSub}_gre*.bids data/${newSub}/fmap/${newSub}_gre.json

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

mv data/${origSub}/notes derivatives/${newSub}/about
mv data/${origSub}/behav/regressors derivatives/${newSub}/about/



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



