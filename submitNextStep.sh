#!/bin/zsh

#
# Script to automatically submit jobs for next step (RECO or NTUP) for all
# samples in SAMPLEDIR. Can adjust events per job with variables listed
# below (EVTSRECO and EVTSNTUP).
#

eosExec='/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'
SAMPLEDIR='/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production'
EVTSRECO=10
EVTSNTUP=100

for i in `$eosExec ls $SAMPLEDIR`; do
    CONTENT=("${(@f)$($eosExec ls $SAMPLEDIR/$i)}")
    echo "$i has $CONTENT"
    if [[ ${CONTENT[(r)GSD]} == GSD ]]; then
        if [[ ${CONTENT[(r)RECO]} == RECO ]]; then
            if [[ ${CONTENT[(r)NTUP]} == NTUP ]]; then
                echo "Nothing to be done"
            else
                echo "submit NTUP for $i"
                python SubmitHGCalPGun.py --datTier NTUP --evtsperjob $EVTSNTUP --queue 8nh --inDir $i
            fi
        else
            echo "submit RECO for $i"
            python SubmitHGCalPGun.py --datTier RECO --evtsperjob $EVTSRECO --queue 8nh --inDir $i
        fi
    else
        echo "$i does not seem to be a directory containing event samples! Skipping."
    fi
done
