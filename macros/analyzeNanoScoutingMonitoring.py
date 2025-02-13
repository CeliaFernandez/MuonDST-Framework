import ROOT as r
import numpy as np
import optparse
from include.plotTools import *
import __main__
import mplhep as hep
import matplotlib.pyplot as plt
import time
from include.helper import helper

PWD = ''
for _p,path in enumerate(os.path.abspath(__main__.__file__).split('/')):
       if _p == len(os.path.abspath(__main__.__file__).split('/')) - 1: break
       PWD += path + '/'
print(PWD)

r.gROOT.LoadMacro(PWD+'include/tdrstyle.C')
r.gROOT.LoadMacro(PWD+'libraries/muon_scouting_run3.C')
r.gROOT.SetBatch(1)
r.setTDRStyle()
hep.style.use("CMS")

### Plotting functions

def getValues(histo):
    values = []
    for n in range(1, histo.GetNbinsX()+1):
        values.append(histo.GetBinContent(n))
    return np.array(values)

def plotHistograms(name, histos, var, bins, labels, isstack, ylog=False, xlog=False):
    hs = []
    colors = [ 'tab:'+c for c in ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']]
    
    for h in histos:
        hs.append(getValues(h))
    fig, ax = plt.subplots(figsize=(12, 9))
    htype = 'fill' if isstack else 'step'
    hep.histplot(
        hs,
        bins=bins,
        histtype=htype,
        color=colors[:len(hs)],
#        alpha=0.8,
        edgecolor="black" if isstack else colors[:len(hs)],
        label=labels,
        stack=isstack,
        ax=ax,
    )
    hep.cms.label("Preliminary", data=True, year='2024D', lumi='X', com='13.6')
    ax.set_xlabel(histos[0].GetXaxis().GetTitle(), fontsize=20)
    ax.set_ylabel("Events", fontsize=20)
    if ylog:
        ax.set_yscale('log')
        ax.set_ylim(0.1, 100*max([max(x) for x in hs]))
    if xlog:
        ax.set_xscale('log')
    ax.set_xlim(bins[0], bins[-1])
    legsize = 15 if len(labels)<7 else 10
    ax.legend(fontsize=15)
    fig.savefig(name+".png", dpi=140)
    

if __name__ == "__main__":

    parser = optparse.OptionParser(usage='usage: %prog [opts] FilenameWithSamples', version='%prog 1.0')
    parser.add_option('--l1', action='store', type=str,  dest='l1', default='Total', help='Total or L1 seed name')
    parser.add_option('--inDir', action='store', type=str,  dest='inDir', default='Total', help='Input dir')
    parser.add_option('--tag', action='store', type=str,  dest='tag', default='tag', help='Input dir')
    parser.add_option('--hlt', action='store', type=str,  dest='hlt', default='', help='HLT path')
    parser.add_option('--muon', action='store', type=str,  dest='muon', default='ScoutingMuonNoVtx', help='the muon')
    parser.add_option('-s', '--step', action='store', type=int,  dest='step', default=0, help='Input dir')
    parser.add_option('-n', '--number', action='store', type=int,  dest='number', default=0, help='Input dir')
    (opts, args) = parser.parse_args()

    ## Running parameters
    l1seed = opts.l1
    inputdir = opts.inDir
    step = opts.step
    number = opts.number
    tag = opts.tag
    hlt = opts.hlt
    muon = opts.muon
    redirector = 'root://cmsxrootd.fnal.gov' # root://cmsxrootd.fnal.gov | root://hip-cms-se.csc.fi
    central = True
    
    ## Load samples
    #inputdir = '/eos/user/f/fernance/DST-Muons/2024E_dimuon/ScoutingPFRun3/2024E_dimuon/240610_213819' # 2024D
    print('Reading from ', inputdir)
    nfiles = 0
    files = []
    if redirector:
        help = helper(inputdir, central, redirector)
        fileNames = help.getFiles(step, number)
    else:
        tchain = r.TChain('Events')
        for root, dirs, files in os.walk(inputdir):
            for f in files:
                if '.root' in f:
                    #print('Including %s file'%(f))
                    tchain.Add(os.path.join(root, f))
                    nfiles += 1
                    #break
    nfiles == len(files)

    ## Load dataframe
    # print(files)
    rdf = r.RDataFrame("Events", files)
    print(f'Init RDataFrame with {rdf.Count().GetValue()} entries in files from {step*number} to {step*number + number}')
    
    ## DST path selection
    if (hlt != '' and hlt!='none'):
        rdf = rdf.Filter("%s  == 1"%(hlt))

    ## Number of muons selection
    rdf = rdf.Filter("((nMuon  > 1) && (n%s > 1))"%(muon))

    ## Definitions
    print('Setting definitions...')

    rdf = rdf.Define("Muon_vec", "GetTLorentzVector(Muon_pt, Muon_eta, Muon_phi, 0.106)")
    rdf = rdf.Define("%s_vec"%(muon), "GetTLorentzVector(%s_pt, %s_eta, %s_phi, 0.106)"%(muon,muon,muon))
    rdf = rdf.Define("DiMuon_idx", "GetDimuonPairs(Muon_charge, Muon_vec)")
    rdf = rdf.Define("Di%s_idx"%(muon), "GetMatchedObjects(DiMuon_idx, Muon_vec, %s_vec)"%(muon))
    rdf = rdf.Define("Good_DiMuon_idx", "PruneDimuonPairs(DiMuon_idx, Di%s_idx)"%muon)
    rdf = rdf.Define("Good_Di%s_idx"%(muon), "PruneDimuonPairs(Di%s_idx, Di%s_idx)"%(muon,muon))
    #rdf = rdf.Define("max_idx", "ROOT::VecOps::Max(Good_Di%s_idx)"%(muon))
    rdf = rdf.Define("DiMuon_mass", "GetDimuonMass(Good_DiMuon_idx, Muon_vec)")
    rdf = rdf.Define("Di%s_mass"%(muon), "GetDimuonMass(Good_Di%s_idx, %s_vec)"%(muon,muon))
    ## rdf = rdf.Define("DiMuon_mass", "GetDimuonMass(DiMuon_idx, Muon_vec)")
    ## rdf = rdf.Define("Di%s_idx"%(muon), "GetDimuonPairs(%s_charge, %s_vec)"%(muon,muon))
    ## rdf = rdf.Define("Di%s_mass"%(muon), "GetDimuonMass(Di%s_idx, %s_vec)"%(muon,muon))
    #rdf = rdf.Define("SVNoVtx_pt1", "GetElements<float>(MuonNoVtx_pt, SVNoVtx_idx1)")
    #rdf = rdf.Define("ScoutingDiMuonVtx_mass", "sqrt(2*ScoutingMuonVtx_pt[0]*ScoutingMuonVtx_pt[1]*(cosh(ScoutingMuonVtx_eta[0] - ScoutingMuonVtx_eta[1]) - cos(ScoutingMuonVtx_phi[0] - ScoutingMuonVtx_phi[1])))")
    #rdf = rdf.Define("DiMuon_mass", "sqrt(2*Muon_pt[0]*Muon_pt[1]*(cosh(Muon_eta[0] - Muon_eta[1]) - cos(Muon_phi[0] - Muon_phi[1])))")
    print('Definitions set')



    ## Post-filter
    #rdf = rdf.Filter("(Good_DiMuon_idx.size() == 2) && (Good_Di%s_idx.size() == 2)"%(muon))
    rdf = rdf.Filter("(DiMuon_mass.size() == 1) && (Di%s_mass.size() == 1)"%(muon))
    #rdf = rdf.Filter("(Good_Di%s_idx.size() == 2)"%muon)
    #rdf = rdf.Filter("(max_idx > %s_vec.size())"%(muon))
    #rdf.Display(['DiMuon_idx', 'Di%s_idx'%muon]).Print()
    #rdf.Display(['Good_DiMuon_idx', 'Good_Di%s_idx'%muon, 'max_idx', '%s_vec'%(muon)]).Print()
    #rdf.Display(['DiMuon_mass', 'Di%s_mass'%muon]).Print()
    
    ## L1 rdfs (Saved for later because it is not included in Nano so far)
    #if l1seed == 'Total':
    #    condition = '(L1_DoubleMu_15_7 || L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7 || L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18 || L1_DoubleMu8_SQ || L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6 || L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4 || L1_DoubleMu4p5_SQ_OS_dR_Max1p2 || L1_DoubleMu0_Upt15_Upt7 | L1_DoubleMu0_Upt6_IP_Min1_Upt4)'
    #    rdf = rdf.Filter(condition)
    #else:
    #    rdf = rdf.Filter("%s == 1"%(l1seed))
    #print(f'{l1seed} RDataFrame has {rdf.Count().GetValue()} entries')
    print(f'RDataFrame has {rdf.Count().GetValue()} entries')

    ## Filling
    histo_cfg = []
    mbins = [0.215]
    while (mbins[-1]<250):
        mbins.append(1.01*mbins[-1])
    pt_bins = np.linspace(0, 50, 101)
    eta_bins = np.linspace(-3, 3, 51)
    phi_bins = np.linspace(-3.14, 3.14, 51)
    """
    histo_cfg.append(['Di%s_mass'%(muon), r'; Mass $m_{\mu\mu}$ (GeV); Number of dimuons', np.array(mbins)])
    histo_cfg.append(['DiMuon_mass', r'; Mass $m_{\mu\mu}$ (GeV); Number of dimuons', np.array(mbins)])
    #histo_cfg.append(['ScoutingMuonVtx_pt', r'; Muon $p_{T}$ (GeV); Number of muons', pt_bins])

    histos = []
    for cfg in histo_cfg:
        histos.append(rdf.Histo1D((cfg[0], cfg[1], len(cfg[2])-1, cfg[2]), cfg[0]))
        print('Histogram with %f'%(histos[-1].GetEntries()))
    """
    histos = []
    histos.append(rdf.Histo1D(('DiMuon_mass', r'; Mass $m_{\mu\mu}$ (GeV); Number of dimuons', len(np.array(mbins))-1, np.array(mbins)), 'DiMuon_mass'))
    histos.append(rdf.Histo1D(('Di%s_mass'%(muon), r'; Mass $m_{\mu\mu}$ (GeV); Number of dimuons', len(np.array(mbins))-1, np.array(mbins)), 'Di%s_mass'%(muon)))
    histos.append(rdf.Histo2D(('2D_mass', r'; Offline mass $m_{\mu\mu}$ (GeV); Scouting mass $m_{\mu\mu}$ (GeV)', len(np.array(mbins))-1, np.array(mbins), len(np.array(mbins))-1, np.array(mbins)), 'DiMuon_mass', 'Di%s_mass'%(muon)))
    for histo in histos:
        print('Histogram with %f'%(histo.GetEntries()))

    ## Save histograms
    outputdir = '/eos/user/f/fernance/DST-Muons' + '/ScoutingOutput_%s_%s/'%(tag, l1seed)
    print('Saving in %s'%outputdir)
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    out_ = r.TFile(outputdir + 'output_%s_%s_%s.root'%(tag, l1seed, str(step)), 'RECREATE')
    for h in histos:
        h.Write()
    out_.Close()


