import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.Pythia8CUEP8M1Settings_cfi import *
from Configuration.Generator.PythiaUEZ2starSettings_cfi import *

def defineProcessGenerator(process,proc='minbias'):
    
    """
    wraps up a couple of interesting processes for HGCal studies
    minbias (min.bias), hgg (H->gamgam), wqq (W->qq')
    """

    #MinBias
    if proc=='minbias':
        process.generator = cms.EDFilter("Pythia8GeneratorFilter",
                                         comEnergy = cms.double(14000.0),
                                         crossSection = cms.untracked.double(8.45E-6),
                                         filterEfficiency = cms.untracked.double(1.0),
                                         maxEventsToPrint = cms.untracked.int32(1),
                                         pythiaPylistVerbosity = cms.untracked.int32(1),
                                         pythiaHepMCVerbosity = cms.untracked.bool(False),
                                         PythiaParameters = cms.PSet( pythia8CommonSettings = cms.vstring('Tune:preferLHAPDF = 2',
                                                                                                          'Main:timesAllowErrors = 10000',
                                                                                                          'Check:epTolErr = 0.01',
                                                                                                          #'Beams:setProductionScalesFromLHEF = off',
                                                                                                          'SLHA:keepSM = on',
                                                                                                          'SLHA:minMassSM = 1000.',
                                                                                                          'ParticleDecays:limitTau0 = on',
                                                                                                          'ParticleDecays:tau0Max = 10',
                                                                                                          'ParticleDecays:allowPhotonRadiation = on'),
                                                                      pythia8CUEP8M1Settings = cms.vstring('Tune:pp 14',
                                                                                                           'Tune:ee 7',
                                                                                                           'MultipartonInteractions:pT0Ref=2.4024',
                                                                                                           'MultipartonInteractions:ecmPow=0.25208',
                                                                                                           'MultipartonInteractions:expPow=1.6'),
                                                                      processParameters = cms.vstring('Main:timesAllowErrors    = 10000',
                                                                                                      'ParticleDecays:limitTau0 = on',
                                                                                                      'ParticleDecays:tauMax = 10',
                                                                                                      'SoftQCD:nonDiffractive = on',
                                                                                                      'SoftQCD:singleDiffractive = on',
                                                                                                      'SoftQCD:doubleDiffractive = on'),
                                                                      parameterSets = cms.vstring('pythia8CommonSettings',
                                                                                                  'pythia8CUEP8M1Settings',
                                                                                                  'processParameters')
                                                                  )
                                     )

    #H->gg
    if proc=='hgg':
        process.generator = cms.EDFilter("Pythia8GeneratorFilter",
                                         comEnergy = cms.double(14000.0),
                                         crossSection = cms.untracked.double(8.45E-6),
                                         filterEfficiency = cms.untracked.double(1.0),
                                         maxEventsToPrint = cms.untracked.int32(1),
                                         pythiaPylistVerbosity = cms.untracked.int32(1),
                                         pythiaHepMCVerbosity = cms.untracked.bool(False),
                                         PythiaParameters = cms.PSet( pythia8CommonSettingsBlock,
                                                                      pythia8CUEP8M1SettingsBlock,
                                                                      processParameters = cms.vstring('Main:timesAllowErrors    = 10000',
                                                                                                      'HiggsSM:all=true',
                                                                                                      '25:m0 = 125.0',
                                                                                                      '25:onMode = off',
                                                                                                      '25:onIfMatch = 22 22'       
                                                                                                  ),
                                                                      
                                                                      parameterSets = cms.vstring('pythia8CommonSettings',
                                                                                                  'pythia8CUEP8M1Settings',
                                                                                                  'processParameters')
                                                                  )
                                    )
    
    #W->qq'
    if proc=='wqq':
        process.generator = cms.EDFilter("Pythia6GeneratorFilter",
                                         pythiaHepMCVerbosity = cms.untracked.bool(False),
                                         maxEventsToPrint = cms.untracked.int32(0),
                                         pythiaPylistVerbosity = cms.untracked.int32(1),
                                         filterEfficiency = cms.untracked.double(1.),
                                         crossSection = cms.untracked.double(9.181e3),
                                         comEnergy = cms.double(14000.0),
                                         PythiaParameters = cms.PSet(
                                             pythiaUESettingsBlock,
                                             processParameters = cms.vstring('MSEL        = 0    !User defined processes', 
                                                                             'MSUB(2)     = 1    !W production', 
                                                                             'MDME(190,1) = 1    !W decay into dbar u', 
                                                                             'MDME(191,1) = 1    !W decay into dbar c', 
                                                                             'MDME(192,1) = 0    !W decay into dbar t', 
                                                                             'MDME(194,1) = 1    !W decay into sbar u', 
                                                                             'MDME(195,1) = 1    !W decay into sbar c', 
                                                                             'MDME(196,1) = 0    !W decay into sbar t', 
                                                                             'MDME(198,1) = 0    !W decay into bbar u', 
                                                                             'MDME(199,1) = 0    !W decay into bbar c', 
                                                                             'MDME(200,1) = 0    !W decay into bbar t', 
                                                                             'MDME(205,1) = 0    !W decay into bbar tp', 
                                                                             'MDME(206,1) = 0    !W decay into e+ nu_e', 
                                                                             'MDME(207,1) = 0    !W decay into mu+ nu_mu', 
                                                                             'MDME(208,1) = 0    !W decay into tau+ nu_tau'),
                                             # This is a vector of ParameterSet names to be read, in this order
                                             parameterSets = cms.vstring('pythiaUESettings', 
                                                                         'processParameters')
                                         )
                                     )

    #ttbar
    if proc=='ttbar':
        addJetFilter=True
        process.generator = cms.EDFilter("Pythia8GeneratorFilter",
                                         maxEventsToPrint = cms.untracked.int32(1),
                                         pythiaPylistVerbosity = cms.untracked.int32(1),
                                         filterEfficiency = cms.untracked.double(1.0),
                                         pythiaHepMCVerbosity = cms.untracked.bool(False),
                                         comEnergy = cms.double(14000.0),                                         
                                         crossSection = cms.untracked.double(1),                                         
                                         PythiaParameters = cms.PSet(
                                             pythia8CommonSettingsBlock,
                                             pythia8CUEP8M1SettingsBlock,
                                             processParameters = cms.vstring(
                                                 'Top:gg2ttbar    = on',
                                                 'Top:qqbar2ttbar = on',
                                                 '6:m0 = 172.5',    # top mass',
                                             ),
                                             parameterSets = cms.vstring('pythia8CommonSettings',
                                                                         'pythia8CUEP8M1Settings',
                                                                         'processParameters',
                                                                     )                                             
                                         )
                                     )

def defineJetBasedBias(process,jetColl="ak8GenJetsNoNu",thr=100,minObj=1):

    """
    defines a path to execute to filter the output based on a given gen-jet collection
    and the presence of minObj-jets with pt>thr
    """

    #gen level selection of gen jets in the endcap        
    setattr(process,'ee'+jetColl,cms.EDFilter("CandViewShallowCloneProducer",
                                              src = cms.InputTag(jetColl),
                                              cut = cms.string("abs(eta)<3.0 && abs(eta)>1.5") ) )
    setattr(process,'goodee'+jetColl,cms.EDFilter("CandViewSelector",
                                                  src = cms.InputTag("ee"+jetColl),
                                                  cut = cms.string("pt > %f"%thr) ) )
    setattr(process,jetColl+'Filter',cms.EDFilter("CandViewCountFilter",
                                                  src = cms.InputTag("goodee"+jetColl),
                                                  minNumber = cms.uint32(minObj) ) )            
    setattr(process,jetColl+'FilterSeq',cms.Sequence( getattr(process,'ee'+jetColl)*
                                                      getattr(process,'goodee'+jetColl)*
                                                      getattr(process,jetColl+'Filter') ) )              
    setattr(process,jetColl+'FilterPath',cms.Path( getattr(process,jetColl+'FilterSeq') ) )
    return getattr(process,jetColl+'FilterPath')
