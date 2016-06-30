## External vars
curDir=${1}
outDir=${2}
cfgFile=${3}
localFlag=${4}
CMSSWVER=${5} # CMSSW_8_1_0_pre7
CMSSWDIR=${6} # ${curDir}/../${CMSSWVER}
CMSSWARCH=${7} # slc6_amd64_gcc530

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
#cp ${curDir}/${outDir}/cfg/${cfgFile} ./
echo "Job running on `hostname` at `date`"
cmsRun ${curDir}/${outDir}/cfg/${cfgFile}

# copy to outDir in curDir or at CMG EOS
if [ ${localFlag} == "True" ]
  then
    cp *.root ${curDir}/${outDir}/GSD/
  else
    xrdcp -N -v *.root root://eoscms.cern.ch//eos/cms/store/cmst3/group/hgcal/CMG_studies/Production/${outDir}/GSD/
fi
