# coding: utf-8

import math

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from reco_prodtools.templates.GSD_fragment import process

# option parsing
options = VarParsing('python')
options.setDefault('outputFile', 'file:DUMMYFILENAME')
options.setDefault('maxEvents', DUMMYEVTSPERJOB)
options.register("seed", DUMMYSEED, VarParsing.multiplicity.singleton, VarParsing.varType.int,
    "random seed")
options.parseArguments()

process.maxEvents.input = cms.untracked.int32(options.maxEvents)

# random seeds
process.RandomNumberGeneratorService.generator.initialSeed = cms.untracked.uint32(options.seed)
process.RandomNumberGeneratorService.VtxSmeared.initialSeed = cms.untracked.uint32(options.seed)
process.RandomNumberGeneratorService.mix.initialSeed = cms.untracked.uint32(options.seed)

# Input source
process.source.firstLuminosityBlock = cms.untracked.uint32(options.seed)

# Output definition
process.FEVTDEBUGHLToutput.fileName = cms.untracked.string(
    options.__getattr__("outputFile", noTags=True))

# helper
def calculate_rho(z, eta):
    return z * math.tan(2 * math.atan(math.exp(-eta)))

#DUMMYPUSECTION

gunmode = 'GUNMODE'

if gunmode == 'default':
    process.generator = cms.EDProducer("GUNPRODUCERTYPE",
        AddAntiParticle = cms.bool(True),
        PGunParameters = cms.PSet(
            MaxEta = cms.double(DUMMYETAMAX),
            MaxPhi = cms.double(math.pi),
            MAXTHRESHSTRING = cms.double(DUMMYTHRESHMAX),
            MINTHRESHSTRING = cms.double(DUMMYTHRESHMIN),
            MinEta = cms.double(DUMMYETAMIN),
            MinPhi = cms.double(-math.pi),
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
          MinPhi = cms.double(-math.pi),
          MaxPhi = cms.double(math.pi),
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
            RandomShoot = cms.bool(DUMMYRANDOMSHOOT),
            NParticles = cms.int32(DUMMYNRANDOMPARTICLES),
            MaxEta = cms.double(DUMMYETAMAX),
            MinEta = cms.double(DUMMYETAMIN),
            MaxPhi = cms.double(math.pi / 6.),
            MinPhi = cms.double(-math.pi / 6.)
        ),
        Verbosity = cms.untracked.int32(10),
        psethack = cms.string('single or multiple particles predefined E moving vertex'),
        firstRun = cms.untracked.uint32(1)
    )
elif gunmode == 'closebydr':
    process.generator = cms.EDProducer("CloseByFlatDeltaRGunProducer",
        # particle ids
        particleIDs=cms.vint32(DUMMYIDs),
        # max number of particles to shoot at a time
        nParticles=cms.int32(DUMMYNRANDOMPARTICLES),
        # shoot exactly the particles defined in particleIDs in that order
        exactShoot=cms.bool(DUMMYEXACTSHOOT),
        # randomly shoot [1, nParticles] particles, each time randomly drawn from particleIDs
        randomShoot=cms.bool(DUMMYRANDOMSHOOT),
        # energy range
        eMin=cms.double(DUMMYTHRESHMIN),
        eMax=cms.double(DUMMYTHRESHMAX),
        # phi range
        phiMin=cms.double(-math.pi / 6.),
        phiMax=cms.double(math.pi / 6.),
        # longitudinal distance in cm
        zMin=cms.double(DUMMYZMIN),
        zMax=cms.double(DUMMYZMAX),
        # radial distance in cm
        rhoMin=cms.double(calculate_rho(DUMMYZMAX, 1.6)),
        rhoMax=cms.double(calculate_rho(DUMMYZMIN, 3.0)),
        # deltaR settings
        deltaRMin=cms.double(DUMMYRMIN),
        deltaRMax=cms.double(DUMMYRMAX),
        # debug flag
        debug=cms.untracked.bool(True),
    )
elif gunmode == 'physproc':

    # GUNPRODUCERTYPE is a string in the form of proc[:jetColl:threshold:min_jets]
    physicsProcess = 'GUNPRODUCERTYPE'
    proc_cfg = physicsProcess.split(':')
    proc = proc_cfg[0]

    # phase space cuts
    ptMin = DUMMYTHRESHMIN
    ptMax = DUMMYTHRESHMAX

    from reco_prodtools.templates.hgcBiasedGenProcesses_cfi import *

    #define the process
    print 'Setting process to', proc
    defineProcessGenerator(process, proc=proc, ptMin=ptMin, ptMax=ptMax)

    #set a filter path if it's available
    if len(proc_cfg)==4:
        jetColl = proc_cfg[1]
        thr = float(proc_cfg[2])
        minObj = int(proc_cfg[3])
        print 'Adding a filter with the following settings:'
        print '\tgen-jet collection for filtering:', jetColl
        print '\tpT threshold [GeV]:', thr
        print '\tmin. number of jets with the above threshold:', minObj
        filterPath = defineJetBasedBias(process, jetColl=jetColl, thr=thr, minObj=minObj)
        process.schedule.extend([filterPath])
        process.FEVTDEBUGHLToutput.SelectEvents.SelectEvents=cms.vstring(filterPath.label())
