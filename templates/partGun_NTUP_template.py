# coding: utf-8

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from reco_prodtools.templates.NTUP_fragment import process


# option parsing
options = VarParsing('python')
options.setDefault('inputFiles', DUMMYINPUTFILELIST)
options.setDefault('outputFile', 'file:DUMMYFILENAME')
options.setDefault('maxEvents', DUMMYEVTSPERJOB)
options.parseArguments()

process.maxEvents.input = cms.untracked.int32(options.maxEvents)

process.source.fileNames = cms.untracked.vstring(options.inputFiles)

from FastSimulation.Event.ParticleFilter_cfi import *

process.ana = cms.EDAnalyzer('HGCalAnalysis',
                             detector = cms.string("all"),
                             inputTag_HGCalMultiCluster = cms.string("DUMMYMULCLUSTAG"),
                             rawRecHits = cms.bool(True),
                             verbose = cms.bool(True),
                             readCaloParticles = cms.bool(True),
                             readGenParticles = cms.bool(False),
                             storeGenParticleOrigin = cms.bool(DUMMYSGO),
                             storeGenParticleExtrapolation = cms.bool(DUMMYSGE),
                             storeGunParticles = cms.bool(True),
                             storeElectrons = cms.bool(True),
                             storePFCandidates = cms.bool(DUMMYSPFC),
                             layerClusterPtThreshold = cms.double(-1),  # All LayerCluster belonging to a multicluster are saved; this Pt threshold applied to the others
                             TestParticleFilter = ParticleFilterBlock.ParticleFilter
)

process.ana.TestParticleFilter.protonEMin = cms.double(100000)
process.ana.TestParticleFilter.etaMax = cms.double(3.1)


process.TFileService = cms.Service("TFileService", fileName = cms.string(
    options.__getattr__("outputFile", noTags=True)))

reRunClustering = DUMMYRECLUST

# Remove all registered paths and the schedule, so that only our ntuplizer paths will be executed
for p in process.paths: delattr(process,p)
delattr(process,'schedule')

if reRunClustering:
    # process.hgcalLayerClusters.minClusters = cms.uint32(0)
    # process.hgcalLayerClusters.realSpaceCone = cms.bool(True)
    # process.hgcalLayerClusters.multiclusterRadius = cms.double(2.)  # in cm if realSpaceCone is true
    # process.hgcalLayerClusters.dependSensor = cms.bool(True)
    # process.hgcalLayerClusters.ecut = cms.double(3.)  # multiple of sigma noise if dependSensor is true
    # process.hgcalLayerClusters.kappa = cms.double(9.)  # multiple of sigma noise if dependSensor is true
    #process.hgcalLayerClusters.deltac = cms.vdouble(2.,3.,5.) #specify delta c for each subdetector separately
    process.p = cms.Path(process.hgcalLayerClusters+process.ana)
else:
    process.p = cms.Path(process.ana)

process.schedule = cms.Schedule(process.p)
