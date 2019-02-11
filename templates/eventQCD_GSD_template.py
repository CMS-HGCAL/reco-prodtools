import FWCore.ParameterSet.Config as cms

from reco_prodtools.templates.GSD_fragment import process

process.maxEvents.input = cms.untracked.int32(DUMMYEVTSPERJOB)

# random seeds
process.RandomNumberGeneratorService.generator.initialSeed = cms.untracked.uint32(DUMMYSEED)
process.RandomNumberGeneratorService.VtxSmeared.initialSeed = cms.untracked.uint32(DUMMYSEED)
process.RandomNumberGeneratorService.mix.initialSeed = cms.untracked.uint32(DUMMYSEED)

# Input source
process.source.firstLuminosityBlock = cms.untracked.uint32(DUMMYSEED)

# Output definition
process.FEVTDEBUGHLToutput.fileName = cms.untracked.string('file:DUMMYFILENAME')

#DUMMYPUSECTION

process.generator = cms.EDFilter("Pythia8GeneratorFilter",
     maxEventsToPrint = cms.untracked.int32(1),
     pythiaPylistVerbosity = cms.untracked.int32(1),
     pythiaHepMCVerbosity = cms.untracked.bool(True),
     PythiaParameters = cms.PSet(
         parameterSets = cms.vstring(
             'pythia8CommonSettings',
             'pythia8CUEP8M1Settings',
             'processParameters'
             ),
         processParameters = cms.vstring(
             'HardQCD:all = on',
             'PhaseSpace:pTHatMin = 80.',
             'PhaseSpace:pTHatMax = 120.'
             ),
         pythia8CUEP8M1Settings = cms.vstring(
              'Tune:pp 14',
              'Tune:ee 7',
              'MultipartonInteractions:pT0Ref=2.4024',
              'MultipartonInteractions:ecmPow=0.25208',
              'MultipartonInteractions:expPow=1.6'
              ),
         pythia8CommonSettings = cms.vstring(
               'Tune:preferLHAPDF = 2',
               'Main:timesAllowErrors = 10000',
               'Check:epTolErr = 0.01',
               'Beams:setProductionScalesFromLHEF = off',
               'SLHA:keepSM = on',
               'SLHA:minMassSM = 1000.',
               'ParticleDecays:limitTau0 = on',
               'ParticleDecays:tau0Max = 10',
               'ParticleDecays:allowPhotonRadiation = on'
               )
         ),
     comEnergy = cms.double(14000.0),
     filterEfficiency = cms.untracked.double(1.0),
)
