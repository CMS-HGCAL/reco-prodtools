#!/bin/sh

# This is the shell script that will generate all the skeletons using cmsDriver commands.
# The commands included have been taken from runTheMatrix with the following command:
#
# runTheMatrix.py -w upgrade -l 29234.11 --command="--no_exec" --dryRun
#
# For all commands remove --filein and --fileout options.
# Add python_filename option
#
# The first command combines step1 and step2 (GSD):
# - run up to DIGI...HLT:@fake2
# The following changes are implemented on top:
# --eventcontent FEVTDEBUG ➜ --eventcontent FEVTDEBUGHLT
#
# The second command is step3 removing overlap with step2 (RECO):
# - also remove MINIAODSIM, PAT
# - remove from VALIDATION@miniAODValidation
# - remove from DQM:@miniAODDQM
#
# The third command is a copy of the second only re-running RECO (for NTUP):
# - remove DQM
# - add processName=NTUP option
#
# Those commands should be regularly checked and, in case of changes, propagated into this script!


cmsDriver.py TTbar_14TeV_TuneCUETP8M1_cfi  --conditions auto:phase2_realistic \
  -n 10 --era Phase2C8 --eventcontent FEVTDEBUGHLT --nThreads 4 \
  -s GEN,SIM,DIGI:pdigi_valid,L1,L1TrackTrigger,DIGI2RAW,HLT:@fake2 \
  --datatier GEN-SIM --beamspot HLLHC14TeV \
  --geometry Extended2023D41 \
  --no_exec --python_filename=GSD_fragment.py


cmsDriver.py step3  --conditions auto:phase2_realistic -n 10 \
  --era Phase2C8 --eventcontent FEVTDEBUGHLT,DQM --runUnscheduled --nThreads 4 \
  -s RAW2DIGI,L1Reco,RECO,RECOSIM,VALIDATION:@phase2Validation,DQM:@phase2 \
  --datatier GEN-SIM-RECO,DQMIO --geometry Extended2023D41 \
  --no_exec --python_filename=RECO_fragment.py


cmsDriver.py step3 --conditions auto:phase2_realistic -n 10 \
  --era Phase2C8 --eventcontent FEVTDEBUGHLT --runUnscheduled \
  -s RAW2DIGI,L1Reco,RECO,RECOSIM \
  --datatier GEN-SIM-RECO --geometry Extended2023D41 \
  --no_exec --python_filename=NTUP_fragment.py \
  --processName=NTUP