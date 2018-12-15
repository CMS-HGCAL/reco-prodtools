#!/bin/bash
export XRD_NETWORKSTACK=IPv4

## External vars
clusterid=${1}
procid=${2}
curDir=${3}
outDir=${4}
cfgFile=${5}
localFlag=${6}
CMSSWVER=${7} # CMSSW_8_1_0_pre7
CMSSWDIR=${8} # ${curDir}/../${CMSSWVER}
CMSSWARCH=${9} # slc6_amd64_gcc530
eosArea=${10}
dataTier=${11}

##Create Work Area
export SCRAM_ARCH=${CMSSWARCH}
source /afs/cern.ch/cms/cmsset_default.sh
eval `scramv1 project CMSSW ${CMSSWVER}`
cd ${CMSSWVER}/
rm -rf ./*
cp -r -d ${CMSSWDIR}/* ./
cd src
eval `scramv1 runtime -sh`
edmPluginRefresh -p ../lib/$SCRAM_ARCH

## Execute job and retrieve the outputs
echo "Job running on `hostname` at `date`"

cmsRun ${curDir}/${outDir}/cfg/${cfgFile}

# copy to outDir in curDir or at given EOS area
if [ ${localFlag} == "True" ]
  then
    cp *${dataTier}*.root ${curDir}/${outDir}/${dataTier}/
  else
    xrdcp -N -v *${dataTier}*.root root://eoscms.cern.ch/${eosArea}/${outDir}/${dataTier}/
fi