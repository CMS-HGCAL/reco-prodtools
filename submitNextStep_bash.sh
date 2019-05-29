#!/bin/bash

#
# Script to automatically submit jobs for next step (RECO or NTUP) for all
# samples in SAMPLEDIR. Can adjust events per job with variables listed
# below (EVTSRECO and EVTSNTUP).
#
SAMPLEDIR='/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production'
MYDIRS=('FlatRandomEGunProducer_test_bruno_20190528')
EVTSRECO=1
EVTSNTUP=120

arrayContains() { 
    # Checks whether a certain element belongs to the provided array
    # Arguments:
    # 1. Name of the array
    # 2. Element to search in the array
    local array="$1[@]"
    local match="${2}"
    local flag=false;
    for i in "${!array}"; do
	if [[ $i == "${match}" ]]; then
	    flag=true;
	    break;
	fi
    done
    echo $flag;
}

for item in `ls $SAMPLEDIR`; do
    if [ $(arrayContains MYDIRS "${item}") = true ]; then
	CONTENT=(`ls $SAMPLEDIR/$item`)
	if [ $(arrayContains CONTENT "GSD") = true ]; then
	    if [ $(arrayContains CONTENT "RECO") = true ]; then
		if [ $(arrayContains CONTENT "NTUP") = true ]; then
                    echo "Nothing to be done"
		else
                    echo "submit NTUP for $item"
                    python SubmitHGCalPGun.py --datTier NTUP --evtsperjob $EVTSNTUP --queue workday --inDir $item --eosArea $SAMPLEDIR
		fi
            else
		echo "submit RECO for $item"
		python SubmitHGCalPGun.py --datTier RECO --evtsperjob $EVTSRECO --queue longlunch --inDir $item --eosArea $SAMPLEDIR
            fi
	else
            echo "$item does not seem to be a directory containing event samples! Skipping."
	fi
    fi
done
