#!/bin/bash
#===============================================================================
#
#          FILE: format_data.sh
# 
#         USAGE: ./format_data.sh --initialize -s sub1 -s sub2 -a analysis1 -p
#         FILE_PATH
#         OR
#         ./format_data.sh -s sub3 -s sub4 (to add more subjects)
# 
#   DESCRIPTION: 
#   this script is run in each analysis, sets up file structure and populates it with subjects
#   arguments:
#   basically is a wrapper for make_file_structure.sh and copies data in. should
#   be able to pull new subjects without the --initialize option
#   
#	OPTIONS: ---
#       --initialize | switch for first time initialization
#       -s subject
#       -a analyses 
#       -p path
#   REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Jeff Chiang (jc), jeff.njchiang@gmail.com
#  ORGANIZATION: Monti Lab
#       CREATED: 10/22/2016 10:18:15 PM
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

METHOD='local'
COPY=false
INITIALIZE=false
OPATH=${PWD}
REMOVEVOLS=0
RUNLIST=''
SUBLIST=''
ANALYSIS=''
SERVER='njchiang@funcserv1.psych.ucla.edu'
SPATH='/space/raid5/data/monti/Analysis/Analogy'
while [[ $# -ge 1 ]]
do
	key="$1"
	case $key in
	-p|--OPATH)
		OPATH="$2"
		shift # past argument
		;;	
	-s|--sub)
		ADDSUBJECTS=true
		SUBLIST="${SUBLIST} ${2}"
		shift # past argument
		;;
	-a|--analysis)
		ANALYSIS="${ANALYSIS} -a ${2}"
		shift
		;;
	--initialize)
		INITIALIZE=true
		;;
	-v | --remove)
		REMOVEVOLS=${2}
		shift
		;;
	-r | --runs)
		RUNLIST="${RUNLIST} ${2}"
		shift
		;;
	--copy)
		COPY=true
		;;
	--reference)
		REFERENCE=${2}
		shift
		;;
	*)
		echo "./format_data.sh --initialize -s sub1 -s sub2 -a analysis1 -p FILE_PATH"
		echo "./format_data.sh -s sub3 -s sub4 (to add more subjects)"
		;;
	esac
	shift # past argument or value
done

case ${OSTYPE} in 
	darwin*)
	GITDIR=~/GitHub/task-fmri-utils
	;;
	linux*)
	GITDIR=~/data/GitHub/task-fmri-utils
esac

mkdir ${OPATH}/data/logs
date=`date +"%Y%m%d%H%M"`
logfile=${OPATH}/data/logs/format_data_${date}.log
echo "Logging to: ${logfile}"

########## INITIALIZE FILE STRUCTURE #############
# this can and should be modified
if [[ ${INITIALIZE} == "true" ]]
then
	echo "Initializing project directory" >> $logfile
	cmd="sh ${GITDIR}/data-init/make_file_structure.sh --initialize ${ANALYSIS} -p ${OPATH}"
	echo ${cmd} >> ${logfile}
	${cmd}
fi

for s in ${SUBLIST}
do
	# copy subject data from the FUNC
	if [ ${COPY} == "true" ]
	then
		echo "copying data from server" >> ${logfile}
		cmd="scp -r ${SERVER}:${SPATH}/data/${s} ${OPATH}/data/${s}"
		echo ${cmd} >> ${logfile}
		${cmd}
	fi

	# make additional folders if needed
	echo "Adding extra folders to subject directory" >> ${logfile}
	cmd="sh ${GITDIR}/data-init/make_file_structure.sh --noanalysis -s ${s} -p ${OPATH}"
	echo ${cmd} >> ${logfile}
	${cmd}

	# rename runs in a friendly format
	echo "Renaming runs" >> ${logfile}
	cmd="sh ${GITDIR}/data-init/rename_runs.sh -p ${OPATH} -s ${s}"
	echo ${cmd} >> ${logfile}
	${cmd}
	
	# preprocess runs
	echo "Preprocessing ${REFERENCE}" >> ${logfile}
	cmd="sh ${GITDIR}/data-init/preprocess_BOLD_data.sh -p ${OPATH} -s ${s} \
		-r ${REMOVEVOLS} --mcflirt -f ${REFERENCE} --bet"
	echo ${cmd} >> ${logfile}
	${cmd}
	
	echo "BOLD template" >> ${logfile}
	cmd="sh ${GITDIR}/data-init/BOLD_template.sh -p ${OPATH} -s ${s} \
				-f ${REFERENCE}_preproc -o ${REFERENCE} --template"
	echo ${cmd} >> ${logfile}
	${cmd}

	echo "Register masks" >> ${logfile}
	cmd="sh ${GITDIR}/data-init/register_masks.sh -p ${OPATH} -s ${s} \
		-t ${REFERENCE} -m grayMatter"
	echo ${cmd} >> ${logfile}
	${cmd}

	for r in $RUNLIST
	do
		# preprocess runs
		echo "Preprocessing ${r}" >> ${logfile}
		cmd="sh ${GITDIR}/data-init/preprocess_BOLD_data.sh -p ${OPATH} -s ${s} \
			-r ${REMOVEVOLS} --mcflirt -f ${r} --bet"
		echo ${cmd} >> ${logfile}
		${cmd}

		echo "BOLD template" >> ${logfile}
		if [ ${r} != ${REFERENCE} ]
		then
			cmd="sh ${GITDIR}/data-init/BOLD_template.sh -p ${OPATH} -s ${s} \
			-f ${r}_preproc -o ${r} -t BOLD_template"
		fi
		echo ${cmd} >> ${logfile}
		${cmd}
	done
done

