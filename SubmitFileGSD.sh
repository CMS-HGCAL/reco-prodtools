#!/bin/bash
export XRD_NETWORKSTACK=IPv4

## External vars
clusterid=${1}
procid=${2}
curDir=${3}
outDir=${4}
cfgFileGSD=${5}
cfgFileRECO=${6}
cfgFileNTUP=${7}
localFlag=${8}
CMSSWVER=${9} # CMSSW_8_1_0_pre7
CMSSWDIR=${10} # ${curDir}/../${CMSSWVER}
CMSSWARCH=${11} # slc6_amd64_gcc530
eosArea=${12}
dataTier=${13}
keepDQMfile=${14}

##Create Work Area
export SCRAM_ARCH=${CMSSWARCH}
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 project CMSSW ${CMSSWVER}`
cd ${CMSSWVER}/
rm -rf ./*
cp -r -d ${CMSSWDIR}/* ./
cd src
eval `scramv1 runtime -sh`
edmPluginRefresh -p ../lib/$SCRAM_ARCH

## Execute job and retrieve the outputs
echo "Job running on `hostname` at `date`"

cmsRun ${curDir}/${outDir}/cfg/${cfgFileGSD}

if [ $dataTier = "ALL" ]; then
  cmsRun ${curDir}/${outDir}/cfg/${cfgFileRECO}
  cmsRun ${curDir}/${outDir}/cfg/${cfgFileNTUP}
  dataTier="NTUP"
fi

# copy to outDir in curDir or at given EOS area
if [ ${localFlag} == "True" ]
  then
    cp *${dataTier}*.root ${curDir}/${outDir}/${dataTier}/
    if [ ${keepDQMfile} == "True" ]
        then
        cp *DQM*.root ${curDir}/${outDir}/DQM/
    fi
  else
    xrdcp -N -v *${dataTier}*.root root://eoscms.cern.ch/${eosArea}/${outDir}/${dataTier}/
    if [ ${keepDQMfile} == "True" ]
        then
        xrdcp -N -v *DQM*.root root://eoscms.cern.ch/${eosArea}/${outDir}/DQM/
    fi  
fi
