import FWCore.ParameterSet.Config as cms

from reco_prodtools.templates.RECO_fragment import process

process.maxEvents.input = cms.untracked.int32(DUMMYEVTSPERJOB)

# Input source
process.source.fileNames = cms.untracked.vstring(DUMMYINPUTFILELIST)

# Output definition
process.FEVTDEBUGHLToutput.fileName = cms.untracked.string('file:DUMMYFILENAME')
process.DQMoutput.fileName = cms.untracked.string('file:DUMMYDQMFILENAME')

# Customisation from command line
# process.hgcalLayerClusters.minClusters = cms.uint32(3)
#those below are all now the default values - just there to illustrate what can be customised
#process.hgcalLayerClusters.dependSensor = cms.bool(True)
#process.hgcalLayerClusters.ecut = cms.double(3.) #multiple of sigma noise if dependSensor is true
#process.hgcalLayerClusters.kappa = cms.double(9.) #multiple of sigma noise if dependSensor is true
#process.hgcalLayerClusters.multiclusterRadii = cms.vdouble(2.,2.,2.) #(EE,FH,BH), in com
#process.hgcalLayerClusters.deltac = cms.vdouble(2.,2.,2.) #(EE,FH,BH), in cm
