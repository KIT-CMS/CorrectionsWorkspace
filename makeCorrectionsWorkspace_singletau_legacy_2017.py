#!/usr/bin/env python
import ROOT
import imp
import json
from array import array
import numpy as np

wsptools = imp.load_source('wsptools', 'workspaceTools.py')

def GetFromTFile(str):
    f = ROOT.TFile(str.split(':')[0])
    obj = f.Get(str.split(':')[1]).Clone()
    f.Close()
    return obj

# Boilerplate
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.RooWorkspace.imp = getattr(ROOT.RooWorkspace, 'import')
ROOT.TH1.AddDirectory(0)

w = ROOT.RooWorkspace('w')

####################################################################################################
# Single tau trigger weights
####################################################################################################

loc = 'inputs/2017/singletau/DESY/'

# Wrap input histograms in workspace.
histsToWrap = []
for sample in ["_mc", "_emb"]:
    for trg in ["singleANDdouble_t", "single_t", "double_t"]:
        for dm in ["1pr", "1pr1pi0", "3pr"]:
            for region in ["barrel", "endcap"]:
                histsToWrap.append(
                        (loc + 'eff_tauTriggers_2017_v3.root:trg_{trg}{sample}_{dm}_{reg}'.format(trg=trg,
                                                                                               sample=sample,
                                                                                               dm=dm,
                                                                                               reg=region),
                         't_trg_{trg}{sample}_{dm}_{reg}'.format(trg=trg,
                                                                 sample=sample,
                                                                 dm=dm,
                                                                 reg=region)
                        )
                )

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['t_pt'],
                          GetFromTFile(task[0]), name=task[1])

# Build histograms inclusive in eta.
w.factory('expr::t_abs_eta("TMath::Abs(@0)", t_eta[0])')

for sample in ["_mc", "_emb"]:
    for trg in ["singleANDdouble_t", "single_t", "double_t"]:
        for dm in ["1pr", "1pr1pi0", "3pr"]:
            w.factory('expr::t_trg_{trg}{sample}_{dm}("(@0<=1.48)*@1+(@0>1.48)*(@0<2.1)*@2", t_abs_eta, t_trg_{trg}{sample}_{dm}_barrel, t_trg_{trg}{sample}_{dm}_endcap)'.format(trg=trg, sample=sample, dm=dm))

# Build histogram inclusive in eta and dm.
for sample in ["_mc", "_emb"]:
    for trg in ["singleANDdouble_t", "single_t", "double_t"]:
        w.factory('expr::t_trg_{trg}{sample}("(@0==0)*(@1)+(@0==1)*(@2)+(@0==2)*(@2)+(@0==10)*(@3)+(@0==11)*(@3)", t_dm[0], t_trg_{trg}{sample}_1pr, t_trg_{trg}{sample}_1pr1pi0, t_trg_{trg}{sample}_3pr)'.format(sample=sample, trg=trg))

# Wrap histograms for single tau efficiencies measured in W* events.
histsToWrap = [
        (loc + 'SingleTauTriggerEff_MediumDeepTau2017v2p1_2017.root:MC', 't_trg_single_t_wstar_mc'),
        (loc + 'SingleTauTriggerEff_MediumDeepTau2017v2p1_2017.root:Data', 't_trg_single_t_wstar_data'),
        (loc + 'SingleTauTriggerEff_MediumDeepTau2017v2p1_2017.root:SF', 't_trg_single_t_wstar_ratio')
]
for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['t_pt'],
                          GetFromTFile(task[0]), name=task[1])


w.Print()
w.writeToFile('output/htt_scalefactors_singletau_legacy_2017.root')
w.Delete()
