#!/bin/bash

#TIER="GSD"
#TIER="RECO"
#TIER="NTUP"
if [ $# -ne 3 ]
then
  echo "ERROR - needs three arguments"
  echo "First should be one of GSD, RECO, or NTUP"
  echo "Second is the PDGID"
  echo "Third is the pT"
  exit 1
fi
TIER=$1
PARTID=$2
PT=$3

NEVTS=1000
QUEUE="8nh"
#PARTID=22
NPART=1
#PT=35

#TAG="clange_PDGid22_nPart1_Pt35"
#TAG="escott_PDGid22_nPart1_Pt35"
#TAG="testing_pre15"
#TAG="clange_PDGid22_nPart1_Pt35_kdtreeMergeOldGSDlocalRecoParams01and10"
#TAG="clange_PDGid22_nPart1_Pt35_kdtreeMergeOldGSDlocalRecoWithFHandBHparams01and10"
#TAG="escott_PDGid${PARTID}_nPart1_Pt35_FullPre15HexelRemovedTest"
#TAG='clange_PDGid22_nPart1_Pt35Pre15HexelRemovedLocalReco'
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_FullWorkingTest"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_FullWorkingTestOldPhysicsList"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_LindseyPRfullTestTwo"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_LindseyPRfullTestCorrectSequence"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_AutomaticMulticlusterTest"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_AutomaticMulticlusterTest_DebuggedRealSpaceMultis0dot5cm"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_AutomaticMulticlusterTest_DebuggedRealSpaceMultis1cm"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_AutomaticMulticlusterTest_DebuggedRealSpaceMultis2cm"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_AutomaticMulticlusterTest_DebuggedRealSpaceMultis4cm"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_AutomaticMulticlusterTest_DebuggedRealSpaceMultis6cm"
TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_AutomaticMulticlusterTest"

EOS="/eos/cms/store/group/dpg_hgcal/comm_hgcal/escott"

#DATE="20160729"
DATE="20161208"
#DATE="20161213"
#DATE="20161214"

#EXTRALABEL=""
#EXTRALABEL="_fullPre8setup"
#EXTRALABEL="_fullPre8setupEEonly"
#EXTRALABEL="_fullPre8setupEEonlyOldParams"
#EXTRALABEL="_fullPre8setupEEonlyOldParamsSharing"
#EXTRALABEL="_fullPre8setupEEonlyNoSharing"
#EXTRALABEL="_fullPre8setupEEonlyEmilioParams"
#EXTRALABEL="_fullPre8setupEEonlyParams01and12"
#EXTRALABEL="_fullPre8setupEEonlyParams1and10"
#EXTRALABEL="_kdtreeMergeOldGSDlocalRecoParams01and10"
#EXTRALABEL="_kdtreeMergeOldGSDlocalRecoWithFHparams01and10"
#EXTRALABEL="_kdtreeMergeOldGSDlocalRecoWithFHandBHparams01and10"
#EXTRALABEL="Pre15HexelRemovedLocalReco"
#EXTRALABEL="DepthCone03"
#EXTRALABEL="DepthCone05"
#EXTRALABEL="DepthCone1"
#EXTRALABEL="KeepClusters"
#EXTRALABEL="Amended"
#EXTRALABEL="AutomaticMulticlusterTest"
#EXTRALABEL="_RealSpaceMultis0dot5cm"
#EXTRALABEL="_RealSpaceMultis1cm"
#EXTRALABEL="_RealSpaceMultis2cm"
#EXTRALABEL="_RealSpaceMultis4cm"
#EXTRALABEL="_RealSpaceMultis6cm"
#EXTRALABEL="_DebuggedRealSpaceMultis0dot5cm"
#EXTRALABEL="_DebuggedRealSpaceMultis1cm"
#EXTRALABEL="_DebuggedRealSpaceMultis2cm"
#EXTRALABEL="_DebuggedRealSpaceMultis4cm"
#EXTRALABEL="_DebuggedRealSpaceMultis6cm"
#EXTRALABEL="_RerunNtuplerTest"
EXTRALABEL="_ContiguityTest"
#EXTRALABEL=""


if [ "$TIER" == "GSD" ]
then
  EVTSPERJOB=20
  echo "python SubmitHGCalPGun.py --datTier $TIER --nevts $NEVTS --evtsperjob $EVTSPERJOB --queue $QUEUE --partID $PARTID --nPart $NPART --pTmin $PT --pTmax $PT --tag $TAG --eosArea $EOS"
  #python SubmitHGCalPGun.py --datTier $TIER --nevts $NEVTS --evtsperjob $EVTSPERJOB --queue $QUEUE --partID $PARTID --nPart $NPART --pTmin $PT --pTmax $PT --tag $TAG --eosArea $EOS
  python SubmitHGCalPGun.py --datTier $TIER --nevts $NEVTS --evtsperjob $EVTSPERJOB --queue $QUEUE --partID $PARTID --nPart $NPART --thresholdMin $PT --thresholdMax $PT --tag $TAG --eosArea $EOS
fi


if [ "$TIER" == "RECO" ]
then
  EVTSPERJOB=50
  echo "python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag $TAG --eosArea $EOS --inDir partGun_${TAG}_$DATE"
  python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag $TAG$EXTRALABEL --eosArea $EOS --inDir partGun_${TAG}_$DATE
fi


if [ "$TIER" == "NTUP" ]
then
  EVTSPERJOB=50
  echo "python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag $TAG --eosArea $EOS --inDir partGun_${TAG}_$DATE"
  python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag ${TAG}${EXTRALABEL} --eosArea $EOS --inDir partGun_${TAG}_$DATE
fi
