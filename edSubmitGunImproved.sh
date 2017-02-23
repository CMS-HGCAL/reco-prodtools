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
#NEVTS=5000
QUEUE="8nh"
#PARTID=22
NPART=1
#PT=35

TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_SensorDependent"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_SuperclusteringOneEight"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_SuperclusteringTwoTwo"
#TAG="escott_PDGid${PARTID}_nPart1_Pt${PT}_SuperclusteringTwoSix"

EOS="/eos/cms/store/group/dpg_hgcal/comm_hgcal/escott"

#DATE="20160729" #for "old" sample from Clemens

GSDDATE="20170125" #for default, sensor dependent pions and photons
#GSDDATE="20170127" #for large photon pt35 sample (same tag)
#GSDDATE="20170207" #for photon superclustering

RECODATE="20170222"

#EXTRALABEL=""
#EXTRALABEL="_FH3BH5"
#EXTRALABEL="_FH5BH7"
#EXTRALABEL="_FH2BH2R03"
#EXTRALABEL="_FH3BH5R03"
#EXTRALABEL="_FH5BH7R03"
#EXTRALABEL="_FH5BH7R03"
#EXTRALABEL="CorrectCartesian10mm"
#EXTRALABEL="CorrectCartesian15mm"
#EXTRALABEL="CorrectCartesian20mm"
#EXTRALABEL="CorrectCartesian25mm"
#EXTRALABEL="CorrectCartesian30mm"
#EXTRALABEL="CorrectCartesian40mm"
#EXTRALABEL="CorrectCartesian50mm"
EXTRALABEL="CorrectCartesian60mm"
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
  echo "python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag $TAG$EXTRALABEL --eosArea $EOS --inDir partGun_${TAG}_$GSDDATE"
  python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag $TAG$EXTRALABEL --eosArea $EOS --inDir partGun_${TAG}_$GSDDATE
fi


if [ "$TIER" == "NTUP" ]
then
  EVTSPERJOB=50
  echo "python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag $TAG${EXTRALABEL} --eosArea $EOS --inDir partGun_${TAG}${EXTRALABEL}_$RECODATE"
  #python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag ${TAG}${EXTRALABEL} --eosArea $EOS --inDir partGun_${TAG}_$DATE
  python SubmitHGCalPGun.py --datTier $TIER --evtsperjob $EVTSPERJOB --queue $QUEUE --tag ${TAG}${EXTRALABEL} --eosArea $EOS --inDir partGun_${TAG}${EXTRALABEL}_$RECODATE
fi
