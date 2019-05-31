#!/usr/bin/env bash
#
# Script to automatically submit jobs for next step (RECO or NTUP) for all
# samples in SAMPLEDIR. Can adjust events per job with variables listed
# below (EVTSRECO and EVTSNTUP). The folders where the GSD, RECO or NTUP folders
#are in turn stored must be specified as follows:
#
# bash submitNextStep.sh folder1 folder2 ...
#
SAMPLEDIR='/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production'
MYDIRS=( "$@" )
EVTSRECO=1
EVTSNTUP=120

arrayContains() { 
    # Checks whether a certain element belongs to the provided array
    # Arguments:
    # 1. Element to search in the array
    # 2. Name of the array
    local match="${1}"
    shift
    local array=("$@")
    local flag=false;

    for i in "${array[@]}"; do
	if [ $i == "${match}" ] || [ $i == "${match}/" ]; then
	    flag=true;
	    break;
	fi
    done
    echo $flag;
}

for item in `ls $SAMPLEDIR`; do
    if [ $(arrayContains "${item}" "${MYDIRS[@]}") = true ]; then
    	CONTENT=(`ls $SAMPLEDIR/$item`)
    	if [ $(arrayContains "GSD" "${CONTENT[@]}") = true ]; then
    	    if [ $(arrayContains "RECO" "${CONTENT[@]}") = true ]; then
    		if [ $(arrayContains "NTUP" "${CONTENT[@]}") = true ]; then
                    echo "${item}: Nothing to be done."
    		else
                    echo "${item}: submit NTUP."
                    python SubmitHGCalPGun.py --datTier NTUP --evtsperjob $EVTSNTUP --queue workday --inDir $item --eosArea $SAMPLEDIR
    		fi
            else
    		echo "${item}: submit RECO."
    		python SubmitHGCalPGun.py --datTier RECO --evtsperjob $EVTSRECO --queue longlunch --inDir $item --eosArea $SAMPLEDIR
            fi
    	else
            echo "$item does not seem to be a directory containing event samples (GSD)!"
	    echo "Skipping."
    	fi
    fi
done
