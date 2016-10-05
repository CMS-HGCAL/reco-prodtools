# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options: SingleGammaPt35_cfi --conditions auto:run2_mc -n 10 --era Phase2C2 --eventcontent FEVTDEBUGHLT --relval 10000,100 -s GEN,SIM,DIGI:pdigi_valid,L1,DIGI2RAW,HLT:@fake --datatier GEN-SIM-DIGI-RAW --beamspot Realistic50ns13TeVCollision --customise SLHCUpgradeSimulations/Configuration/combinedCustoms.cust_2023tilted --geometry Extended2023D3 --no_exec --fileout file:step1_DIGIRAW.root
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('HLT',eras.Phase2C2)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2023D3Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2023D3_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic50ns13TeVCollision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.SimIdeal_cff')
process.load('Configuration.StandardSequences.Digi_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.DigiToRaw_cff')
process.load('HLTrigger.Configuration.HLT_Fake_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(DUMMYEVTSPERJOB)
)

process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
                                                   generator = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('HepJamesRandom')
                ),
                                                   mix = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('TRandom3')
                ),
                                                   VtxSmeared = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('TRandom3')
                ),
                                                   g4SimHits = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('TRandom3')
                ),
                                                   simMuonGEMDigis = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('TRandom3')
                ),
                                                   simMuonME0Digis = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('TRandom3')
                ),
                                                   simMuonCSCDigis = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('TRandom3')
                ),
                                                   simMuonDTDigis = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('TRandom3')
                ),
                                                   simMuonRPCDigis = cms.PSet(
                initialSeed = cms.untracked.uint32(DUMMYSEED),
                engineName = cms.untracked.string('TRandom3')
                )
                                                   )


# Input source
process.source = cms.Source("EmptySource")

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('MultipleParticleGun_cfi'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.FEVTDEBUGHLToutput = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    ),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM-DIGI-RAW'),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(10485760),
    fileName = cms.untracked.string('file:DUMMYFILENAME'),
    outputCommands = process.FEVTDEBUGHLTEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
process.mix.digitizers = cms.PSet(process.theDigitizersValid)
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

process.RandomNumberGeneratorService.generator.initialSeed = DUMMYSEED

process.generator = cms.EDProducer("FlatRandomPtGunProducer",
    AddAntiParticle = cms.bool(True),
    PGunParameters = cms.PSet(
        MaxEta = cms.double(3.0),
        MaxPhi = cms.double(3.14159265359),
        MaxPt = cms.double(DUMMYPTMAX),
        MinEta = cms.double(1.479),
        MinPhi = cms.double(-3.14159265359),
        MinPt = cms.double(DUMMYPTMIN),
        PartID = cms.vint32(DUMMYIDs)
    ),
    Verbosity = cms.untracked.int32(0),
    firstRun = cms.untracked.uint32(1),
    psethack = cms.string('multiple particles predefined pT eta 1p479 to 3')
)


# Path and EndPath definitions
process.generation_step = cms.Path(process.pgen)
process.simulation_step = cms.Path(process.psim)
process.digitisation_step = cms.Path(process.pdigi_valid)
process.L1simulation_step = cms.Path(process.SimL1Emulator)
process.digi2raw_step = cms.Path(process.DigiToRaw)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.FEVTDEBUGHLToutput)

# Schedule definition
process.schedule = cms.Schedule(process.generation_step,process.genfiltersummary_step,process.simulation_step,process.digitisation_step,process.L1simulation_step,process.digi2raw_step)
process.schedule.extend(process.HLTSchedule)
process.schedule.extend([process.endjob_step,process.FEVTDEBUGHLToutput_step])
# filter all path with the production filter sequence
for path in process.paths:
	getattr(process,path)._seq = process.generator * getattr(process,path)._seq

# customisation of the process.

# Automatic addition of the customisation function from SLHCUpgradeSimulations.Configuration.combinedCustoms
from SLHCUpgradeSimulations.Configuration.combinedCustoms import cust_2023tilted

#call to customisation function cust_2023tilted imported from SLHCUpgradeSimulations.Configuration.combinedCustoms
process = cust_2023tilted(process)

# Automatic addition of the customisation function from HLTrigger.Configuration.customizeHLTforMC
from HLTrigger.Configuration.customizeHLTforMC import customizeHLTforFullSim

#call to customisation function customizeHLTforFullSim imported from HLTrigger.Configuration.customizeHLTforMC
process = customizeHLTforFullSim(process)

# End of customisation functions

# Customisation from command line
