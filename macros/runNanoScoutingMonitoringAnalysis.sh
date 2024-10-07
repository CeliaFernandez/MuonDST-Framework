#!/bin/bash

SCRAMARCH=el9_amd64_gcc12
CMSSWVERSION=CMSSW_14_0_7

while ! [ -z "$1" ]; do
    FLAGS="$FLAGS $1"; shift;
done

pushd /cvmfs/cms.cern.ch/${SCRAMARCH}/cms/cmssw/${CMSSWVERSION}/src
eval `scramv1 runtime -sh`
pushd

cp /afs/cern.ch/work/f/fernance/private/Scouting/2024Analysis/CMSSW_14_0_7/src/Analysis/MuonDST-Framework/macros/analyzeNanoScoutingMonitoring.py .
cp -r /afs/cern.ch/work/f/fernance/private/Scouting/2024Analysis/CMSSW_14_0_7/src/Analysis/MuonDST-Framework/macros/libraries .
cp -r /afs/cern.ch/work/f/fernance/private/Scouting/2024Analysis/CMSSW_14_0_7/src/Analysis/MuonDST-Framework/macros/include .
echo ${FLAGS}
python3 analyzeNanoScoutingMonitoring.py ${FLAGS}
rm analyzeNanoScoutingMonitoring.py