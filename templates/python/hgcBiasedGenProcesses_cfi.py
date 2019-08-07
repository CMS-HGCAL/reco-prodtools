import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *


def defineProcessGenerator(process,proc='minbias'):

    """
    wraps up a couple of interesting processes for HGCal studies
    - minbias (minimum bias),
    - hgg (H->gammagamma),
    - wqq (W->qq')
    - ttbar
    """
    processParameters = None
    if proc == 'minbias':
        # Taken from https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/PPD-RunIIFall17GS-00004
        processParameters = cms.vstring(
            'SoftQCD:nonDiffractive = on',
            'SoftQCD:singleDiffractive = on',
            'SoftQCD:doubleDiffractive = on',
        )
    elif proc == 'hgg':
        # adjust e.g. from https://github.com/cms-sw/genproductions/blob/master/python/ThirteenTeV/Higgs/SMHiggsToTauTau_13TeV-powheg_pythia8_cff.py
        processParameters = cms.vstring(
            'Main:timesAllowErrors    = 10000',
            'HiggsSM:all=true',
            '25:m0 = 125.0',
            '25:onMode = off',
            '25:onIfMatch = 22 22'
        )
    elif proc == 'wqq':
        # adjust e.g. from https://github.com/cms-sw/genproductions/blob/master/python/ThirteenTeV/WToMuNu_M_1000_TuneCUETP8M1_13TeV_pythia8_cfi.py
        processParameters = cms.vstring(
            'WeakSingleBoson:ffbar2W = on',
            '24:onMode = off',
            '24:onIfAny = 1,2,3,4',
        )
    elif proc == 'ttbar':
        processParameters = cms.vstring(
            'Top:gg2ttbar    = on',
            'Top:qqbar2ttbar = on',
            '6:m0 = 172.5',  # top mass'
        )
    else:
        raise ValueError('Process \"{}\" not defined.'.format(proc))

    process.generator = cms.EDFilter(
        "Pythia8GeneratorFilter",
        maxEventsToPrint = cms.untracked.int32(1),
        pythiaPylistVerbosity = cms.untracked.int32(1),
        filterEfficiency = cms.untracked.double(1.0),
        pythiaHepMCVerbosity = cms.untracked.bool(False),
        comEnergy = cms.double(14000.),
        PythiaParameters = cms.PSet(
            pythia8CommonSettingsBlock,
            pythia8CP5SettingsBlock,
            processParameters = processParameters,
            parameterSets = cms.vstring(
                'pythia8CommonSettings',
                'pythia8CP5Settings',
                'processParameters',
            )
        )
    )


def defineJetBasedBias(process, jetColl="ak8GenJetsNoNu", thr=100, minObj=1):

    """
    defines a path to execute to filter the output based on a given gen-jet collection
    and the presence of minObj-jets with pt>thr
    """

    #gen level selection of gen jets in the endcap
    setattr(process, 'ee'+jetColl, cms.EDFilter(
        "CandViewShallowCloneProducer",
        src = cms.InputTag(jetColl),
        cut = cms.string("abs(eta)<3.0 && abs(eta)>1.479")
    ))
    setattr(process, 'goodee'+jetColl, cms.EDFilter(
        "CandViewSelector",
        src = cms.InputTag("ee"+jetColl),
        cut = cms.string("pt > %f"%thr)
    ))
    setattr(process, jetColl+'Filter', cms.EDFilter(
        "CandViewCountFilter",
        src = cms.InputTag("goodee"+jetColl),
        minNumber = cms.uint32(minObj)
    ))
    setattr(process, jetColl+'FilterSeq', cms.Sequence(
        getattr(process,'ee'+jetColl)*
        getattr(process,'goodee'+jetColl)*
        getattr(process,jetColl+'Filter')
    ))
    setattr(process, jetColl+'FilterPath', cms.Path(
        getattr(process,jetColl+'FilterSeq')
    ))
    return getattr(process,jetColl+'FilterPath')
