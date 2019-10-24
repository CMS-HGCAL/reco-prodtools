#!/bin/sh

# This is the shell script that will generate all the skeletons using cmsDriver commands.
# The commands included have been taken from runTheMatrix with the following command:
#
# runTheMatrix.py -w upgrade -l 21234.0 --command="--no_exec" --dryRun
#
# The reconstruction as part of the ticl framework is injected into the RECO_fragment.
#
# For all commands remove --filein and --fileout options.
# Add python_filename option
#
# The first command combines step1 and step2 (GSD):
# - mix in pileup
# - run up to DIGI...HLT:@fake2
# The following changes are implemented on top:
# --beamspot HLLHC14TeV ➜ --beamspot NoSmear
# --eventcontent FEVTDEBUG ➜ --eventcontent FEVTDEBUGHLT
# Removed --relval option.
#
# The second command is step3 removing overlap with step2 (RECO):
# - remove pileup part
# - remove MINIAODSIM from event content and data tier
# - remove PAT from steps (-s)
# - remove @miniAODValidation from VALIDATION step
# - remove @miniAODDQM from DQM step
#
# The third command is a copy of the second only re-running RECO (for NTUP):
# - remove DQM from event content
# - remove DQMIO from data tier
# - add --processName=NTUP option
#
# Those commands should be regularly checked and, in case of changes, propagated into this script!

action() {
  # default arguments
  local inject_ticl="1"

  # parse arguments
  for arg in "$@"; do
    if [ "$arg" = "ticl" ]; then
      inject_ticl="1"
    elif [ "$arg" = "no-ticl" ]; then
      inject_ticl="0"
    else
      2>&1 echo "unknown argument: $arg"
      return "1"
    fi
  done

  pileup_input='/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production//MinBias_14TeV_Extended2026D44_Phase2C6_timing_layer_bar_v0/GEN-SIM/'
  pileup_input=`find ${pileup_input} -iname "*.root" -printf "file:%h/%f,"`
  pileup_input=${pileup_input::-1}
  

  cmsDriver.py TTbar_14TeV_TuneCUETP8M1_cfi \
    --conditions auto:phase2_realistic_T14 \
    -n 10 \
    --era Phase2C6_timing_layer_bar \
    --eventcontent FEVTDEBUGHLT \
    -s GEN,SIM,DIGI:pdigi_valid,L1,L1TrackTrigger,DIGI2RAW,HLT:@fake2 \
    --datatier GEN-SIM \
    --beamspot NoSmear \
    --geometry Extended2026D44 \
    --pileup AVE_200_BX_25ns \
    --pileup_input ${pileup_input} \
    --no_exec \
    --python_filename=GSD_fragment.py


  cmsDriver.py step3 \
    --conditions auto:phase2_realistic_T14 \
    -n 10 \
    --era Phase2C6_timing_layer_bar \
    --eventcontent FEVTDEBUGHLT,DQM \
    --runUnscheduled \
    -s RAW2DIGI,L1Reco,RECO,RECOSIM,VALIDATION:@phase2Validation,DQM:@phase2 \
    --datatier GEN-SIM-RECO,DQMIO \
    --geometry Extended2026D44 \
    --no_exec \
    --python_filename=RECO_fragment.py


  if [ "$inject_ticl" = "1" ]; then
    echo -e "\ninject ticl into RECO_fragment.py"
    ./inject_ticl.sh RECO_fragment.py
    if [ "$?" = "0" ]; then
      echo
    else
      2>&1 echo "ticl injection failed"
      return "2"
    fi
  fi


  cmsDriver.py step3 \
    --conditions auto:phase2_realistic_T14 \
    -n 10 \
    --era Phase2C6_timing_layer_bar \
    --eventcontent FEVTDEBUGHLT \
    --runUnscheduled \
    -s RAW2DIGI,L1Reco,RECO,RECOSIM \
    --datatier GEN-SIM-RECO \
    --geometry Extended2026D44 \
    --no_exec \
    --processName=NTUP \
    --python_filename=NTUP_fragment.py
}
action "$@"
