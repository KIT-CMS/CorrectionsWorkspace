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
ROOT.gROOT.LoadMacro("CrystalBallEfficiency.cxx+")

w = ROOT.RooWorkspace('w')

### Muon tracking efficiency scale factor from the Tracking POG
loc = 'inputs/2018/TrackingPOG'

muon_trk_eff_hist = wsptools.TGraphAsymmErrorsToTH1D(GetFromTFile(loc+'/fits.root:ratio_eff_eta3_dr030e030_corr'))
wsptools.SafeWrapHist(w, ['m_eta'], muon_trk_eff_hist, name='m_trk_ratio')

### Electron reconstruction efficiency scale factor from the egamma POG
loc = 'inputs/2018/EGammaPOG'

electron_trk_eff_hist = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_updatedAll_2018.root:EGamma_SF2D')
electron_reco_eff_hist = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_updatedAll_2018.root:EGamma_SF2D')
wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_trk_eff_hist, name='e_trk_ratio')

wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_reco_eff_hist, name='e_reco_ratio')

# for embedded we (IC) derived an additional correction based on the MC and embedding reco efficiency differences, these are applied on top of the usual data/MC SFs
# note this is not needed for muons as differences between embedding and MC are very small

wsptools.SafeWrapHist(w, ['e_eta','e_pt'], GetFromTFile('inputs/2018/ICSF/elec_trk/embed_electron_reco_efficiencies_2018.root:embed_sf'), name='e_trk_embed')
w.factory('expr::e_trk_embed_ratio("@0*@1",e_trk_ratio, e_trk_embed)')


################################################
### KIT muon scale factors for normalisation ####
################################################

loc_kit = 'inputs/2018/KIT/2018'

histsToWrap = [(loc_kit + '/Mu8/muon_SFs.root:Mu8_pt_eta_bins', 'm_sel_trg8_1_data'),
               (loc_kit + '/Mu17/muon_SFs.root:Mu17_pt_eta_bins','m_sel_trg17_1_data')]

for task in histsToWrap:
    wsptools.SafeWrapHist(
        w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
        GetFromTFile(task[0]),
        name=task[1])

histsToWrap = [(loc_kit + '/Mu8/muon_SFs.root:Mu8_pt_eta_bins', 'm_sel_trg8_2_data'),
               (loc_kit + '/Mu17/muon_SFs.root:Mu17_pt_eta_bins','m_sel_trg17_2_data')]

for task in histsToWrap:
    wsptools.SafeWrapHist(
        w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
        GetFromTFile(task[0]),
        name=task[1])

    w.factory('expr::m_sel_trg_data("0.9946*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
    w.factory('expr::m_sel_trg_ratio("min(1./@0,2)", m_sel_trg_data)')

histsToWrap = [
    (loc_kit + '/muonEmbID.root:ID_pt_eta_bins', 'm_sel_idEmb_data')
]
wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
                          GetFromTFile(histsToWrap[0][0]),
                          name=histsToWrap[0][1])

w.factory('expr::m_sel_idEmb_ratio("min(1./@0,20)", m_sel_idEmb_data)')

### DESY electron & muon tag and probe results
loc = 'inputs/2018/LeptonEfficiencies'

 #electron triggers
desyHistsToWrap = [
    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'MC', 'e_trg_EleTau_Ele24Leg_desy_mc'),
    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'Data', 'e_trg_EleTau_Ele24Leg_desy_data'),
    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'MC', 'e_trg_SingleEle_Ele32OREle35_desy_mc'),
    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'Data', 'e_trg_SingleEle_Ele32OREle35_desy_data')
]

for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['trg_EleTau_Ele24Leg_desy','trg_SingleEle_Ele32OREle35_desy']:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))

# muon triggers
desyHistsToWrap = [
    (loc+'/Muon/Run2017/Muon_MuTau_IsoMu20.root',           'MC', 'm_trg_MuTau_Mu20Leg_desy_mc'),
    (loc+'/Muon/Run2017/Muon_MuTau_IsoMu20.root',           'Data', 'm_trg_MuTau_Mu20Leg_desy_data'),
    (loc+'/Muon/Run2017/Muon_IsoMu24orIsoMu27.root',           'MC', 'm_trg_SingleMu_Mu24ORMu27_desy_mc'),
    (loc+'/Muon/Run2017/Muon_IsoMu24orIsoMu27.root',           'Data', 'm_trg_SingleMu_Mu24ORMu27_desy_data')
]

for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['trg_MuTau_Mu20Leg_desy','trg_SingleMu_Mu24ORMu27_desy']:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))

### KIT electron/muon tag and probe results

# trigger SFs Muons from KIT
loc = 'inputs/2018/KIT/v18_2/'


histsToWrap = [
    (loc+'muon_TP_Data_2018_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                'm_id_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                  'm_id_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',           'm_id_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',              'm_iso_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                'm_iso_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',         'm_iso_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'm_aiso1_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',                'm_aiso1_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',         'm_aiso1_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'm_aiso2_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                'm_aiso2_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',         'm_aiso2_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins',      'm_trg24_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins',        'm_trg24_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins', 'm_trg24_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta',      'm_trg24_aiso1_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta',        'm_trg24_aiso1_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta', 'm_trg24_aiso1_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta',      'm_trg24_aiso2_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta',        'm_trg24_aiso2_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta', 'm_trg24_aiso2_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins',      'm_trg27_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins',        'm_trg27_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins', 'm_trg27_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta',      'm_trg27_aiso1_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta',        'm_trg27_aiso1_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta', 'm_trg27_aiso1_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta',      'm_trg27_aiso2_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta',        'm_trg27_aiso2_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta', 'm_trg27_aiso2_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins',      'm_trg24_27_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins',        'm_trg24_27_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins', 'm_trg24_27_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta',      'm_trg24_27_aiso1_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta',        'm_trg24_27_aiso1_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta', 'm_trg24_27_aiso1_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta',      'm_trg24_27_aiso2_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta',        'm_trg24_27_aiso2_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta', 'm_trg24_27_aiso2_kit_embed'),
 
    (loc+'crossmuon_TP_Data_2018_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_data'), 
    (loc+'crossmuon_TP_DY_2018_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_mc'), 
    (loc+'crossmuon_TP_Embedding_2018_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_embed'),

]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_binned_kit_data', ['m_trg24_kit_data', 'm_trg24_aiso1_kit_data', 'm_trg24_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_binned_kit_mc', ['m_trg24_kit_mc', 'm_trg24_aiso1_kit_mc', 'm_trg24_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_binned_kit_embed', ['m_trg24_kit_embed', 'm_trg24_aiso1_kit_embed', 'm_trg24_aiso2_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg27_binned_kit_data', ['m_trg27_kit_data', 'm_trg27_aiso1_kit_data', 'm_trg27_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg27_binned_kit_mc', ['m_trg27_kit_mc', 'm_trg27_aiso1_kit_mc', 'm_trg27_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg27_binned_kit_embed', ['m_trg27_kit_embed', 'm_trg27_aiso1_kit_embed', 'm_trg27_aiso2_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_27_binned_kit_data', ['m_trg24_27_kit_data', 'm_trg24_27_aiso1_kit_data', 'm_trg24_27_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_27_binned_kit_mc', ['m_trg24_27_kit_mc', 'm_trg24_27_aiso1_kit_mc', 'm_trg24_27_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_27_binned_kit_embed', ['m_trg24_27_kit_embed', 'm_trg24_27_aiso1_kit_embed', 'm_trg24_27_aiso2_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_data', ['m_iso_kit_data', 'm_aiso1_kit_data', 'm_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_mc', ['m_iso_kit_mc', 'm_aiso1_kit_mc', 'm_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_embed', ['m_iso_kit_embed', 'm_aiso1_kit_embed', 'm_aiso2_kit_embed'])

for t in ['data', 'mc', 'embed']:
    w.factory('expr::m_idiso_kit_%s("@0*@1", m_id_kit_%s, m_iso_kit_%s)' % (t, t, t))
    w.factory('expr::m_idiso_binned_kit_%s("@0*@1", m_id_kit_%s, m_iso_binned_kit_%s)' % (t, t, t))

for t in ['trg24', 'trg24_binned', 'trg27', 'trg27_binned', 'trg24_27', 'trg24_27_binned', 'id', 'iso', 'iso_binned', 'idiso_binned', 'trg_MuTau_Mu20Leg' ]:
    w.factory('expr::m_%s_kit_ratio("@0/@1", m_%s_kit_data, m_%s_kit_mc)' % (t, t, t))
    w.factory('expr::m_%s_embed_kit_ratio("@0/@1", m_%s_kit_data, m_%s_kit_embed)' % (t, t, t))

# emu and mu+tau trigger and loose (<0.2) muon isolation scale factors from IC

loc = 'inputs/2018/ICSF/'

histsToWrap = [
    (loc+'EM_HI/muon_SFs.root:data_trg_eff', 'm_trg_23_data'),
    (loc+'EM_HI/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_mc'),
    (loc+'EM_HI/muon_SFs.root:embed_trg_eff', 'm_trg_23_embed'),
    (loc+'EM_LO/muon_SFs.root:data_trg_eff', 'm_trg_8_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_trg_eff', 'm_trg_8_embed'),
    (loc+'EM_LO/muon_SFs.root:data_iso_eff', 'm_looseiso_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_iso_eff', 'm_looseiso_embed'),

    (loc+'EM_HI/aiso/muon_SFs.root:data_trg_eff', 'm_trg_23_aiso_data'),
    (loc+'EM_HI/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_aiso_mc'),
    (loc+'EM_HI/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_23_aiso_embed'),
    (loc+'EM_LO/aiso/muon_SFs.root:data_trg_eff', 'm_trg_8_aiso_data'),
    (loc+'EM_LO/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_aiso_mc'),
    (loc+'EM_LO/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_8_aiso_embed'),
    (loc+'EM_LO/aiso/muon_SFs.root:data_iso_eff', 'm_looseiso_aiso_data'),
    (loc+'EM_LO/aiso/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_aiso_mc'),
    (loc+'EM_LO/aiso/muon_SFs.root:embed_iso_eff', 'm_looseiso_aiso_embed'), 

    (loc+'MU20/muon_SFs.root:data_trg_eff', 'm_trg_20_data'),
    (loc+'MU20/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_mc'),
    (loc+'MU20/muon_SFs.root:embed_trg_eff', 'm_trg_20_embed'),
    (loc+'MU20/aiso1/muon_SFs.root:data_trg_eff', 'm_trg_20_aiso1_data'),
    (loc+'MU20/aiso1/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_aiso1_mc'),
    (loc+'MU20/aiso1/muon_SFs.root:embed_trg_eff', 'm_trg_20_aiso1_embed'),
    (loc+'MU20/aiso2/muon_SFs.root:data_trg_eff', 'm_trg_20_aiso2_data'),
    (loc+'MU20/aiso2/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_aiso2_mc'),
    (loc+'MU20/aiso2/muon_SFs.root:embed_trg_eff', 'm_trg_20_aiso2_embed'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_23_data', ['m_trg_23_data', 'm_trg_23_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_23_mc', ['m_trg_23_mc', 'm_trg_23_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_23_embed', ['m_trg_23_embed', 'm_trg_23_aiso_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_8_data', ['m_trg_8_data', 'm_trg_8_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_8_mc', ['m_trg_8_mc', 'm_trg_8_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_8_embed', ['m_trg_8_embed', 'm_trg_8_aiso_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_20_data', ['m_trg_20_data', 'm_trg_20_aiso1_data', 'm_trg_20_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_20_embed', ['m_trg_20_embed', 'm_trg_20_aiso1_embed', 'm_trg_20_aiso2_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_20_mc', ['m_trg_20_mc', 'm_trg_20_aiso1_mc', 'm_trg_20_aiso2_mc'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_data', ['m_looseiso_data', 'm_looseiso_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_mc', ['m_looseiso_mc', 'm_looseiso_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_embed', ['m_looseiso_embed', 'm_looseiso_aiso_embed'])

w.factory('expr::m_looseiso_ratio("@0/@1", m_looseiso_data, m_looseiso_mc)')
w.factory('expr::m_looseiso_embed_ratio("@0/@1", m_looseiso_data, m_looseiso_embed)')

w.factory('expr::m_looseiso_binned_ratio("@0/@1", m_looseiso_binned_data, m_looseiso_binned_mc)')
w.factory('expr::m_looseiso_binned_embed_ratio("@0/@1", m_looseiso_binned_data, m_looseiso_binned_embed)')

for t in ['trg','trg_binned']:
    w.factory('expr::m_%s_23_ratio("@0/@1", m_%s_23_data, m_%s_23_mc)' % (t, t, t))
    w.factory('expr::m_%s_8_ratio("@0/@1", m_%s_8_data, m_%s_8_mc)' % (t, t, t))
    w.factory('expr::m_%s_20_ratio("@0/@1", m_%s_20_data, m_%s_20_mc)' % (t, t, t))
    w.factory('expr::m_%s_23_embed_ratio("@0/@1", m_%s_23_data, m_%s_23_embed)' % (t, t, t))
    w.factory('expr::m_%s_8_embed_ratio("@0/@1", m_%s_8_data, m_%s_8_embed)' % (t, t, t))
    w.factory('expr::m_%s_20_embed_ratio("@0/@1", m_%s_20_data, m_%s_20_embed)' % (t, t, t))

# trigger SFs Electrons from KIT
loc = 'inputs/2018/KIT/v18_2/'

histsToWrap = [
    (loc+'electron_TP_Data_2018_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                'e_id90_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                  'e_id90_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',           'e_id90_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                'e_id80_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                  'e_id80_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',           'e_id80_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',              'e_iso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                'e_iso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',         'e_iso_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',              'e_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',                'e_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',         'e_aiso_kit_embed'),
    # (loc+'electron_TP_Data_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'e_aiso2_kit_data'),
    # (loc+'electron_TP_DY_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                'e_aiso2_kit_mc'),
    # (loc+'electron_TP_Embedding_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',         'e_aiso2_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',      'e_trg_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',        'e_trg_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins', 'e_trg_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta',      'e_trg_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta',        'e_trg_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta', 'e_trg_aiso_kit_embed'),
    # (loc+'electron_TP_Data_2018_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',      'e_trg_aiso2_kit_data'),
    # (loc+'electron_TP_DY_2018_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',        'e_trg_aiso2_kit_mc'),
    # (loc+'electron_TP_Embedding_2018_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta', 'e_trg_aiso2_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins',      'e_trg27_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins',        'e_trg27_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins', 'e_trg27_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta',      'e_trg27_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta',        'e_trg27_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta', 'e_trg27_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins',      'e_trg32_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins',        'e_trg32_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins', 'e_trg32_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta',      'e_trg32_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta',        'e_trg32_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta', 'e_trg32_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins',      'e_trg32fb_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins',        'e_trg32fb_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins', 'e_trg32fb_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta',      'e_trg32fb_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta',        'e_trg32fb_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta', 'e_trg32fb_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins',      'e_trg35_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins',        'e_trg35_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins', 'e_trg35_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta',      'e_trg35_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta',        'e_trg35_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta', 'e_trg35_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins',      'e_trg27_trg32_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins',        'e_trg27_trg32_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins', 'e_trg27_trg32_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta',      'e_trg27_trg32_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta',        'e_trg27_trg32_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta', 'e_trg27_trg32_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins',      'e_trg27_trg35_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins',        'e_trg27_trg35_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins', 'e_trg27_trg35_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg27_trg35_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg27_trg35_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg27_trg35_aiso_kit_embed'),


    (loc+'electron_TP_Data_2018_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins',      'e_trg32_trg35_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins',        'e_trg32_trg35_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins', 'e_trg32_trg35_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg32_trg35_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg32_trg35_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg32_trg35_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins',      'e_trg27_trg32_trg35_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins',        'e_trg27_trg32_trg35_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins', 'e_trg27_trg32_trg35_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg27_trg32_trg35_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg27_trg32_trg35_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg27_trg32_trg35_aiso_kit_embed'),

    (loc+'crosselectron_TP_Data_2018_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',      'e_trg_EleTau_Ele24Leg_kit_data'),
    (loc+'crosselectron_TP_DY_2018_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',        'e_trg_EleTau_Ele24Leg_kit_mc'),
    (loc+'crosselectron_TP_Embedding_2018_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',      'e_trg_EleTau_Ele24Leg_kit_embed'),
    

]
for task in histsToWrap:
    print task
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])


wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_kit_data', ['e_trg_kit_data', 'e_trg_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_kit_mc', ['e_trg_kit_mc', 'e_trg_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_kit_embed', ['e_trg_kit_embed', 'e_trg_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_binned_kit_data', ['e_trg27_kit_data', 'e_trg27_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_binned_kit_mc', ['e_trg27_kit_mc', 'e_trg27_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_binned_kit_embed', ['e_trg27_kit_embed', 'e_trg27_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_binned_kit_data', ['e_trg32_kit_data', 'e_trg32_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_binned_kit_mc', ['e_trg32_kit_mc', 'e_trg32_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_binned_kit_embed', ['e_trg32_kit_embed', 'e_trg32_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32fb_binned_kit_data', ['e_trg32fb_kit_data', 'e_trg32fb_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32fb_binned_kit_mc', ['e_trg32fb_kit_mc', 'e_trg32fb_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32fb_binned_kit_embed', ['e_trg32fb_kit_embed', 'e_trg32fb_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg35_binned_kit_data', ['e_trg35_kit_data', 'e_trg35_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg35_binned_kit_mc', ['e_trg35_kit_mc', 'e_trg35_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg35_binned_kit_embed', ['e_trg35_kit_embed', 'e_trg35_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_binned_kit_data', ['e_trg27_trg32_kit_data', 'e_trg27_trg32_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_binned_kit_mc', ['e_trg27_trg32_kit_mc', 'e_trg27_trg32_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_binned_kit_embed', ['e_trg27_trg32_kit_embed', 'e_trg27_trg32_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg35_binned_kit_data', ['e_trg27_trg35_kit_data', 'e_trg27_trg35_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg35_binned_kit_mc', ['e_trg27_trg35_kit_mc', 'e_trg27_trg35_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg35_binned_kit_embed', ['e_trg27_trg35_kit_embed', 'e_trg27_trg35_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_trg35_binned_kit_data', ['e_trg32_trg35_kit_data', 'e_trg32_trg35_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_trg35_binned_kit_mc', ['e_trg32_trg35_kit_mc', 'e_trg32_trg35_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_trg35_binned_kit_embed', ['e_trg32_trg35_kit_embed', 'e_trg32_trg35_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_trg35_binned_kit_data', ['e_trg27_trg32_trg35_kit_data', 'e_trg27_trg32_trg35_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_trg35_binned_kit_mc', ['e_trg27_trg32_trg35_kit_mc', 'e_trg27_trg32_trg35_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_trg35_binned_kit_embed', ['e_trg27_trg32_trg35_kit_embed', 'e_trg27_trg32_trg35_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_kit_data', ['e_iso_kit_data', 'e_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_kit_mc', ['e_iso_kit_mc', 'e_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_kit_embed', ['e_iso_kit_embed', 'e_aiso_kit_embed'])


w.factory('expr::e_id90iso_kit_embed("@0*@1", e_id90_kit_embed, e_iso_kit_embed)')
w.factory('expr::e_id90iso_binned_kit_embed("@0*@1", e_id90_kit_embed, e_iso_binned_kit_embed)')
w.factory('expr::e_id80iso_kit_embed("@0*@1", e_id80_kit_embed, e_iso_kit_embed)')
w.factory('expr::e_id80iso_binned_kit_embed("@0*@1", e_id80_kit_embed, e_iso_binned_kit_embed)')

w.factory('expr::e_id90iso_kit_data("@0*@1", e_id90_kit_data, e_iso_kit_data)')
w.factory('expr::e_id90iso_binned_kit_data("@0*@1", e_id90_kit_data, e_iso_binned_kit_data)')
w.factory('expr::e_id80iso_kit_data("@0*@1", e_id80_kit_data, e_iso_kit_data)')
w.factory('expr::e_id80iso_binned_kit_data("@0*@1", e_id80_kit_data, e_iso_binned_kit_data)')

w.factory('expr::e_id90iso_kit_mc("@0*@1", e_id90_kit_mc, e_iso_kit_mc)')
w.factory('expr::e_id90iso_binned_kit_mc("@0*@1", e_id90_kit_mc, e_iso_binned_kit_mc)')
w.factory('expr::e_id80iso_kit_mc("@0*@1", e_id80_kit_mc, e_iso_kit_mc)')
w.factory('expr::e_id80iso_binned_kit_mc("@0*@1", e_id80_kit_mc, e_iso_binned_kit_mc)')

for t in ['trg', 'trg_binned', 'trg27_trg32', 'trg27_trg32_binned', 'trg27_trg35', 'trg27_trg35_binned', 'trg32_trg35', 'trg32_trg35_binned', 'trg27_trg32_trg35', 'trg27_trg32_trg35_binned', 'trg27', 'trg32', 'trg32fb', 'trg35','id90', 'id80', 'iso', 'iso_binned', 'id90iso_binned', 'id80iso_binned', 'trg_EleTau_Ele24Leg']:
    w.factory('expr::e_%s_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_mc)' % (t, t, t))
    w.factory('expr::e_%s_embed_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_embed)' % (t, t, t))

######### WORK IN PROGRESS
##################
# IC electron and muon id, iso, and trigger SFs for MC and embedding
##################

## electron
loc = 'inputs/2018/ICSF/'

histsToWrap = [

    (loc+'singleElec/electron_SFs.root:data_trg_eff', 'e_trg_ic_data'),
    (loc+'singleElec/electron_SFs.root:ZLL_trg_eff', 'e_trg_ic_mc'),
    (loc+'singleElec/electron_SFs.root:embed_trg_eff', 'e_trg_ic_embed'),
    # update aiso ones
    # (loc+'singleElec/aiso1/electron_SFs.root:data_trg_eff', 'e_trg_aiso1_ic_data'),
    # (loc+'singleElec/aiso1/electron_SFs.root:ZLL_trg_eff', 'e_trg_aiso1_ic_mc'),
    # (loc+'singleElec/aiso1/electron_SFs.root:embed_trg_eff', 'e_trg_aiso1_ic_embed'),
    # (loc+'singleElec/aiso2/electron_SFs.root:data_trg_eff', 'e_trg_aiso2_ic_data'),
    # (loc+'singleElec/aiso2/electron_SFs.root:ZLL_trg_eff', 'e_trg_aiso2_ic_mc'),
    # (loc+'singleElec/aiso2/electron_SFs.root:embed_trg_eff', 'e_trg_aiso2_ic_embed'),

    (loc+'singleElec/electron_SFs.root:data_iso_eff', 'e_iso_ic_data'),
    (loc+'singleElec/electron_SFs.root:ZLL_iso_eff', 'e_iso_ic_mc'),
    (loc+'singleElec/electron_SFs.root:embed_iso_eff', 'e_iso_ic_embed'),
    # update aiso ones
    # (loc+'singleElec/aiso1/electron_SFs.root:data_iso_eff', 'e_iso_aiso1_ic_data'),
    # (loc+'singleElec/aiso1/electron_SFs.root:ZLL_iso_eff', 'e_iso_aiso1_ic_mc'),
    # (loc+'singleElec/aiso1/electron_SFs.root:embed_iso_eff', 'e_iso_aiso1_ic_embed'),
    # (loc+'singleElec/aiso2/electron_SFs.root:data_iso_eff', 'e_iso_aiso2_ic_data'),
    # (loc+'singleElec/aiso2/electron_SFs.root:ZLL_iso_eff', 'e_iso_aiso2_ic_mc'),
    # (loc+'singleElec/aiso2/electron_SFs.root:embed_iso_eff', 'e_iso_aiso2_ic_embed'),

    (loc+'singleElec/electron_SFs.root:data_id_eff', 'e_id_ic_data'),
    (loc+'singleElec/electron_SFs.root:ZLL_id_eff', 'e_id_ic_mc'),
    (loc+'singleElec/electron_SFs.root:embed_id_eff', 'e_id_ic_embed'),

    (loc+'ET/electron_SFs.root:data_trg_eff', 'e_trg_24_ic_data'),
    (loc+'ET/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_ic_mc'),
    (loc+'ET/electron_SFs.root:embed_trg_eff', 'e_trg_24_ic_embed'),
    # update aiso ones
    # (loc+'ET/aiso1/electron_SFs.root:data_trg_eff', 'e_trg_24_aiso1_ic_data'),
    # (loc+'ET/aiso1/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_aiso1_ic_mc'),
    # (loc+'ET/aiso1/electron_SFs.root:embed_trg_eff', 'e_trg_24_aiso1_ic_embed'),
    # (loc+'ET/aiso2/electron_SFs.root:data_trg_eff', 'e_trg_24_aiso2_ic_data'),
    # (loc+'ET/aiso2/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_aiso2_ic_mc'),
    # (loc+'ET/aiso2/electron_SFs.root:embed_trg_eff', 'e_trg_24_aiso2_ic_embed'),

    (loc+'EM_HI/electron_SFs.root:data_trg_eff', 'e_trg_23_ic_data'),
    (loc+'EM_HI/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_ic_mc'),
    (loc+'EM_HI/electron_SFs.root:embed_trg_eff', 'e_trg_23_ic_embed'),
    (loc+'EM_LO/electron_SFs.root:data_trg_eff', 'e_trg_12_ic_data'),
    (loc+'EM_LO/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_ic_mc'),
    (loc+'EM_LO/electron_SFs.root:embed_trg_eff', 'e_trg_12_ic_embed'),

    # update aiso ones
    # (loc+'EM_HI/aiso/electron_SFs.root:data_trg_eff', 'e_trg_23_aiso_ic_data'),
    # (loc+'EM_HI/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_aiso_ic_mc'),
    # (loc+'EM_HI/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_23_aiso_ic_embed'),
    # (loc+'EM_LO/aiso/electron_SFs.root:data_trg_eff', 'e_trg_12_aiso_ic_data'),
    # (loc+'EM_LO/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_aiso_ic_mc'),
    # (loc+'EM_LO/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_12_aiso_ic_embed'),
]

for task in histsToWrap:
    print task[0], task[1]
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
#                                   'e_trg_23_binned_ic_data', ['e_trg_23_ic_data', 'e_trg_23_aiso_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
#                                   'e_trg_23_binned_ic_mc', ['e_trg_23_ic_mc', 'e_trg_23_aiso_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
#                                   'e_trg_23_binned_ic_embed', ['e_trg_23_ic_embed', 'e_trg_23_aiso_ic_embed'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
#                                   'e_trg_12_binned_ic_data', ['e_trg_12_ic_data', 'e_trg_12_aiso_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
#                                   'e_trg_12_binned_ic_mc', ['e_trg_12_ic_mc', 'e_trg_12_aiso_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
#                                   'e_trg_12_binned_ic_embed', ['e_trg_12_ic_embed', 'e_trg_12_aiso_ic_embed'])
#
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_trg_binned_ic_data', ['e_trg_ic_data', 'e_trg_aiso1_ic_data', 'e_trg_aiso2_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_trg_binned_ic_mc', ['e_trg_ic_mc', 'e_trg_aiso1_ic_mc', 'e_trg_aiso2_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_trg_binned_ic_embed', ['e_trg_ic_embed', 'e_trg_aiso1_ic_embed', 'e_trg_aiso2_ic_embed'])
#
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_trg_24_binned_ic_data', ['e_trg_24_ic_data', 'e_trg_24_aiso1_ic_data', 'e_trg_24_aiso2_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_trg_24_binned_ic_mc', ['e_trg_24_ic_mc', 'e_trg_24_aiso1_ic_mc', 'e_trg_24_aiso2_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_trg_24_binned_ic_embed', ['e_trg_24_ic_embed', 'e_trg_24_aiso1_ic_embed', 'e_trg_24_aiso2_ic_embed'])
#
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_iso_binned_ic_data', ['e_iso_ic_data', 'e_iso_aiso1_ic_data', 'e_iso_aiso2_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_iso_binned_ic_mc', ['e_iso_ic_mc', 'e_iso_aiso1_ic_mc', 'e_iso_aiso2_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
#                                   'e_iso_binned_ic_embed', ['e_iso_ic_embed', 'e_iso_aiso1_ic_embed', 'e_iso_aiso2_ic_embed'])

# temporarily take isolated SFs for all until anti iso ones are included
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_23_binned_ic_data', ['e_trg_23_ic_data', 'e_trg_23_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_23_binned_ic_mc', ['e_trg_23_ic_mc', 'e_trg_23_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_23_binned_ic_embed', ['e_trg_23_ic_embed', 'e_trg_23_ic_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_12_binned_ic_data', ['e_trg_12_ic_data', 'e_trg_12_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_12_binned_ic_mc', ['e_trg_12_ic_mc', 'e_trg_12_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_12_binned_ic_embed', ['e_trg_12_ic_embed', 'e_trg_12_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_binned_ic_data', ['e_trg_ic_data', 'e_trg_ic_data', 'e_trg_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_binned_ic_mc', ['e_trg_ic_mc', 'e_trg_ic_mc', 'e_trg_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_binned_ic_embed', ['e_trg_ic_embed', 'e_trg_ic_embed', 'e_trg_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_24_binned_ic_data', ['e_trg_24_ic_data', 'e_trg_24_ic_data', 'e_trg_24_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_24_binned_ic_mc', ['e_trg_24_ic_mc', 'e_trg_24_ic_mc', 'e_trg_24_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_24_binned_ic_embed', ['e_trg_24_ic_embed', 'e_trg_24_ic_embed', 'e_trg_24_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_iso_binned_ic_data', ['e_iso_ic_data', 'e_iso_ic_data', 'e_iso_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_iso_binned_ic_mc', ['e_iso_ic_mc', 'e_iso_ic_mc', 'e_iso_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_iso_binned_ic_embed', ['e_iso_ic_embed', 'e_iso_ic_embed', 'e_iso_ic_embed'])

w.factory('expr::e_idiso_ic_data("@0*@1", e_iso_ic_data, e_id_ic_data)' % vars())
w.factory('expr::e_idiso_ic_mc("@0*@1", e_iso_ic_mc, e_id_ic_mc)' % vars())
w.factory('expr::e_idiso_ic_embed("@0*@1", e_iso_ic_embed, e_id_ic_embed)' % vars())

w.factory('expr::e_idiso_binned_ic_data("@0*@1", e_iso_binned_ic_data, e_id_ic_data)' % vars())
w.factory('expr::e_idiso_binned_ic_mc("@0*@1", e_iso_binned_ic_mc, e_id_ic_mc)' % vars())
w.factory('expr::e_idiso_binned_ic_embed("@0*@1", e_iso_binned_ic_embed, e_id_ic_embed)' % vars())

for i in ['trg', 'trg_24', 'trg_12', 'trg_23', 'id', 'iso', 'idiso']:
  w.factory('expr::e_%(i)s_ic_ratio("@0/@1", e_%(i)s_ic_data, e_%(i)s_ic_mc)' % vars())
  w.factory('expr::e_%(i)s_ic_embed_ratio("@0/@1", e_%(i)s_ic_data, e_%(i)s_ic_embed)' % vars())
  w.factory('expr::e_%(i)s_binned_ic_ratio("@0/@1", e_%(i)s_binned_ic_data, e_%(i)s_binned_ic_mc)' % vars())
  w.factory('expr::e_%(i)s_binned_ic_embed_ratio("@0/@1", e_%(i)s_binned_ic_data, e_%(i)s_binned_ic_embed)' % vars())

## muon
loc = 'inputs/2018/ICSF/'

histsToWrap = [

    (loc+'singleMu/muon_SFs.root:data_trg_eff', 'm_trg_ic_data'),
    (loc+'singleMu/muon_SFs.root:ZLL_trg_eff', 'm_trg_ic_mc'),
    (loc+'singleMu/muon_SFs.root:embed_trg_eff', 'm_trg_ic_embed'),
    # update aiso ones
    # (loc+'singleMu/aiso1/muon_SFs.root:data_trg_eff', 'm_trg_aiso1_ic_data'),
    # (loc+'singleMu/aiso1/muon_SFs.root:ZLL_trg_eff', 'm_trg_aiso1_ic_mc'),
    # (loc+'singleMu/aiso1/muon_SFs.root:embed_trg_eff', 'm_trg_aiso1_ic_embed'),
    # (loc+'singleMu/aiso2/muon_SFs.root:data_trg_eff', 'm_trg_aiso2_ic_data'),
    # (loc+'singleMu/aiso2/muon_SFs.root:ZLL_trg_eff', 'm_trg_aiso2_ic_mc'),
    # (loc+'singleMu/aiso2/muon_SFs.root:embed_trg_eff', 'm_trg_aiso2_ic_embed'),

    (loc+'singleMu/muon_SFs.root:data_iso_eff', 'm_iso_ic_data'),
    (loc+'singleMu/muon_SFs.root:ZLL_iso_eff', 'm_iso_ic_mc'),
    (loc+'singleMu/muon_SFs.root:embed_iso_eff', 'm_iso_ic_embed'),
    # update aiso ones
    # (loc+'singleMu/aiso1/muon_SFs.root:data_iso_eff', 'm_iso_aiso1_ic_data'),
    # (loc+'singleMu/aiso1/muon_SFs.root:ZLL_iso_eff', 'm_iso_aiso1_ic_mc'),
    # (loc+'singleMu/aiso1/muon_SFs.root:embed_iso_eff', 'm_iso_aiso1_ic_embed'),
    # (loc+'singleMu/aiso2/muon_SFs.root:data_iso_eff', 'm_iso_aiso2_ic_data'),
    # (loc+'singleMu/aiso2/muon_SFs.root:ZLL_iso_eff', 'm_iso_aiso2_ic_mc'),
    # (loc+'singleMu/aiso2/muon_SFs.root:embed_iso_eff', 'm_iso_aiso2_ic_embed'),

    (loc+'singleMu/muon_SFs.root:data_id_eff', 'm_id_ic_data'),
    (loc+'singleMu/muon_SFs.root:ZLL_id_eff', 'm_id_ic_mc'),
    (loc+'singleMu/muon_SFs.root:embed_id_eff', 'm_id_ic_embed'),

    (loc+'MT/muon_SFs.root:data_trg_eff', 'm_trg_20_ic_data'),
    (loc+'MT/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_ic_mc'),
    (loc+'MT/muon_SFs.root:embed_trg_eff', 'm_trg_20_ic_embed'),
    # update aiso ones
    # (loc+'MT/aiso1/muon_SFs.root:data_trg_eff', 'm_trg_20_aiso1_ic_data'),
    # (loc+'MT/aiso1/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_aiso1_ic_mc'),
    # (loc+'MT/aiso1/muon_SFs.root:embed_trg_eff', 'm_trg_20_aiso1_ic_embed'),
    # (loc+'MT/aiso2/muon_SFs.root:data_trg_eff', 'm_trg_20_aiso2_ic_data'),
    # (loc+'MT/aiso2/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_aiso2_ic_mc'),
    # (loc+'MT/aiso2/muon_SFs.root:embed_trg_eff', 'm_trg_20_aiso2_ic_embed'),

    (loc+'EM_HI/muon_SFs.root:data_trg_eff', 'm_trg_23_ic_data'),
    (loc+'EM_HI/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_ic_mc'),
    (loc+'EM_HI/muon_SFs.root:embed_trg_eff', 'm_trg_23_ic_embed'),
    (loc+'EM_LO/muon_SFs.root:data_trg_eff', 'm_trg_8_ic_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_ic_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_trg_eff', 'm_trg_8_ic_embed'),
    (loc+'EM_LO/muon_SFs.root:data_iso_eff', 'm_looseiso_ic_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_ic_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_iso_eff', 'm_looseiso_ic_embed'),
    # update aiso ones
    # (loc+'EM_LO/aiso/muon_SFs.root:data_iso_eff', 'm_looseiso_aiso_ic_data'),
    # (loc+'EM_LO/aiso/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_aiso_ic_mc'),
    # (loc+'EM_LO/aiso/muon_SFs.root:embed_iso_eff', 'm_looseiso_aiso_ic_embed'),

    # update aiso ones
    # (loc+'EM_HI/aiso/muon_SFs.root:data_trg_eff', 'm_trg_23_aiso_ic_data'),
    # (loc+'EM_HI/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_aiso_ic_mc'),
    # (loc+'EM_HI/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_23_aiso_ic_embed'),
    # (loc+'EM_LO/aiso/muon_SFs.root:data_trg_eff', 'm_trg_8_aiso_ic_data'),
    # (loc+'EM_LO/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_aiso_ic_mc'),
    # (loc+'EM_LO/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_8_aiso_ic_embed'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_trg_23_binned_ic_data', ['m_trg_23_ic_data', 'm_trg_23_aiso_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_trg_23_binned_ic_mc', ['m_trg_23_ic_mc', 'm_trg_23_aiso_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_trg_23_binned_ic_embed', ['m_trg_23_ic_embed', 'm_trg_23_aiso_ic_embed'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_trg_8_binned_ic_data', ['m_trg_8_ic_data', 'm_trg_8_aiso_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_trg_8_binned_ic_mc', ['m_trg_8_ic_mc', 'm_trg_8_aiso_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_trg_8_binned_ic_embed', ['m_trg_8_ic_embed', 'm_trg_8_aiso_ic_embed'])
#
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_looseiso_binned_ic_data', ['m_looseiso_ic_data', 'm_looseiso_aiso_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_looseiso_binned_ic_mc', ['m_looseiso_ic_mc', 'm_looseiso_aiso_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
#                                   'm_looseiso_binned_ic_embed', ['m_looseiso_ic_embed', 'm_looseiso_aiso_ic_embed'])
#
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_trg_binned_ic_data', ['m_trg_ic_data', 'm_trg_aiso1_ic_data', 'm_trg_aiso2_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_trg_binned_ic_mc', ['m_trg_ic_mc', 'm_trg_aiso1_ic_mc', 'm_trg_aiso2_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_trg_binned_ic_embed', ['m_trg_ic_embed', 'm_trg_aiso1_ic_embed', 'm_trg_aiso2_ic_embed'])
#
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_trg_20_binned_ic_data', ['m_trg_20_ic_data', 'm_trg_20_aiso1_ic_data', 'm_trg_20_aiso2_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_trg_20_binned_ic_mc', ['m_trg_20_ic_mc', 'm_trg_20_aiso1_ic_mc', 'm_trg_20_aiso2_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_trg_20_binned_ic_embed', ['m_trg_20_ic_embed', 'm_trg_20_aiso1_ic_embed', 'm_trg_20_aiso2_ic_embed'])
#
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_iso_binned_ic_data', ['m_iso_ic_data', 'm_iso_aiso1_ic_data', 'm_iso_aiso2_ic_data'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_iso_binned_ic_mc', ['m_iso_ic_mc', 'm_iso_aiso1_ic_mc', 'm_iso_aiso2_ic_mc'])
#wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
#                                   'm_iso_binned_ic_embed', ['m_iso_ic_embed', 'm_iso_aiso1_ic_embed', 'm_iso_aiso2_ic_embed'])

# temporarily take isolated SFs for all until anti iso ones are included
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_23_binned_ic_data', ['m_trg_23_ic_data', 'm_trg_23_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_23_binned_ic_mc', ['m_trg_23_ic_mc', 'm_trg_23_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_23_binned_ic_embed', ['m_trg_23_ic_embed', 'm_trg_23_ic_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_8_binned_ic_data', ['m_trg_8_ic_data', 'm_trg_8_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_8_binned_ic_mc', ['m_trg_8_ic_mc', 'm_trg_8_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_8_binned_ic_embed', ['m_trg_8_ic_embed', 'm_trg_8_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_ic_data', ['m_looseiso_ic_data', 'm_looseiso_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_ic_mc', ['m_looseiso_ic_mc', 'm_looseiso_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_ic_embed', ['m_looseiso_ic_embed', 'm_looseiso_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_ic_data', ['m_trg_ic_data', 'm_trg_ic_data', 'm_trg_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_ic_mc', ['m_trg_ic_mc', 'm_trg_ic_mc', 'm_trg_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_ic_embed', ['m_trg_ic_embed', 'm_trg_ic_embed', 'm_trg_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_20_binned_ic_data', ['m_trg_20_ic_data', 'm_trg_20_ic_data', 'm_trg_20_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_20_binned_ic_mc', ['m_trg_20_ic_mc', 'm_trg_20_ic_mc', 'm_trg_20_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_20_binned_ic_embed', ['m_trg_20_ic_embed', 'm_trg_20_ic_embed', 'm_trg_20_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_ic_data', ['m_iso_ic_data', 'm_iso_ic_data', 'm_iso_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_ic_mc', ['m_iso_ic_mc', 'm_iso_ic_mc', 'm_iso_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_ic_embed', ['m_iso_ic_embed', 'm_iso_ic_embed', 'm_iso_ic_embed'])

w.factory('expr::m_idiso_ic_data("@0*@1", m_iso_ic_data, m_id_ic_data)' % vars())
w.factory('expr::m_idiso_ic_mc("@0*@1", m_iso_ic_mc, m_id_ic_mc)' % vars())
w.factory('expr::m_idiso_ic_embed("@0*@1", m_iso_ic_embed, m_id_ic_embed)' % vars())
w.factory('expr::m_idlooseiso_ic_data("@0*@1", m_looseiso_ic_data, m_id_ic_data)' % vars())
w.factory('expr::m_idlooseiso_ic_mc("@0*@1", m_looseiso_ic_mc, m_id_ic_mc)' % vars())
w.factory('expr::m_idlooseiso_ic_embed("@0*@1", m_looseiso_ic_embed, m_id_ic_embed)' % vars())

w.factory('expr::m_idiso_binned_ic_data("@0*@1", m_iso_binned_ic_data, m_id_ic_data)' % vars())
w.factory('expr::m_idiso_binned_ic_mc("@0*@1", m_iso_binned_ic_mc, m_id_ic_mc)' % vars())
w.factory('expr::m_idiso_binned_ic_embed("@0*@1", m_iso_binned_ic_embed, m_id_ic_embed)' % vars())
w.factory('expr::m_idlooseiso_binned_ic_data("@0*@1", m_looseiso_binned_ic_data, m_id_ic_data)' % vars())
w.factory('expr::m_idlooseiso_binned_ic_mc("@0*@1", m_looseiso_binned_ic_mc, m_id_ic_mc)' % vars())
w.factory('expr::m_idlooseiso_binned_ic_embed("@0*@1", m_looseiso_binned_ic_embed, m_id_ic_embed)' % vars())

for i in ['trg', 'trg_20', 'trg_8', 'trg_23', 'id', 'iso', 'looseiso', 'idiso', 'idlooseiso']:
  w.factory('expr::m_%(i)s_ic_ratio("@0/@1", m_%(i)s_ic_data, m_%(i)s_ic_mc)' % vars())
  w.factory('expr::m_%(i)s_ic_embed_ratio("@0/@1", m_%(i)s_ic_data, m_%(i)s_ic_embed)' % vars())
  w.factory('expr::m_%(i)s_binned_ic_ratio("@0/@1", m_%(i)s_binned_ic_data, m_%(i)s_binned_ic_mc)' % vars())
  w.factory('expr::m_%(i)s_binned_ic_embed_ratio("@0/@1", m_%(i)s_binned_ic_data, m_%(i)s_binned_ic_embed)' % vars())

histsToWrap = [
    (loc+'MM_LO/muon_SFs.root:data_id_eff', 'm_sel_id_ic_1_data'),
    (loc+'MM_LO/muon_SFs.root:data_trg_eff', 'm_sel_trg_8_ic_1_data'),
    (loc+'MM_HI/muon_SFs.root:data_trg_eff', 'm_sel_trg_17_ic_1_data'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

histsToWrap = [
    (loc+'MM_LO/muon_SFs.root:data_id_eff', 'm_sel_id_ic_2_data'),
    (loc+'MM_LO/muon_SFs.root:data_trg_eff', 'm_sel_trg_8_ic_2_data'),
    (loc+'MM_HI/muon_SFs.root:data_trg_eff', 'm_sel_trg_17_ic_2_data'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

w.factory('expr::m_sel_trg_ic_data("0.9989*(@0*@3+@1*@2-@1*@3)", m_sel_trg_8_ic_1_data, m_sel_trg_17_ic_1_data, m_sel_trg_8_ic_2_data, m_sel_trg_17_ic_2_data)')
w.factory('expr::m_sel_trg_ic_ratio("min(1./@0,20)", m_sel_trg_ic_data)')

wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
                          GetFromTFile(loc+'MM_LO/muon_SFs.root:data_id_eff'), 'm_sel_id_ic_data')

w.factory('expr::m_sel_id_ic_ratio("min(1./@0,20)", m_sel_id_ic_data)')
############### WORK IN PROGRESS

# emu and e+tau trigger electron scale factors from IC

loc = 'inputs/2018/ICSF/'

histsToWrap = [
    (loc+'EM_LO/electron_SFs.root:data_trg_eff', 'e_trg_12_data'),
    (loc+'EM_LO/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_mc'),
    (loc+'EM_LO/electron_SFs.root:embed_trg_eff', 'e_trg_12_embed'),
    (loc+'EM_HI/electron_SFs.root:data_trg_eff', 'e_trg_23_data'),
    (loc+'EM_HI/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_mc'),
    (loc+'EM_HI/electron_SFs.root:embed_trg_eff', 'e_trg_23_embed'),

    (loc+'EM_LO/aiso/electron_SFs.root:data_trg_eff', 'e_trg_12_aiso_data'),
    (loc+'EM_LO/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_aiso_mc'),
    (loc+'EM_LO/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_12_aiso_embed'),
    (loc+'EM_HI/aiso/electron_SFs.root:data_trg_eff', 'e_trg_23_aiso_data'),
    (loc+'EM_HI/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_aiso_mc'),
    (loc+'EM_HI/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_23_aiso_embed'),

    (loc+'EL24/electron_SFs.root:data_trg_eff', 'e_trg_24_data'),
    (loc+'EL24/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_mc'),
    (loc+'EL24/electron_SFs.root:embed_trg_eff', 'e_trg_24_embed'),
    (loc+'EL24/aiso1/electron_SFs.root:data_trg_eff', 'e_trg_24_aiso1_data'),
    (loc+'EL24/aiso1/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_aiso1_mc'),
    (loc+'EL24/aiso1/electron_SFs.root:embed_trg_eff', 'e_trg_24_aiso1_embed'),
    (loc+'EL24/aiso2/electron_SFs.root:data_trg_eff', 'e_trg_24_aiso2_data'),
    (loc+'EL24/aiso2/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_aiso2_mc'),
    (loc+'EL24/aiso2/electron_SFs.root:embed_trg_eff', 'e_trg_24_aiso2_embed'),

]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.5],
                                   'e_trg_binned_23_data', ['e_trg_23_data', 'e_trg_23_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_23_mc', ['e_trg_23_mc', 'e_trg_23_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_23_embed', ['e_trg_23_embed', 'e_trg_23_aiso_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_12_data', ['e_trg_12_data', 'e_trg_12_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_12_mc', ['e_trg_12_mc', 'e_trg_12_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_12_embed', ['e_trg_12_embed', 'e_trg_12_aiso_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.5],
                                   'e_trg_binned_24_data', ['e_trg_24_data', 'e_trg_24_aiso1_data', 'e_trg_24_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.5],
                                   'e_trg_binned_24_mc', ['e_trg_24_mc', 'e_trg_24_aiso1_mc', 'e_trg_24_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.5],
                                   'e_trg_binned_24_embed', ['e_trg_24_embed', 'e_trg_24_aiso1_embed', 'e_trg_24_aiso2_embed'])

for t in ['trg','trg_binned']:
    w.factory('expr::e_%s_12_ratio("@0/@1", e_%s_12_data, e_%s_12_mc)' % (t, t, t))
    w.factory('expr::e_%s_23_ratio("@0/@1", e_%s_23_data, e_%s_23_mc)' % (t, t, t))
    w.factory('expr::e_%s_24_ratio("@0/@1", e_%s_24_data, e_%s_24_mc)' % (t, t, t))
    w.factory('expr::e_%s_12_embed_ratio("@0/@1", e_%s_12_data, e_%s_12_embed)' % (t, t, t))
    w.factory('expr::e_%s_23_embed_ratio("@0/@1", e_%s_23_data, e_%s_23_embed)' % (t, t, t))
    w.factory('expr::e_%s_24_embed_ratio("@0/@1", e_%s_24_data, e_%s_24_embed)' % (t, t, t))

# KIT tau trigger scale factors

loc = 'inputs/2018/KIT/TauTrigger/'
TauTriggerFile = ROOT.TFile(loc+"output_2018_tau_leg.root", "read")
for wp in ["vloose", "loose", "medium", "tight", "vtight", "vvtight"]:
    ## Tau Leg MuTau ##
    mt_tau_leg_kit_data = TauTriggerFile.Get("hist_mutauTriggerEfficiency_{}TauMVA_DATA".format(wp))
    mt_tau_leg_kit_embed = TauTriggerFile.Get("hist_mutauTriggerEfficiency_{}TauMVA_EMB".format(wp))
    mt_tau_leg_kit_mc = TauTriggerFile.Get("hist_mutauTriggerEfficiency_{}TauMVA_MC".format(wp))

    wsptools.SafeWrapHist(w,['t_pt'],mt_tau_leg_kit_data, name="mt_LooseChargedIsoPFTau27_{}_kit_data".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],mt_tau_leg_kit_mc, name="mt_LooseChargedIsoPFTau27_{}_kit_mc".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],mt_tau_leg_kit_embed, name="mt_LooseChargedIsoPFTau27_{}_kit_embed".format(wp))
    w.factory('expr::mt_LooseChargedIsoPFTau27_{}_kit_ratio("@0/@1", mt_LooseChargedIsoPFTau27_{}_kit_data, mt_LooseChargedIsoPFTau27_{}_kit_mc)'.format(wp,wp,wp))
    w.factory('expr::mt_emb_LooseChargedIsoPFTau27_{}_kit_ratio("@0/@1", mt_LooseChargedIsoPFTau27_{}_kit_data, mt_LooseChargedIsoPFTau27_{}_kit_embed)'.format(wp,wp,wp))

    ## Tau Leg MuTau ## Decay-Mode binned
    #~ mt_tau_leg_kit_dm_binned_data = TauTriggerFile.Get("mutau_{}_dm_DATA".format(wp))
    #~ mt_tau_leg_kit_dm_binned_embed = TauTriggerFile.Get("mutau_{}_dm_EMB".format(wp))
    #~ mt_tau_leg_kit_dm_binned_mc = TauTriggerFile.Get("mutau_{}_dm_MC".format(wp))

    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],mt_tau_leg_kit_dm_binned_data, name="mt_LooseChargedIsoPFTau27_{}_dm_binned_kit_data".format(wp))
    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],mt_tau_leg_kit_dm_binned_mc, name="mt_LooseChargedIsoPFTau27_{}_dm_binned_kit_mc".format(wp))
    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],mt_tau_leg_kit_dm_binned_embed, name="mt_LooseChargedIsoPFTau27_{}_dm_binned_kit_embed".format(wp))
    #~ w.factory('expr::mt_LooseChargedIsoPFTau27_{}_dm_binned_kit_ratio("@0/@1", mt_LooseChargedIsoPFTau27_{}_dm_binned_kit_data, mt_LooseChargedIsoPFTau27_{}_dm_binned_kit_mc)'.format(wp,wp,wp))
    #~ w.factory('expr::mt_emb_PFTau35OR40_{}_dm_binned_kit_ratio("@0/@1", mt_LooseChargedIsoPFTau27_{}_dm_binned_kit_data, mt_LooseChargedIsoPFTau27_{}_dm_binned_kit_embed)'.format(wp,wp,wp))

    ## Tau Leg ETau ##
    et_tau_leg_kit_data = TauTriggerFile.Get("hist_etauTriggerEfficiency_{}TauMVA_DATA".format(wp))
    et_tau_leg_kit_embed = TauTriggerFile.Get("hist_etauTriggerEfficiency_{}TauMVA_EMB".format(wp))
    et_tau_leg_kit_mc = TauTriggerFile.Get("hist_etauTriggerEfficiency_{}TauMVA_MC".format(wp))

    wsptools.SafeWrapHist(w,['t_pt'],et_tau_leg_kit_data, name="et_LooseChargedIsoPFTau30_{}_kit_data".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],et_tau_leg_kit_mc, name="et_LooseChargedIsoPFTau30_{}_kit_mc".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],et_tau_leg_kit_embed, name="et_LooseChargedIsoPFTau30_{}_kit_embed".format(wp))
    w.factory('expr::et_LooseChargedIsoPFTau30_{}_kit_ratio("@0/@1", et_LooseChargedIsoPFTau30_{}_kit_data, et_LooseChargedIsoPFTau30_{}_kit_mc)'.format(wp,wp,wp))
    w.factory('expr::et_emb_LooseChargedIsoPFTau30_{}_kit_ratio("@0/@1", et_LooseChargedIsoPFTau30_{}_kit_data, et_LooseChargedIsoPFTau30_{}_kit_embed)'.format(wp,wp,wp))

    ## Tau Leg ETau ## Decay-Mode binned
    #~ et_tau_leg_kit_dm_binned_data = TauTriggerFile.Get("etau_{}_dm_DATA".format(wp))
    #~ et_tau_leg_kit_dm_binned_embed = TauTriggerFile.Get("etau_{}_dm_EMB".format(wp))
    #~ et_tau_leg_kit_dm_binned_mc = TauTriggerFile.Get("etau_{}_dm_MC".format(wp))

    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],et_tau_leg_kit_dm_binned_data, name="et_LooseChargedIsoPFTau30_{}_dm_binned_kit_data".format(wp))
    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],et_tau_leg_kit_dm_binned_mc, name="et_LooseChargedIsoPFTau30_{}_dm_binned_kit_mc".format(wp))
    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],et_tau_leg_kit_dm_binned_embed, name="et_LooseChargedIsoPFTau30_{}_dm_binned_kit_embed".format(wp))
    #~ w.factory('expr::et_LooseChargedIsoPFTau30_{}_dm_binned_kit_ratio("@0/@1", et_LooseChargedIsoPFTau30_{}_dm_binned_kit_data, et_LooseChargedIsoPFTau30_{}_dm_binned_kit_mc)'.format(wp,wp,wp))
    w.factory('expr::et_LooseChargedIsoPFTau30_{}_dm_binned_kit_ratio("@0/@1", et_LooseChargedIsoPFTau30_{}_dm_binned_kit_data, et_LooseChargedIsoPFTau30_{}_dm_binned_kit_embed)'.format(wp,wp,wp))

    ## Tau Leg TauTau ##
    tt_tau_leg_kit_data = TauTriggerFile.Get("hist_ditauTriggerEfficiency_{}TauMVA_DATA".format(wp))
    tt_tau_leg_kit_embed = TauTriggerFile.Get("hist_ditauTriggerEfficiency_{}TauMVA_EMB".format(wp))
    tt_tau_leg_kit_mc = TauTriggerFile.Get("hist_ditauTriggerEfficiency_{}TauMVA_MC".format(wp))

    wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_data, name="tt_PFTau35OR40_{}_kit_data".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_mc, name="tt_PFTau35OR40_{}_kit_mc".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_embed, name="tt_PFTau35OR40_{}_kit_embed".format(wp))
    w.factory('expr::tt_PFTau35OR40_{}_kit_ratio("@0/@1", tt_PFTau35OR40_{}_kit_data, tt_PFTau35OR40_{}_kit_mc)'.format(wp,wp,wp))
    w.factory('expr::tt_emb_PFTau35OR40_{}_kit_ratio("@0/@1", tt_PFTau35OR40_{}_kit_data, tt_PFTau35OR40_{}_kit_embed)'.format(wp,wp,wp))

    ## Tau Leg TauTau ## Decay-Mode binned
    #~ tt_tau_leg_kit_dm_binned_data = TauTriggerFile.Get("ditau_{}_dm_DATA".format(wp))
    #~ tt_tau_leg_kit_dm_binned_embed = TauTriggerFile.Get("ditau_{}_dm_EMB".format(wp))
    #~ tt_tau_leg_kit_dm_binned_mc = TauTriggerFile.Get("ditau_{}_dm_MC".format(wp))

    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],tt_tau_leg_kit_dm_binned_data, name="tt_PFTau35OR40_{}_dm_binned_kit_data".format(wp))
    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],tt_tau_leg_kit_dm_binned_mc, name="tt_PFTau35OR40_{}_dm_binned_kit_mc".format(wp))
    #~ wsptools.SafeWrapHist(w,['t_pt','t_dm'],tt_tau_leg_kit_dm_binned_embed, name="tt_PFTau35OR40_{}_dm_binned_kit_embed".format(wp))
    #~ w.factory('expr::tt_PFTau35OR40_{}_dm_binned_kit_ratio("@0/@1", tt_PFTau35OR40_{}_dm_binned_kit_data, tt_PFTau35OR40_{}_dm_binned_kit_mc)'.format(wp,wp,wp))
    #~ w.factory('expr::tt_emb_PFTau35OR40_{}_dm_binned_kit_ratio("@0/@1", tt_PFTau35OR40_{}_dm_binned_kit_data, tt_PFTau35OR40_{}_dm_binned_kit_embed)'.format(wp,wp,wp))
TauTriggerFile.Close()

### Tau Trigger scale factors from Tau POG

loc = 'inputs/2018/TauPOGTriggerSFs/'
tau_trg_file = ROOT.TFile(loc+'tauTriggerEfficiencies2018.root')
w.factory('expr::t_pt_trig("min(max(@0,20),450)" ,t_pt[0])')
tau_id_wps=['vloose','loose','medium','tight','vtight']

for wp in tau_id_wps:
  for dm in ['0','1','10']:
    histsToWrap = [
      (loc+'tauTriggerEfficiencies2018.root:ditau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:ditau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:ditau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:ditau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:mutau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:mutau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:mutau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:mutau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:etau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:etau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:etau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:etau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_mc' % (wp,dm))
    ]
    for task in histsToWrap:  
      wsptools.SafeWrapHist(w, ['t_eta','t_phi'],
                            GetFromTFile(task[0]), name=task[1])

    for x in ['data', 'mc']:
      for y in ['ditau','mutau','etau']:
        func = tau_trg_file.Get("%s_%sMVAv2_dm%s_%s_fit" % (y,wp,dm,x.upper())) 
        params = func.GetParameters()
        w.factory('expr::t_trg_pt_%s_%s_dm%s_%s("%.12f - ROOT::Math::crystalball_cdf(-@0, %.12f, %.12f, %.12f, %.12f)*(%.12f)", t_pt_trig)' % (wp,y,dm,x, params[5],params[0],params[1],params[2],params[3],params[4]))
  
        w.factory('expr::t_trg_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_phieta_%s_%s_dm0_%s, t_trg_phieta_%s_%s_dm1_%s, t_trg_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
        w.factory('expr::t_trg_ave_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_ave_phieta_%s_%s_dm0_%s, t_trg_ave_phieta_%s_%s_dm1_%s, t_trg_ave_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
  
        w.factory('expr::t_trg_pt_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_pt_%s_%s_dm0_%s, t_trg_pt_%s_%s_dm1_%s, t_trg_pt_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x)) 

        w.factory('expr::t_trg_%s_%s_data("min(@0*@1/@2,1)", t_trg_pt_%s_%s_data, t_trg_phieta_%s_%s_data, t_trg_ave_phieta_%s_%s_data)' % (wp, y, wp, y, wp, y, wp, y))  
        w.factory('expr::t_trg_%s_%s_mc("min(@0*@1/@2,1)", t_trg_pt_%s_%s_mc, t_trg_phieta_%s_%s_mc, t_trg_ave_phieta_%s_%s_mc)' % (wp, y, wp, y, wp, y, wp, y))

        w.factory('expr::t_trg_%s_%s_ratio("@0/@1", t_trg_%s_%s_data, t_trg_%s_%s_mc)' % (wp, y, wp, y, wp, y))


# now use the histograms to get the uncertainty variations
for wp in tau_id_wps:
  for dm in ['0','1','10']:
     histsToWrap = [
      ('ditau_%sMVAv2_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_ditau_dm%s_data' % (wp,dm)),
      ('mutau_%sMVAv2_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_mutau_dm%s_data' % (wp,dm)),
      ('etau_%sMVAv2_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_etau_dm%s_data' % (wp,dm)),
      ('ditau_%sMVAv2_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_ditau_dm%s_mc' % (wp,dm)),
      ('mutau_%sMVAv2_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_mutau_dm%s_mc' % (wp,dm)),
      ('etau_%sMVAv2_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_etau_dm%s_mc' % (wp,dm))
    ]

     for task in histsToWrap:
       hist = tau_trg_file.Get(task[0])
       uncert_hists = wsptools.UncertsFromHist(hist) 
       wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[0], name=task[1]+'_up')
       wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[1], name=task[1]+'_down')

  for y in ['ditau','mutau','etau']:
    for x in ['data', 'mc']:
      w.factory('expr::t_trg_pt_uncert_%s_%s_%s_up("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_uncert_%s_%s_dm0_%s_up, t_trg_uncert_%s_%s_dm1_%s_up, t_trg_uncert_%s_%s_dm10_%s_up)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
      w.factory('expr::t_trg_pt_uncert_%s_%s_%s_down("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_uncert_%s_%s_dm0_%s_down, t_trg_uncert_%s_%s_dm1_%s_down, t_trg_uncert_%s_%s_dm10_%s_down)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

      w.factory('expr::t_trg_%s_%s_%s_up("(@0>0)*min((@0+@1)*@2/@0,1)", t_trg_pt_%s_%s_%s, t_trg_pt_uncert_%s_%s_%s_up, t_trg_%s_%s_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
      w.factory('expr::t_trg_%s_%s_%s_down("(@0>0)*max((@0-@1)*@2/@0,0)", t_trg_pt_%s_%s_%s, t_trg_pt_uncert_%s_%s_%s_down, t_trg_%s_%s_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

    w.factory('expr::t_trg_%s_%s_ratio_up("(@1>0)*(@3>0)*(sqrt(pow((@0-@1)/@1,2) + pow((@2-@3)/@3,2))+1.)*@4",t_trg_%s_%s_data_up, t_trg_%s_%s_data, t_trg_%s_%s_mc_up, t_trg_%s_%s_mc, t_trg_%s_%s_ratio)' % (wp, y, wp, y, wp, y, wp, y, wp, y, wp, y))

    w.factory('expr::t_trg_%s_%s_ratio_down("(@1>0)*(@3>0)*(1.-sqrt(pow((@1-@0)/@1,2) + pow((@3-@2)/@3,2)))*@4",t_trg_%s_%s_data_down, t_trg_%s_%s_data, t_trg_%s_%s_mc_down, t_trg_%s_%s_mc, t_trg_%s_%s_ratio)' % (wp, y, wp, y, wp, y, wp, y, wp, y, wp, y))

# deepTau ID SFs

loc = 'inputs/2018/TauPOGTriggerSFs/'
tau_trg_file = ROOT.TFile(loc+'2018_tauTriggerEff_DeepTau2017v2p1.root')
#tau_id_wps=['VVVLoose','VVLoose','VLoose','Loose','Medium','Tight']
tau_id_wps=['Medium']#,'Tight']

for wp in tau_id_wps:
  for dm in ['0','1','10',11]:

    histsToWrap = [
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:data_ditau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_ditau_dm%s_data' % (wp.lower(),dm)),
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:mc_ditau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_ditau_dm%s_mc' % (wp.lower(),dm)),
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:sf_ditau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_ditau_dm%s_ratio' % (wp.lower(),dm)),
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:data_mutau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_mutau_dm%s_data' % (wp.lower(),dm)),
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:mc_mutau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_mutau_dm%s_mc' % (wp.lower(),dm)),
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:sf_mutau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_mutau_dm%s_ratio' % (wp.lower(),dm)),
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:data_etau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_etau_dm%s_data' % (wp.lower(),dm)),
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:mc_etau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_etau_dm%s_mc' % (wp.lower(),dm)),
      (loc+'2018_tauTriggerEff_DeepTau2017v2p1.root:sf_etau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_etau_dm%s_ratio' % (wp.lower(),dm)),
    ]

    for task in histsToWrap:
        wsptools.SafeWrapHist(w, ['t_pt'],
                              GetFromTFile(task[0]), name=task[1])

        hist = GetFromTFile(task[0])
        uncert_hists = wsptools.UncertsFromHist(hist)
        wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[0], name=task[1]+'_up')
        wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[1], name=task[1]+'_down')

  wp_lower = wp.lower()
  for i in ['data','mc','ratio']:
    for j in ['ditau','mutau', 'etau']:
      w.factory('expr::t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s("(@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4", t_dm[0], t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm0_%(i)s, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm1_%(i)s, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm10_%(i)s, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm11_%(i)s)' % vars())

      w.factory('expr::t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s_up("@5 + ((@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4)", t_dm[0], t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm0_%(i)s_up, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm1_%(i)s_up, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm10_%(i)s_up, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm11_%(i)s_up, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s)' % vars())

      w.factory('expr::t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s_down("@5 - ((@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4)", t_dm[0], t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm0_%(i)s_down, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm1_%(i)s_down, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm10_%(i)s_down, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_dm11_%(i)s_down, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s)' % vars())

      for dm in ['0','1','10','11']:
        w.factory('expr::t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s_dm%(dm)s_down("(@0==%(dm)s)*@1 + (@0!=%(dm)s)*@2",t_dm[0], t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s_down, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s)' % vars())
        w.factory('expr::t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s_dm%(dm)s_up("(@0==%(dm)s)*@1 + (@0!=%(dm)s)*@2",t_dm[0], t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s_up, t_trg_pog_deeptau_%(wp_lower)s_%(j)s_%(i)s)' % vars())


## IC tau trigger SFs in bins of DM and MVA-DM

loc = 'inputs/IC_tau_trigger/'
tau_trg_file = ROOT.TFile(loc+'trigger_SF_tauh.root')
tau_id_wps=['medium']

for wp in tau_id_wps:
  for chan in ['mt','tt','et']:
    for dm in ['0','1','2','10',11]:
      if chan == 'et': chan_name = 'etau'
      if chan == 'mt': chan_name = 'mutau'
      if chan == 'tt': chan_name = 'ditau'

      if not dm=='2':
        histsToWrap = [
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_HPSDM_%(dm)s_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_HPSDM_%(dm)s_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_mc' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_HPSDM_%(dm)s_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_ratio' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_HPSDM_%(dm)s_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_embed_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_HPSDM_%(dm)s_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_embed' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_HPSDM_%(dm)s_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_embed_ratio' % vars()),
        ]
      
      if dm in ['1','2']:
        histsToWrap += [
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_mvaDM_%(dm)s_NoHPS0_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_mvaDM_%(dm)s_NoHPS0_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_mc' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_mvaDM_%(dm)s_NoHPS0_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_ratio' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_mvaDM_%(dm)s_NoHPS0_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_mvaDM_%(dm)s_NoHPS0_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_mvaDM_%(dm)s_NoHPS0_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed_ratio' % vars()),
        ]
      else:
        histsToWrap += [
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_mvaDM_%(dm)s_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_mvaDM_%(dm)s_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_mc' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingMCSamples_mvaDM_%(dm)s_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_ratio' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_mvaDM_%(dm)s_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_mvaDM_%(dm)s_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2018_PredUsingembedSamples_mvaDM_%(dm)s_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed_ratio' % vars()),
        ]
      
      for task in histsToWrap:
          wsptools.SafeWrapHist(w, ['t_pt'],
                                GetFromTFile(task[0]), name=task[1])

          hist = GetFromTFile(task[0])
          uncert_hists = wsptools.UncertsFromHist(hist)
          wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[0], name=task[1]+'_up')
          wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[1], name=task[1]+'_down')

  wp_lower = wp.lower()
  for i in ['data','mc','ratio','embed_data','embed','embed_ratio']:
    for j in ['ditau','mutau', 'etau']:
      w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s("(@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4", t_dm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm0_%(i)s, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm1_%(i)s, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm10_%(i)s, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm11_%(i)s)' % vars())

      w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s_up("@5 + ((@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4)", t_dm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm0_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm1_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm10_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm11_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s)' % vars())

      w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s_down("@5 - ((@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4)", t_dm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm0_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm1_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm10_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_dm11_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s)' % vars())

      for dm in ['0','1','10','11']:

        w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s_dm%(dm)s_down("(@0==%(dm)s)*@1 + (@0!=%(dm)s)*@2",t_dm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s)' % vars())
        w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s_dm%(dm)s_up("(@0==%(dm)s)*@1 + (@0!=%(dm)s)*@2",t_dm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_%(i)s)' % vars())

      # MVA-DM version ### doesnt work from here!!!
#t_trg_ic_deeptau_medium_ditau_mvadm_data

      w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_mvadm_%(j)s_%(i)s("(@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4 + (@0==2)*@5", t_mvadm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm0_%(i)s, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm1_%(i)s, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm10_%(i)s, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm11_%(i)s, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm2_%(i)s)' % vars())

      w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm_%(i)s_up("@6 + ((@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4) + (@0==2)*@5", t_mvadm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm0_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm1_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm10_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm11_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm2_%(i)s_up,t_trg_ic_deeptau_%(wp_lower)s_mvadm_%(j)s_%(i)s)' % vars())

      w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm_%(i)s_down("@6 - ((@0==0)*@1 + (@0==1)*@2 + (@0==10||@0==5)*@3 + (@0==11||@0==6)*@4 + (@0==2)*@5)", t_mvadm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm0_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm1_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm10_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm11_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm2_%(i)s_down,t_trg_ic_deeptau_%(wp_lower)s_mvadm_%(j)s_%(i)s)' % vars())

      for dm in ['0','1','2','10','11']:
        w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_mvadm_%(j)s_%(i)s_mvadm%(dm)s_down("(@0==%(dm)s)*@1 + (@0!=%(dm)s)*@2",t_mvadm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm_%(i)s_down, t_trg_ic_deeptau_%(wp_lower)s_mvadm_%(j)s_%(i)s)' % vars())
        w.factory('expr::t_trg_ic_deeptau_%(wp_lower)s_mvadm_%(j)s_%(i)s_mvadm%(dm)s_up("(@0==%(dm)s)*@1 + (@0!=%(dm)s)*@2",t_mvadm[0], t_trg_ic_deeptau_%(wp_lower)s_%(j)s_mvadm_%(i)s_up, t_trg_ic_deeptau_%(wp_lower)s_mvadm_%(j)s_%(i)s)' % vars()) 

# tau trigger SFs for embedded samples from KIT

loc = 'inputs/2018/KIT/TauTrigger/'
tau_trg_file = ROOT.TFile(loc+'tau_trigger_fits.root')
w.factory('expr::t_pt_trig("min(max(@0,20),450)" ,t_pt[0])')
tau_id_wps=['vloose','loose','medium','tight','vtight']

for wp in tau_id_wps:
  for dm in ['0','1','10']:
    histsToWrap = [
      (loc+'output_2018_tau_leg.root:ditau_%s_DM%s_DATA' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_embed_data' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:ditau_%s_DM%s_EMB' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_embed' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:ditau_%s_DM%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_embed_data' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:ditau_%s_DM%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_embed' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:mutau_%s_DM%s_DATA' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_embed_data' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:mutau_%s_DM%s_EMB' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_embed' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:mutau_%s_DM%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_embed_data' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:mutau_%s_DM%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_embed' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:etau_%s_DM%s_DATA' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_embed_data' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:etau_%s_DM%s_EMB' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_embed' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:etau_%s_DM%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_embed_data' % (wp,dm)),
      (loc+'output_2018_tau_leg.root:etau_%s_DM%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_embed' % (wp,dm)),
    ]
    for task in histsToWrap:
      wsptools.SafeWrapHist(w, ['t_eta','t_phi'],
                            GetFromTFile(task[0]), name=task[1])

    for x in ['embed_data', 'embed']:
      for y in ['ditau','mutau','etau']:
        func = tau_trg_file.Get("fit_%s_%s_dm%s_%s" % (y,wp,dm,x.replace('embed','EMB').upper()))
        if 'data' in x: func = tau_trg_file.Get("fit_%s_%s_dm%s_DATA" % (y,wp,dm))
        else:           func = tau_trg_file.Get("fit_%s_%s_dm%s_EMB" % (y,wp,dm))
        params = func.GetParameters()
        w.factory('expr::t_trg_pt_%s_%s_dm%s_%s("%.12f - ROOT::Math::crystalball_cdf(-@0, %.12f, %.12f, %.12f, %.12f)*(%.12f)", t_pt_trig)' % (wp,y,dm,x, params[5],params[0],params[1],params[2],params[3],params[4]))

        w.factory('expr::t_trg_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_phieta_%s_%s_dm0_%s, t_trg_phieta_%s_%s_dm1_%s, t_trg_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
        w.factory('expr::t_trg_ave_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_ave_phieta_%s_%s_dm0_%s, t_trg_ave_phieta_%s_%s_dm1_%s, t_trg_ave_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

        w.factory('expr::t_trg_pt_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_pt_%s_%s_dm0_%s, t_trg_pt_%s_%s_dm1_%s, t_trg_pt_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

        w.factory('expr::t_trg_%s_%s_embed_data("min(@0*@1/@2,1)", t_trg_pt_%s_%s_embed_data, t_trg_phieta_%s_%s_embed_data, t_trg_ave_phieta_%s_%s_embed_data)' % (wp, y, wp, y, wp, y, wp, y))
        w.factory('expr::t_trg_%s_%s_embed("min(@0*@1/@2,1)", t_trg_pt_%s_%s_embed, t_trg_phieta_%s_%s_embed, t_trg_ave_phieta_%s_%s_embed)' % (wp, y, wp, y, wp, y, wp, y))

        w.factory('expr::t_trg_%s_%s_embed_ratio("@0/@1", t_trg_%s_%s_embed_data, t_trg_%s_%s_embed)' % (wp, y, wp, y, wp, y))

### Tau Trigger scale factors from KIT - for using with deeptau IDs and for embedded samples

loc = 'inputs/2018/KIT/tau_trigger/'
tau_trg_file = ROOT.TFile(loc+'tauTriggerEfficiencies2018KIT_deeptau.root')
w.factory('expr::t_pt_trig("min(max(@0,20),450)" ,t_pt[0])')
tau_id_wps=['vlooseDeepTau','looseDeepTau','mediumDeepTau','tightDeepTau','vtightDeepTau','vvtightDeepTau']

for wp in tau_id_wps:
  for dm in ['0','1','10', '11']:
    histsToWrap = [
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:ditau_%s_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:ditau_%s_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:ditau_%s_dm%s_EMB' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:ditau_%s_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:ditau_%s_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:ditau_%s_dm%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:mutau_%s_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:mutau_%s_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:mutau_%s_dm%s_EMB' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:mutau_%s_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:mutau_%s_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:mutau_%s_dm%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:etau_%s_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:etau_%s_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:etau_%s_dm%s_EMB' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:etau_%s_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:etau_%s_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018KIT_deeptau.root:etau_%s_dm%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_embed' % (wp,dm))
    ]
    for task in histsToWrap:
      wsptools.SafeWrapHist(w, ['t_eta','t_phi'],
                            GetFromTFile(task[0]), name=task[1])

    for y in ['ditau','mutau','etau']:
      for x in ['data', 'mc', 'embed']:
        if not x is 'embed': func = tau_trg_file.Get("%s_%s_dm%s_%s_fit" % (y,wp,dm,x.upper()))
        else: func = tau_trg_file.Get("%s_%s_dm%s_EMB_fit" % (y,wp,dm))
        params = func.GetParameters()
        w.factory('expr::t_trg_pt_%s_%s_dm%s_%s("%.12f - ROOT::Math::crystalball_cdf(-@0, %.12f, %.12f, %.12f, %.12f)*(%.12f)", t_pt_trig)' % (wp,y,dm,x, params[5],params[0],params[1],params[2],params[3],params[4]))

        w.factory('expr::t_trg_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_phieta_%s_%s_dm0_%s, t_trg_phieta_%s_%s_dm1_%s, t_trg_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
        w.factory('expr::t_trg_ave_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_ave_phieta_%s_%s_dm0_%s, t_trg_ave_phieta_%s_%s_dm1_%s, t_trg_ave_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

        w.factory('expr::t_trg_pt_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_pt_%s_%s_dm0_%s, t_trg_pt_%s_%s_dm1_%s, t_trg_pt_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

        w.factory('expr::t_trg_%s_%s_%s("min(@0*@1/@2,1)", t_trg_pt_%s_%s_%s, t_trg_phieta_%s_%s_%s, t_trg_ave_phieta_%s_%s_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

      w.factory('expr::t_trg_%s_%s_ratio("@0/@1", t_trg_%s_%s_data, t_trg_%s_%s_mc)' % (wp, y, wp, y, wp, y))
      w.factory('expr::t_trg_%s_%s_embed_ratio("@0/@1", t_trg_%s_%s_data, t_trg_%s_%s_embed)' % (wp, y, wp, y, wp, y))

# now use the histograms to get the uncertainty variations
for wp in tau_id_wps:
  for dm in ['0','1','10','11']:
     histsToWrap = [
      ('ditau_%s_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_ditau_dm%s_data' % (wp,dm)),
      ('mutau_%s_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_mutau_dm%s_data' % (wp,dm)),
      ('etau_%s_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_etau_dm%s_data' % (wp,dm)),
      ('ditau_%s_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_ditau_dm%s_mc' % (wp,dm)),
      ('mutau_%s_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_mutau_dm%s_mc' % (wp,dm)),
      ('etau_%s_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_etau_dm%s_mc' % (wp,dm)),
      ('ditau_%s_dm%s_EMB_errorBand' % (wp,dm), 't_trg_uncert_%s_ditau_dm%s_embed' % (wp,dm)),
      ('mutau_%s_dm%s_EMB_errorBand' % (wp,dm), 't_trg_uncert_%s_mutau_dm%s_embed' % (wp,dm)),
      ('etau_%s_dm%s_EMB_errorBand' % (wp,dm), 't_trg_uncert_%s_etau_dm%s_embed' % (wp,dm))
    ]

     for task in histsToWrap:
       hist = tau_trg_file.Get(task[0])
       uncert_hists = wsptools.UncertsFromHist(hist)
       wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[0], name=task[1]+'_up')
       wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[1], name=task[1]+'_down')

  for y in ['ditau','mutau','etau']:
    for x in ['data', 'mc','embed']:
      w.factory('expr::t_trg_pt_uncert_%s_%s_%s_up("(@0==0)*@1 + (@0==1)*@2 + (@0>=3&&@0<11)*@3 + (@0==11)*@4", t_dm[0], t_trg_uncert_%s_%s_dm0_%s_up, t_trg_uncert_%s_%s_dm1_%s_up, t_trg_uncert_%s_%s_dm10_%s_up, t_trg_uncert_%s_%s_dm11_%s_up)'    % (wp, y, x, wp, y, x, wp, y, x, wp, y, x, wp, y, x))
      w.factory('expr::t_trg_pt_uncert_%s_%s_%s_down("(@0==0)*@1 + (@0==1)*@2 + (@0>=3&&@0<11)*@3 + (@0==11)*@4", t_dm[0], t_trg_uncert_%s_%s_dm0_%s_down, t_trg_uncert_%s_%s_dm1_%s_down, t_trg_uncert_%s_%s_dm10_%s_down, t_trg_uncert_%s_%s_dm11_%s_down)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x, wp, y, x))

      w.factory('expr::t_trg_%s_%s_%s_up("(@0>0)*min((@0+@1)*@2/@0,1)", t_trg_pt_%s_%s_%s, t_trg_pt_uncert_%s_%s_%s_up, t_trg_%s_%s_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
      w.factory('expr::t_trg_%s_%s_%s_down("(@0>0)*max((@0-@1)*@2/@0,0)", t_trg_pt_%s_%s_%s, t_trg_pt_uncert_%s_%s_%s_down, t_trg_%s_%s_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

    w.factory('expr::t_trg_%s_%s_ratio_up("(@1>0)*(@3>0)*(sqrt(pow((@0-@1)/@1,2) + pow((@2-@3)/@3,2))+1.)*@4",t_trg_%s_%s_data_up, t_trg_%s_%s_data, t_trg_%s_%s_mc_up, t_trg_%s_%s_mc, t_trg_%s_%s_ratio)' % (wp, y, wp, y, wp, y, wp, y, wp, y, wp, y))

    w.factory('expr::t_trg_%s_%s_ratio_down("(@1>0)*(@3>0)*(1.-sqrt(pow((@1-@0)/@1,2) + pow((@3-@2)/@3,2)))*@4",t_trg_%s_%s_data_down, t_trg_%s_%s_data, t_trg_%s_%s_mc_down, t_trg_%s_%s_mc, t_trg_%s_%s_ratio)' % (wp, y, wp, y, wp, y, wp, y, wp, y, wp, y))

    w.factory('expr::t_trg_%s_%s_embed_ratio_up("(@1>0)*(@3>0)*(sqrt(pow((@0-@1)/@1,2) + pow((@2-@3)/@3,2))+1.)*@4",t_trg_%s_%s_data_up, t_trg_%s_%s_data, t_trg_%s_%s_embed_up, t_trg_%s_%s_embed, t_trg_%s_%s_embed_ratio)' % (wp, y, wp, y, wp, y, wp, y, wp, y, wp, y))

    w.factory('expr::t_trg_%s_%s_embed_ratio_down("(@1>0)*(@3>0)*(1.-sqrt(pow((@1-@0)/@1,2) + pow((@3-@2)/@3,2)))*@4",t_trg_%s_%s_data_down, t_trg_%s_%s_data, t_trg_%s_%s_embed_down, t_trg_%s_%s_embed, t_trg_%s_%s_embed_ratio)' % (wp, y, wp, y, wp, y, wp, y, wp, y, wp, y))

    for x in ['ratio','embed_ratio','embed','data','mc']:
      w.factory('expr::t_trg_%(wp)s_%(y)s_%(x)s_dm0_up("(@0==0)*@1 + (@0!=0)*@2 ", t_dm[0], t_trg_%(wp)s_%(y)s_%(x)s_up, t_trg_%(wp)s_%(y)s_%(x)s)' % vars())
      w.factory('expr::t_trg_%(wp)s_%(y)s_%(x)s_dm0_down("(@0==0)*@1 + (@0!=0)*@2 ", t_dm[0], t_trg_%(wp)s_%(y)s_%(x)s_down, t_trg_%(wp)s_%(y)s_%(x)s)' % vars())
      w.factory('expr::t_trg_%(wp)s_%(y)s_%(x)s_dm1_up("(@0==1)*@1 + (@0!=1)*@2 ", t_dm[0], t_trg_%(wp)s_%(y)s_%(x)s_up, t_trg_%(wp)s_%(y)s_%(x)s)' % vars())
      w.factory('expr::t_trg_%(wp)s_%(y)s_%(x)s_dm1_down("(@0==1)*@1 + (@0!=1)*@2 ", t_dm[0], t_trg_%(wp)s_%(y)s_%(x)s_down, t_trg_%(wp)s_%(y)s_%(x)s)' % vars())
      w.factory('expr::t_trg_%(wp)s_%(y)s_%(x)s_dm10_up("(@0==10)*@1 + (@0!=10)*@2 ", t_dm[0], t_trg_%(wp)s_%(y)s_%(x)s_up, t_trg_%(wp)s_%(y)s_%(x)s)' % vars())
      w.factory('expr::t_trg_%(wp)s_%(y)s_%(x)s_dm10_down("(@0==10)*@1 + (@0!=10)*@2 ", t_dm[0], t_trg_%(wp)s_%(y)s_%(x)s_down, t_trg_%(wp)s_%(y)s_%(x)s)' % vars())
      w.factory('expr::t_trg_%(wp)s_%(y)s_%(x)s_dm11_up("(@0==11)*@1 + (@0!=11)*@2 ", t_dm[0], t_trg_%(wp)s_%(y)s_%(x)s_up, t_trg_%(wp)s_%(y)s_%(x)s)' % vars())
      w.factory('expr::t_trg_%(wp)s_%(y)s_%(x)s_dm11_down("(@0==11)*@1 + (@0!=11)*@2 ", t_dm[0], t_trg_%(wp)s_%(y)s_%(x)s_down, t_trg_%(wp)s_%(y)s_%(x)s)' % vars())

# differential tau ID SFs from tau POG

# dm binned SFs

loc='inputs/2018/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:VLoose', 't_id_dm_vloose'), 
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:Loose',  't_id_dm_loose'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:Medium', 't_id_dm_medium'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:Tight',  't_id_dm_tight'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:VTight', 't_id_dm_vtight'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:VVTight', 't_id_dm_vvtight')
]

w.factory('expr::t_dm_bounded("(@0<2)*@0 + (@0>2)*10" ,t_dm[0])')

for task in histsToWrap: 
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], GetFromTFile(task[0]), name=task[1])
  uncert_hists = wsptools.UncertsFromHist(GetFromTFile(task[0]))
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], uncert_hists[0], name=task[1]+'_abs_up')
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], uncert_hists[1], name=task[1]+'_abs_down')
  w.factory('expr::%s_up("@1+@0",%s_abs_up,%s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_down("@1-@0",%s_abs_down,%s)' % (task[1],task[1],task[1]))

# pT dependent SFs

sf_funcs = {}

sf_funcs['vloose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9662711+ ( x > 25 && x <=30)*0.9841571+ ( x > 30 && x <=35)*0.8992864+ ( x > 35 && x <=40)*0.8736828+ (x > 40)*0.977607152447'
sf_funcs['vloose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0660781+ ( x > 25 && x <=30)*1.0602211+ ( x > 30 && x <=35)*0.9593934+ ( x > 35 && x <=40)*0.9217598+ (x > 40 && x <=500)*1.01133836263+ (x > 500 && x <= 1000)*(0.977607152447 + 0.0337312101811*(x/500.))+ (x > 1000)*(0.977607152447 + 0.0674624203623)'
sf_funcs['vloose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8664641+ ( x > 25 && x <=30)*0.9080931+ ( x > 30 && x <=35)*0.8391794+ ( x > 35 && x <=40)*0.8256058+ (x > 40 && x <=500)*0.915656669816+ (x > 500 && x <= 1000)*(0.977607152447 - 0.0619504826307*(x/500.))+ (x > 1000)*(0.977607152447 - 0.123900965261)'
sf_funcs['loose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9724238+ ( x > 25 && x <=30)*0.9414591+ ( x > 30 && x <=35)*0.903099+ ( x > 35 && x <=40)*0.8897563+ (x >40)*0.961412176205'
sf_funcs['loose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0508898+ ( x > 25 && x <=30)*0.9908071+ ( x > 30 && x <=35)*0.945873+ ( x > 35 && x <=40)*0.9242753+ (x > 40 && x <=500)*0.993036992306+ (x > 500 && x <= 1000)*(0.961412176205 + 0.0316248161005*(x/500.))+ (x > 1000)*(0.961412176205 + 0.0632496322009)'
sf_funcs['loose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8939578+ ( x > 25 && x <=30)*0.8921111+ ( x > 30 && x <=35)*0.860325+ ( x > 35 && x <=40)*0.8552373+ (x > 40 && x <=500)*0.913623368498+ (x > 500 && x <= 1000)*(0.961412176205 - 0.0477888077072*(x/500.))+ (x > 1000)*(0.961412176205 - 0.0955776154145)'
sf_funcs['medium'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9899992+ ( x > 25 && x <=30)*0.9200476+ ( x > 30 && x <=35)*0.9028496+ ( x > 35 && x <=40)*0.8714629+ (x >40)*0.976360249307'
sf_funcs['medium_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0547492+ ( x > 25 && x <=30)*0.9669146+ ( x > 30 && x <=35)*0.9358836+ ( x > 35 && x <=40)*0.9006419+ (x > 40 && x <=500)*1.00618490594+ (x > 500 && x <= 1000)*(0.976360249307 + 0.0298246566306*(x/500.))+ (x > 1000)*(0.976360249307 + 0.0596493132613)'
sf_funcs['medium_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9252492+ ( x > 25 && x <=30)*0.8731806+ ( x > 30 && x <=35)*0.8698156+ ( x > 35 && x <=40)*0.8422839+ (x > 40 && x <= 500)*0.916024740558+ (x > 500 && x <= 1000)*(0.976360249307 - 0.0603355087495*(x/500.))+ (x > 1000)*(0.976360249307 - 0.120671017499)'
sf_funcs['tight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8956998+ ( x > 25 && x <=30)*0.9134051+ ( x > 30 && x <=35)*0.906231+ ( x > 35 && x <=40)*0.8671195+ (x >40)*0.979299687738'
sf_funcs['tight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9573188+ ( x > 25 && x <=30)*0.9505101+ ( x > 30 && x <=35)*0.932251+ ( x > 35 && x <=40)*0.8922515+ (x > 40 && x <= 500)*1.01259447442+ (x > 500 && x <= 1000)*(0.979299687738 + 0.0332947866851*(x/500.))+ (x > 1000)*(0.979299687738 + 0.0665895733703)'
sf_funcs['tight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8340808+ ( x > 25 && x <=30)*0.8763001+ ( x > 30 && x <=35)*0.880211+ ( x > 35 && x <=40)*0.8419875+ (x > 40 && x <=500)*0.914072075099+ (x > 500 && x <= 1000)*(0.979299687738 - 0.0652276126396*(x/500.))+ (x > 1000)*(0.979299687738 - 0.130455225279)'
sf_funcs['vtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9564608+ ( x > 25 && x <=30)*0.8996362+ ( x > 30 && x <=35)*0.9040256+ ( x > 35 && x <=40)*0.8576584+ (x >40)*0.947281869975'
sf_funcs['VTight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0015008+ ( x > 25 && x <=30)*0.9295192+ ( x > 30 && x <=35)*0.9267386+ ( x > 35 && x <=40)*0.8813924+ (x > 40 && x <=500)*0.978743245481+ (x > 500 && x <= 1000)*(0.947281869975 + 0.0314613755062*(x/500.))+ (x > 1000)*(0.947281869975 + 0.0629227510125)'
sf_funcs['vtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9114208+ ( x > 25 && x <=30)*0.8697532+ ( x > 30 && x <=35)*0.8813126+ ( x > 35 && x <=40)*0.8339244+ (x > 40 && x <=500)*0.892528698913+ (x > 500 && x <= 1000)*(0.947281869975 - 0.054753171062*(x/500.))+ (x > 1000)*(0.947281869975 - 0.109506342124)'
sf_funcs['vvtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9238749+ ( x > 25 && x <=30)*0.8854644+ ( x > 30 && x <=35)*0.8998929+ ( x > 35 && x <=40)*0.9066453+ (x>40)*0.918508990609'
sf_funcs['vvtight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9696919+ ( x > 25 && x <=30)*0.9120364+ ( x > 30 && x <=35)*0.9227749+ ( x > 35 && x <=40)*0.9542053+ (x > 40 && x <=500)*0.951544127496+ (x > 500 && x <= 1000)*(0.918508990609 + 0.0330351368866*(x/500.))+ (x > 1000)*(0.918508990609 + 0.0660702737733)'
sf_funcs['vvtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8780579+ ( x > 25 && x <=30)*0.8588924+ ( x > 30 && x <=35)*0.8770109+ ( x > 35 && x <=40)*0.8590853+ (x > 40 && x <= 500)*0.884945512573+ (x > 500 && x <= 1000)*(0.918508990609 - 0.0335634780354*(x/500.))+ (x > 1000)*(0.918508990609 - 0.0671269560709)'

import re
for x in sf_funcs:
  func = re.sub('x','@0',sf_funcs[x])
  w.factory('expr::t_id_pt_%s("%s",t_pt[0])' % (x, func))

# PRELIMINARY differential tau ID SFs for deepTau ID from Yuta

# dm binned SFs

loc='inputs/2018/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco.root:VVVLoose', 't_deeptauid_dm_vvvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco.root:VVLoose',  't_deeptauid_dm_vvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco.root:VLoose',   't_deeptauid_dm_vloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco.root:Loose',    't_deeptauid_dm_loose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco.root:Medium',   't_deeptauid_dm_medium'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco.root:Tight',    't_deeptauid_dm_tight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco.root:VTight',   't_deeptauid_dm_vtight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco.root:VVTight',  't_deeptauid_dm_vvtight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco_EMB.root:VVVLoose', 't_deeptauid_dm_embed_vvvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco_EMB.root:VVLoose',  't_deeptauid_dm_embed_vvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco_EMB.root:VLoose',   't_deeptauid_dm_embed_vloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco_EMB.root:Loose',    't_deeptauid_dm_embed_loose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco_EMB.root:Medium',   't_deeptauid_dm_embed_medium'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco_EMB.root:Tight',    't_deeptauid_dm_embed_tight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco_EMB.root:VTight',   't_deeptauid_dm_embed_vtight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2018ReReco_EMB.root:VVTight',  't_deeptauid_dm_embed_vvtight')
]

for task in histsToWrap:
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], GetFromTFile(task[0]), name=task[1])
  uncert_hists = wsptools.UncertsFromHist(GetFromTFile(task[0]))
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], uncert_hists[0], name=task[1]+'_abs_up')
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], uncert_hists[1], name=task[1]+'_abs_down')
  w.factory('expr::%s_up("@1+@0",%s_abs_up,%s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_down("@1-@0",%s_abs_down,%s)' % (task[1],task[1],task[1]))

  w.factory('expr::%s_dm0_up("(@0==0)*@1 + (@0!=0)*@2 ", t_dm[0], %s_up, %s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_dm0_down("(@0==0)*@1 + (@0!=0)*@2 ", t_dm[0], %s_down, %s)' % (task[1],task[1],task[1]))

  w.factory('expr::%s_dm1_up("(@0==1)*@1 + (@0!=1)*@2 ", t_dm[0], %s_up, %s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_dm1_down("(@0==1)*@1 + (@0!=1)*@2 ", t_dm[0], %s_down, %s)' % (task[1],task[1],task[1]))

  w.factory('expr::%s_dm10_up("(@0==10)*@1 + (@0!=10)*@2 ", t_dm[0], %s_up, %s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_dm10_down("(@0==10)*@1 + (@0!=10)*@2 ", t_dm[0], %s_down, %s)' % (task[1],task[1],task[1]))

  w.factory('expr::%s_dm11_up("(@0==11)*@1 + (@0!=11)*@2 ", t_dm[0], %s_up, %s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_dm11_down("(@0==11)*@1 + (@0!=11)*@2 ", t_dm[0], %s_down, %s)' % (task[1],task[1],task[1]))


# pT dependent SFs

sf_funcs = {}

sf_funcs = {}
tauid_pt_file = ROOT.TFile(loc+'/TauID_SF_pt_DeepTau2017v2p1VSjet_2018ReReco.root')
for i in ['VVVLoose', 'VVLoose', 'VLoose', 'Loose', 'Medium', 'Tight', 'VTight', 'VVTight']:
  for j in ['cent', 'up', 'down']:
    fname = '%s_%s' % (i,j)
    fit = tauid_pt_file.Get(fname)
    outname = i.lower()
    if j != 'cent': outname+='_%s' % j
    sf_funcs[outname] = fit.GetTitle()


for x in sf_funcs:
  func = re.sub('x','@0',sf_funcs[x])
  w.factory('expr::t_deeptauid_pt_%s("%s",t_pt[0])' % (x, func))

for i in ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']:
  w.factory('expr::t_deeptauid_pt_%(i)s_bin1_up("(@0>20&&@0<=25)*@1 + ((@0>20&&@0<=25)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_up, t_deeptauid_pt_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_%(i)s_bin1_down("(@0>20&&@0<=25)*@1 + ((@0>20&&@0<=25)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_down, t_deeptauid_pt_%(i)s)' % vars())

  w.factory('expr::t_deeptauid_pt_%(i)s_bin2_up("(@0>25&&@0<=30)*@1 + ((@0>25&&@0<=30)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_up, t_deeptauid_pt_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_%(i)s_bin2_down("(@0>25&&@0<=30)*@1 + ((@0>25&&@0<=30)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_down, t_deeptauid_pt_%(i)s)' % vars())

  w.factory('expr::t_deeptauid_pt_%(i)s_bin3_up("(@0>30&&@0<=35)*@1 + ((@0>30&&@0<=35)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_up, t_deeptauid_pt_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_%(i)s_bin3_down("(@0>30&&@0<=35)*@1 + ((@0>30&&@0<=35)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_down, t_deeptauid_pt_%(i)s)' % vars())

  w.factory('expr::t_deeptauid_pt_%(i)s_bin4_up("(@0>35&&@0<=40)*@1 + ((@0>35&&@0<=40)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_up, t_deeptauid_pt_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_%(i)s_bin4_down("(@0>35&&@0<=40)*@1 + ((@0>35&&@0<=40)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_down, t_deeptauid_pt_%(i)s)' % vars())

  w.factory('expr::t_deeptauid_pt_%(i)s_bin5_up("(@0>40&&@0<=500)*@1 + ((@0>40&&@0<=500)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_up, t_deeptauid_pt_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_%(i)s_bin5_down("(@0>40&&@0<=500)*@1 + ((@0>40&&@0<=500)==0)*@2",t_pt[0], t_deeptauid_pt_%(i)s_down, t_deeptauid_pt_%(i)s)' % vars())

# embedded SFs

sf_funcs = {}

sf_funcs = {}
tauid_pt_file = ROOT.TFile(loc+'/TauID_SF_pt_DeepTau2017v2p1VSjet_2018ReReco_EMB.root')
for i in ['VVVLoose', 'VVLoose', 'VLoose', 'Loose', 'Medium', 'Tight', 'VTight', 'VVTight']:
  for j in ['cent', 'up', 'down']:
    fname = '%s_%s' % (i,j)
    fit = tauid_pt_file.Get(fname)
    outname = i.lower()
    if j != 'cent': outname+='_%s' % j
    sf_funcs[outname] = fit.GetTitle()


for x in sf_funcs:
  func = re.sub('x','@0',sf_funcs[x])
  w.factory('expr::t_deeptauid_pt_embed_%s("%s",t_pt[0])' % (x, func))

for i in ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']:
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin1_up("(@0>20&&@0<=25)*@1 + ((@0>20&&@0<=25)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_up, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin1_down("(@0>20&&@0<=25)*@1 + ((@0>20&&@0<=25)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_down, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin2_up("(@0>25&&@0<=30)*@1 + ((@0>25&&@0<=30)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_up, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin2_down("(@0>25&&@0<=30)*@1 + ((@0>25&&@0<=30)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_down, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin3_up("(@0>30&&@0<=35)*@1 + ((@0>30&&@0<=35)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_up, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin3_down("(@0>30&&@0<=35)*@1 + ((@0>30&&@0<=35)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_down, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin4_up("(@0>35&&@0<=40)*@1 + ((@0>35&&@0<=40)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_up, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin4_down("(@0>35&&@0<=40)*@1 + ((@0>35&&@0<=40)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_down, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin5_up("(@0>40&&@0<=500)*@1 + ((@0>40&&@0<=500)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_up, t_deeptauid_pt_embed_%(i)s)' % vars())
  w.factory('expr::t_deeptauid_pt_embed_%(i)s_bin5_down("(@0>40&&@0<=500)*@1 + ((@0>40&&@0<=500)==0)*@2",t_pt[0], t_deeptauid_pt_embed_%(i)s_down, t_deeptauid_pt_embed_%(i)s)' % vars())

# extra SFs for tight anti-electron ID
sf_funcs = {}
tauid_pt_file = ROOT.TFile(loc+'/TauID_SF_pt_DeepTau2017v2p1VSjet_2018ReReco_tight_antie_EMB.root')
for i in ['VVVLoose', 'VVLoose', 'VLoose', 'Loose', 'Medium', 'Tight', 'VTight', 'VVTight']:
  for j in ['cent', 'up', 'down']:
    fname = '%s_%s' % (i,j)
    fit = tauid_pt_file.Get(fname)
    outname = i.lower()
    if j != 'cent': outname+='_%s' % j
    sf_funcs[outname] = fit.GetTitle()


for x in sf_funcs:
  func = re.sub('x','@0',sf_funcs[x])
  w.factory('expr::t_deeptauid_pt_tightvse_embed_%s("%s",t_pt[0])' % (x, func))


histsToWrap = [
  ('inputs/2018/tauIDSF/result_TauIDSF_ttAndmt_MC_2018.root:h_MVA_lowpt', 't_deeptauid_mvadm_medium_lowpt'),
  ('inputs/2018/tauIDSF/result_TauIDSF_ttAndmt_MC_2018.root:h_MVA_highpt', 't_deeptauid_mvadm_medium_highpt'),
  ('inputs/2018/tauIDSF/result_TauIDSF_ttAndmt_embed_2018.root:h_MVA_lowpt', 't_deeptauid_mvadm_embed_medium_lowpt'),
  ('inputs/2018/tauIDSF/result_TauIDSF_ttAndmt_embed_2018.root:h_MVA_highpt', 't_deeptauid_mvadm_embed_medium_highpt'),
]

for task in histsToWrap:
  wsptools.SafeWrapHist(w, ['t_mvadm'], GetFromTFile(task[0]), name=task[1])
  uncert_hists = wsptools.UncertsFromHist(GetFromTFile(task[0]))
  wsptools.SafeWrapHist(w, ['t_mvadm'], uncert_hists[0], name=task[1]+'_abs_up')
  wsptools.SafeWrapHist(w, ['t_mvadm'], uncert_hists[1], name=task[1]+'_abs_down')
  w.factory('expr::%s_up("@1+@0",%s_abs_up,%s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_down("@1-@0",%s_abs_down,%s)' % (task[1],task[1],task[1]))


w.factory('expr::t_deeptauid_mvadm_medium("(@0<40)*(@1) + (@0>=40)*(@2)", t_pt, t_deeptauid_mvadm_medium_lowpt, t_deeptauid_mvadm_medium_highpt)' % vars()) 
w.factory('expr::t_deeptauid_mvadm_embed_medium("(@0<40)*(@1) + (@0>=40)*(@2)", t_pt, t_deeptauid_mvadm_embed_medium_lowpt, t_deeptauid_mvadm_embed_medium_highpt)' % vars()) 

w.factory('expr::t_deeptauid_mvadm_medium_up("(@0<40)*(@1) + (@0>=40)*(@2)", t_pt, t_deeptauid_mvadm_medium_lowpt_abs_up, t_deeptauid_mvadm_medium_highpt_abs_up)' % vars())   
w.factory('expr::t_deeptauid_mvadm_embed_medium_up("(@0<40)*(@1) + (@0>=40)*(@2)", t_pt, t_deeptauid_mvadm_embed_medium_lowpt_abs_up, t_deeptauid_mvadm_embed_medium_highpt_abs_up)' % vars()) 

w.factory('expr::t_deeptauid_mvadm_medium_down("(@0<40)*(@1) + (@0>=40)*(@2)", t_pt, t_deeptauid_mvadm_medium_lowpt_abs_down, t_deeptauid_mvadm_medium_highpt_abs_down)' % vars())
w.factory('expr::t_deeptauid_mvadm_embed_medium_down("(@0<40)*(@1) + (@0>=40)*(@2)", t_pt, t_deeptauid_mvadm_embed_medium_lowpt_abs_down, t_deeptauid_mvadm_embed_medium_highpt_abs_down)' % vars())


for i in ['','embed_']:

  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm0_up("(@3<40)*((@0==0)*(@2+@1) + (@0!=0)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm0_down("(@3<40)*((@0==0)*(@2-@1) + (@0!=0)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm1_up("(@3<40)*((@0==1)*(@2+@1) + (@0!=1)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm1_down("(@3<40)*((@0==1)*(@2-@1) + (@0!=1)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm2_up("(@3<40)*((@0==2)*(@2+@1) + (@0!=2)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm2_down("(@3<40)*((@0==2)*(@2-@1) + (@0!=2)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm10_up("(@3<40)*((@0==10)*(@2+@1) + (@0!=10)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm10_down("(@3<40)*((@0==10)*(@2-@1) + (@0!=10)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm11_up("(@3<40)*((@0==11)*(@2+@1) + (@0!=11)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_lowpt_mvadm11_down("(@3<40)*((@0==11)*(@2-@1) + (@0!=11)*@2 ) +(@3>=40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())

  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm0_up("(@3>=40)*((@0==0)*(@2+@1) + (@0!=0)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm0_down("(@3>=40)*((@0==0)*(@2-@1) + (@0!=0)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm1_up("(@3>=40)*((@0==1)*(@2+@1) + (@0!=1)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm1_down("(@3>=40)*((@0==1)*(@2-@1) + (@0!=1)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm2_up("(@3>=40)*((@0==2)*(@2+@1) + (@0!=2)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm2_down("(@3>=40)*((@0==2)*(@2-@1) + (@0!=2)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm10_up("(@3>=40)*((@0==10)*(@2+@1) + (@0!=10)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm10_down("(@3>=40)*((@0==10)*(@2-@1) + (@0!=10)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm11_up("(@3>=40)*((@0==11)*(@2+@1) + (@0!=11)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_up, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())
  w.factory('expr::t_deeptauid_mvadm_%(i)smedium_highpt_mvadm11_down("(@3>=40)*((@0==11)*(@2-@1) + (@0!=11)*@2 ) +(@3<40)*@2", t_mvadm[0], t_deeptauid_mvadm_%(i)smedium_down, t_deeptauid_mvadm_%(i)smedium, t_pt)' % vars())


# l->tau fake scale factors

loc='inputs/2018/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2018ReReco.root:VVLoose', 't_id_vs_e_eta_vvloose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2018ReReco.root:VLoose', 't_id_vs_e_eta_vloose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2018ReReco.root:Loose',  't_id_vs_e_eta_loose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2018ReReco.root:Medium', 't_id_vs_e_eta_medium'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2018ReReco.root:Tight',  't_id_vs_e_eta_tight'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2018ReReco.root:VTight', 't_id_vs_e_eta_vtight'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSmu_2018ReReco.root:VLoose', 't_id_vs_mu_eta_vloose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSmu_2018ReReco.root:Loose',  't_id_vs_mu_eta_loose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSmu_2018ReReco.root:Medium', 't_id_vs_mu_eta_medium'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSmu_2018ReReco.root:Tight',  't_id_vs_mu_eta_tight'),

]

w.factory('expr::t_eta_bounded("min(2.3,TMath::Abs(@0))" ,t_eta[0])')

for task in histsToWrap:
  wsptools.SafeWrapHist(w, ['t_eta_bounded'], GetFromTFile(task[0]), name=task[1])
  uncert_hists = wsptools.UncertsFromHist(GetFromTFile(task[0]))
  wsptools.SafeWrapHist(w, ['t_eta_bounded'], uncert_hists[0], name=task[1]+'_abs_up')
  wsptools.SafeWrapHist(w, ['t_eta_bounded'], uncert_hists[1], name=task[1]+'_abs_down')
  w.factory('expr::%s_up("@1+@0",%s_abs_up,%s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_down("@1-@0",%s_abs_down,%s)' % (task[1],task[1],task[1]))


# LO DYJetsToLL Z mass vs pT correction
histsToWrap = [
    ('inputs/2018/KIT/zpt_reweighting/zptm_weights_2018_kit.root:zptmass_histo', 'zptmass_weight_nom')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['z_gen_mass', 'z_gen_pt'],
                          GetFromTFile(task[0]), name=task[1])

# em channel OS/SS factors from UW    
loc = "inputs/2018/em_osss/"

em_osss_fits = ROOT.TFile(loc+'/osss_em_2018.root')

# get linear funtions vs dR for each njets bin
for njet in [0,1,2]:
  for x in ['','_unc1_up','_unc1_down','_unc2_up','_unc2_down']:
    func = em_osss_fits.Get('OSSS_qcd_%(njet)ijet_2018%(x)s' % vars()) 
    if njet > 0:
      par1 = func.GetParameter(0) - func.GetParameter(1)*2.5
    else:
      par1 = func.GetParameter(0) - func.GetParameter(1)*4.
    par2 = func.GetParameter(1)
    if njet !=2:
      w.factory('expr::em_qcd_osss_%(njet)ijet%(x)s("(@0==%(njet)i)*(%(par1)f+%(par2)f*@1)",njets[0],dR[0])' % vars())
    else: 
      w.factory('expr::em_qcd_osss_%(njet)ijet%(x)s("(@0>=%(njet)i)*(%(par1)f+%(par2)f*@1)",njets[0],dR[0])' % vars())
# get os and ss closure corrections

wsptools.SafeWrapHist(w, ['m_pt', 'e_pt'],
                      GetFromTFile(loc+'/closure_2018.root:correction'), 'em_qcd_osss_ss_corr')
wsptools.SafeWrapHist(w, ['m_pt', 'e_pt'],
                      GetFromTFile(loc+'/closure_2018.root:closureOS'), 'em_qcd_osss_os_corr')

w.factory('expr::em_qcd_osss("(@0+@1+@2)*@3*@4",em_qcd_osss_0jet,em_qcd_osss_1jet,em_qcd_osss_2jet,em_qcd_osss_ss_corr,em_qcd_osss_os_corr)' % vars())

# add stat uncertainties as independent shifts
for x in ['_unc1_up','_unc1_down','_unc2_up','_unc2_down']:
  w.factory('expr::em_qcd_osss_stat_0jet%(x)s("(@0+@1+@2)*@3*@4",em_qcd_osss_0jet%(x)s,em_qcd_osss_1jet,em_qcd_osss_2jet,em_qcd_osss_ss_corr,em_qcd_osss_os_corr)' % vars())
  w.factory('expr::em_qcd_osss_stat_1jet%(x)s("(@0+@1+@2)*@3*@4",em_qcd_osss_0jet,em_qcd_osss_1jet%(x)s,em_qcd_osss_2jet,em_qcd_osss_ss_corr,em_qcd_osss_os_corr)' % vars())
  w.factory('expr::em_qcd_osss_stat_2jet%(x)s("(@0+@1+@2)*@3*@4",em_qcd_osss_0jet,em_qcd_osss_1jet,em_qcd_osss_2jet%(x)s,em_qcd_osss_ss_corr,em_qcd_osss_os_corr)' % vars())

# add iso extrapolation uncertainty
w.factory('expr::em_qcd_osss_extrap_up("@0*@1",em_qcd_osss,em_qcd_osss_os_corr)')
w.factory('expr::em_qcd_osss_extrap_down("@0/@1",em_qcd_osss,em_qcd_osss_os_corr)')

w.importClassCode('CrystalBallEfficiency')

w.Print()
w.writeToFile('output/htt_scalefactors_legacy_2018.root')
w.Delete()
