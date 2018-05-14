#!/bin/sh

# This is the shell script that will generate all the skeletons using cmsDriver commands.
# The commands included have been taken from runTheMatrix with the following command:

# runTheMatrix.py -w relval_upgrade -j 0 -l 22088

# Those commands should be regularly checked and, in case of changes, propagated into this script!


cmsDriver.py SinglePiPt25Eta1p7_2p7_cfi  --conditions auto:phase2_realistic \
  -n 10 --era Phase2 --eventcontent FEVTDEBUG --nThreads 4 \
  -s GEN,SIM,DIGI:pdigi_valid,L1,L1TrackTrigger,DIGI2RAW,HLT:@fake2 \
  --datatier GEN-SIM --beamspot HLLHC \
  --geometry Extended2023D23 --era Phase2 --eventcontent FEVTDEBUGHLT \
  --no_exec --python_filename=GSD_fragment.py


cmsDriver.py step3  --conditions auto:phase2_realistic -n 10 \
  --era Phase2 --eventcontent FEVTDEBUGHLT,DQM --runUnscheduled --nThreads 4 \
  -s RAW2DIGI,L1Reco,RECO,RECOSIM,VALIDATION:@phase2Validation,DQM:@phase2 \
  --datatier GEN-SIM-RECO,DQMIO --geometry Extended2023D23 \
  --no_exec --python_filename=RECO_fragment.py

cmsDriver.py step3 --conditions auto:phase2_realistic -n 10 \
  --era Phase2 --eventcontent FEVTDEBUGHLT --runUnscheduled \
  -s RAW2DIGI,L1Reco,RECO,RECOSIM \
  --datatier GEN-SIM-RECO --geometry Extended2023D23 \
  --no_exec --python_filename=NTUP_fragment.py \
  --processName=NTUP



