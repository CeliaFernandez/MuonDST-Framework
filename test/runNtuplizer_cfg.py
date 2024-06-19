import FWCore.ParameterSet.Config as cms
import os


process = cms.Process("demo")
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load('Configuration.StandardSequences.Services_cff')

# Debug printout and summary.
process.load("FWCore.MessageService.MessageLogger_cfi")

process.options = cms.untracked.PSet(
  wantSummary = cms.untracked.bool(True),
  # Set up multi-threaded run. Must be consistent with config.JobType.numCores in crab_cfg.py.
  numberOfThreads=cms.untracked.uint32(1)
)

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag

# Select number of events to be processed
nEvents = 100000
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(nEvents) )

#
process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )

# Read events
#listOfFiles = ['file:/eos/cms/store/data/Run2024D/ScoutingPFRun3/HLTSCOUT/v1/000/380/945/00000/416c2734-64ac-4c85-a911-a6e6af7af0ec.root']
inputdir = '/eos/cms/store/data/Run2024D/ScoutingPFRun3/HLTSCOUT/v1/000/380/945/00000/'
listOfFiles = ['file:' + os.path.join(inputdir, f) for f in os.listdir(inputdir) if '.root' in f][:10]
print(listOfFiles[0])
listOfFiles = "/store/data/Run2023D/ScoutingPFRun3/RAW/v1/000/369/869/00000/0a6c87bc-9436-47b0-bc52-a5714dd4f38c.root"
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring( listOfFiles ),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents = cms.untracked.uint32(0)
  )
process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_Prompt_v2')

## Define the process to run 
## 
process.load("Analysis.MuonDST-Framework.ntuples_cfi")

#process.p = cms.EndPath(process.ntuples)
process.p = cms.Path(process.gtStage2Digis+process.ntuples)

