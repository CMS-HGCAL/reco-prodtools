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

gunmode = 'GUNMODE'

if gunmode == 'default':
    process.generator = cms.EDProducer("GUNPRODUCERTYPE",
        AddAntiParticle = cms.bool(True),
        PGunParameters = cms.PSet(
            MaxEta = cms.double(DUMMYETAMAX),
            MaxPhi = cms.double(3.14159265359),
            MAXTHRESHSTRING = cms.double(DUMMYTHRESHMAX),
            MinEta = cms.double(DUMMYETAMIN),
            MinPhi = cms.double(-3.14159265359),
            MINTHRESHSTRING = cms.double(DUMMYTHRESHMIN),
            #DUMMYINCONESECTION
            PartID = cms.vint32(DUMMYIDs)
        ),
        Verbosity = cms.untracked.int32(0),
        firstRun = cms.untracked.uint32(1),
        psethack = cms.string('multiple particles predefined pT/E eta 1p479 to 3')
    )
elif gunmode == 'pythia8':
    process.generator = cms.EDFilter("GUNPRODUCERTYPE",
        maxEventsToPrint = cms.untracked.int32(1),
        pythiaPylistVerbosity = cms.untracked.int32(1),
        pythiaHepMCVerbosity = cms.untracked.bool(True),
        PGunParameters = cms.PSet(
          ParticleID = cms.vint32(DUMMYIDs),
          AddAntiParticle = cms.bool(True),
          MinPhi = cms.double(-3.14159265359),
          MaxPhi = cms.double(3.14159265359),
          MINTHRESHSTRING = cms.double(DUMMYTHRESHMIN),
          MAXTHRESHSTRING = cms.double(DUMMYTHRESHMAX),
          MinEta = cms.double(1.479),
          MaxEta = cms.double(3.0)
          ),
        PythiaParameters = cms.PSet(parameterSets = cms.vstring())
    )
elif gunmode == 'closeby':
    process.generator = cms.EDProducer("GUNPRODUCERTYPE",
        AddAntiParticle = cms.bool(False),
        PGunParameters = cms.PSet(
            PartID = cms.vint32(DUMMYIDs),
            EnMin = cms.double(DUMMYTHRESHMIN),
            EnMax = cms.double(DUMMYTHRESHMAX),
            RMin = cms.double(DUMMYRMIN),
            RMax = cms.double(DUMMYRMAX),
            ZMin = cms.double(DUMMYZMIN),
            ZMax = cms.double(DUMMYZMAX),
            Delta = cms.double(DUMMYDELTA),
            Pointing = cms.bool(DUMMYPOINTING),
            Overlapping = cms.bool(DUMMYOVERLAPPING),
            MaxEta = cms.double(DUMMYETAMAX),
            MinEta = cms.double(DUMMYETAMIN),
            MaxPhi = cms.double(3.14159265359/6.),
            MinPhi = cms.double(-3.14159265359/6.)            
        ),
        Verbosity = cms.untracked.int32(10),
        psethack = cms.string('single or multiple particles predefined E moving vertex'),
        firstRun = cms.untracked.uint32(1)
    )
