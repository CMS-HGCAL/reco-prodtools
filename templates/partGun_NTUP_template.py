import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

process = cms.Process("Demo")
process.load('Configuration.Geometry.GeometryExtended2023simReco_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_PostLS1_cff')
process.load('Configuration.EventContent.EventContent_cff')
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('RecoLocalCalo.HGCalRecHitDump.imagingClusterHGCal_cfi')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(DUMMYEVTSPERJOB) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        DUMMYINPUTFILELIST
    ),
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck")
)

process.ana = cms.EDAnalyzer('HGCalAnalysis',
                             detector = cms.string("both"),
                             depthClusteringCone = cms.double(0.015)
)

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("file:DUMMYFILENAME")

                                   )
process.imagingClusterHGCal.ecut = cms.double(0.01)
process.imagingClusterHGCal.eventsToDisplay = cms.untracked.uint32(1)

process.p = cms.Path(process.imagingClusterHGCal+process.ana)
