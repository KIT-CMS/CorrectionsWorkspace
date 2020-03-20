#!/usr/bin/env python
import ROOT
import imp
import json
from array import array
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

# EGamma tracking SFs from https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaRunIIRecommendations#Electron_Scale_Factors
loc = 'inputs/2016/EGammaPOG'

histsToWrap = [
    (loc+'/EGM2D_BtoH_low_RecoSF_Legacy2016.root:EGamma_EffData2D',
     'e_trk_ST20_data'),
    (loc+'/EGM2D_BtoH_low_RecoSF_Legacy2016.root:EGamma_EffMC2D',           
    'e_trk_ST20_mc'),
    (loc+'/EGM2D_BtoH_low_RecoSF_Legacy2016.root:EGamma_SF2D',
     'e_trk_ST20_ratio'),
    (loc+'/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root:EGamma_EffData2D',
     'e_trk_GT20_data'),
    (loc+'/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root:EGamma_EffMC2D',
     'e_trk_GT20_mc'),
    (loc+'/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root:EGamma_SF2D',
     'e_trk_GT20_ratio')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_eta', 'e_pt'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_pt', [10., 20., 500.],
                                   'e_trk_data', ['e_trk_ST20_data', 'e_trk_GT20_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_pt', [10., 20., 500.],
                                   'e_trk_mc', ['e_trk_ST20_mc', 'e_trk_GT20_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_pt', [10., 20., 500.],
                                   'e_trk_ratio', ['e_trk_ST20_ratio', 'e_trk_GT20_ratio'])

# for embedded we (IC) derived an additional correction based on the MC and embedding reco efficiency differences, these are applied on top of the usual data/MC SFs
# note this is not needed for muons as differences between embedding and MC are very small

wsptools.SafeWrapHist(w, ['e_eta','e_pt'], GetFromTFile('inputs/2016/ICSF/elec_trk/embed_electron_reco_efficiencies_2016.root:embed_sf'), name='e_trk_embed')
w.factory('expr::e_trk_embed_ratio("@0*@1",e_trk_ratio, e_trk_embed)')

### Muon tracking efficiency scale factor from the muon POG
loc = 'inputs/2016/MuonPOG'

muon_trk_eff_hist = wsptools.TGraphAsymmErrorsToTH1D(GetFromTFile(loc+'/Tracking_EfficienciesAndSF_BCDEFGH.root:ratio_eff_eta3_dr030e030_corr'))
wsptools.SafeWrapHist(w, ['m_eta'], muon_trk_eff_hist, name='m_trk_ratio')

# KIT electron/muon tag and probe results
# The trigger refers to OR(IsoMu22, IsoTkMu22, IsoMu22_eta2p1, IsoTkMu22_eta2p1)
loc = 'inputs/2016/KIT/legacy_16_v1'

histsToWrap = [
    (loc+'/muon_TP_Data_2016_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',
     'm_id_data'),
    (loc+'/muon_TP_DY_2016_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',              'm_id_mc'),
    (loc+'/muon_TP_Embedding_2016_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',
     'm_id_emb'),
    (loc+'/muon_TP_Data_2016_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',
     'm_iso_data'),
    (loc+'/muon_TP_DY_2016_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',
     'm_iso_mc'),
    (loc+'/muon_TP_Embedding_2016_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',
     'm_iso_emb'),
    (loc+'/muon_TP_Data_2016_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',
     'm_aiso1_data'),
    (loc+'/muon_TP_DY_2016_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',
     'm_aiso1_mc'),
    (loc+'/muon_TP_Embedding_2016_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',
     'm_aiso1_emb'),
    (loc+'/muon_TP_Data_2016_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',
     'm_aiso2_data'),
    (loc+'/muon_TP_DY_2016_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',
     'm_aiso2_mc'),
    (loc+'/muon_TP_Embedding_2016_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',
     'm_aiso2_emb'),
    (loc+'/muon_TP_Data_2016_Fits_Trg_pt_eta_bins.root:Trg_pt_eta_bins',
     'm_trg_data'),
    (loc+'/muon_TP_DY_2016_Fits_Trg_pt_eta_bins.root:Trg_pt_eta_bins',
     'm_trg_mc'),
    (loc+'/muon_TP_Embedding_2016_Fits_Trg_pt_eta_bins.root:Trg_pt_eta_bins',
     'm_trg_emb'),
    (loc+'/muon_TP_Data_2016_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',    'm_trg_aiso1_data'),
    (loc+'/muon_TP_DY_2016_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',    'm_trg_aiso1_mc'),
    (loc+'/muon_TP_Embedding_2016_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',    'm_trg_aiso1_emb'),
    (loc+'/muon_TP_Data_2016_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',    'm_trg_aiso2_data'),
    (loc+'/muon_TP_DY_2016_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',    'm_trg_aiso2_mc'),
    (loc+'/muon_TP_Embedding_2016_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',    'm_trg_aiso2_emb'),
    # muon lepton legs
    (loc+'/crossmuon_TP_Data_2016_Fits_Trg_Mu19Tau20_pt_eta_bins.root:Trg_Mu19Tau20_pt_eta_bins',      'm_trg_MuTau_Mu19Leg_kit_data'),
    (loc+'/crossmuon_TP_DY_2016_Fits_Trg_Mu19Tau20_pt_eta_bins.root:Trg_Mu19Tau20_pt_eta_bins',        'm_trg_MuTau_Mu19Leg_kit_mc'),
    (loc+'/crossmuon_TP_Embedding_2016_Fits_Trg_Mu19Tau20_pt_eta_bins.root:Trg_Mu19Tau20_pt_eta_bins',      'm_trg_MuTau_Mu19Leg_kit_embed'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])


wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_data', ['m_iso_data', 'm_aiso1_data', 'm_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_mc', ['m_iso_mc', 'm_aiso1_mc', 'm_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_emb', ['m_iso_emb', 'm_aiso1_emb', 'm_aiso2_emb'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_data', ['m_trg_data', 'm_trg_aiso1_data', 'm_trg_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_mc', ['m_trg_mc', 'm_trg_aiso1_mc', 'm_trg_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_emb', ['m_trg_emb', 'm_trg_aiso1_emb', 'm_trg_aiso2_emb'])


for t in ['id', 'iso', 'aiso1', 'aiso2', 'iso_binned', 'trg', 'trg_aiso1', 'trg_aiso2', 'trg_binned', 'trg_MuTau_Mu19Leg']:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))
    w.factory('expr::m_%s_ratio_emb("@0/@1", m_%s_data, m_%s_emb)' % (t, t, t))

for t in ['data', 'mc', 'emb', 'ratio', 'ratio_emb']:
    w.factory('expr::m_idiso_%s("@0*@1", m_id_%s, m_iso_%s)' % (t, t, t))

loc = 'inputs/2016/KIT/legacy_16_v1'

histsToWrap = [
    (loc+'/electron_TP_Data_2016_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',
     'e_id80_data'),
    (loc+'/electron_TP_DY_2016_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',
     'e_id80_mc'),
    (loc+'/electron_TP_Embedding_2016_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',
     'e_id80_emb'),
    (loc+'/electron_TP_Data_2016_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',
     'e_id90_data'),
    (loc+'/electron_TP_DY_2016_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',
     'e_id90_mc'),
    (loc+'/electron_TP_Embedding_2016_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',
     'e_id90_emb'),
    (loc+'/electron_TP_Data_2016_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',
     'e_id_data'),
    (loc+'/electron_TP_DY_2016_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',
     'e_id_mc'),
    (loc+'/electron_TP_Embedding_2016_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',
     'e_id_emb'),
    (loc+'/electron_TP_Data_2016_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',
     'e_iso_data'),
    (loc+'/electron_TP_DY_2016_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',
     'e_iso_mc'),
    (loc+'/electron_TP_Embedding_2016_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',
     'e_iso_emb'),
    (loc+'/electron_TP_Data_2016_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',
     'e_AIso_data'),
    (loc+'/electron_TP_DY_2016_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',
     'e_AIso_mc'),
    (loc+'/electron_TP_Embedding_2016_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',
     'e_AIso_emb'),
    (loc+'/electron_TP_Data_2016_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',
     'e_trg_data'),
    (loc+'/electron_TP_DY_2016_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',
     'e_trg_mc'),
    (loc+'/electron_TP_Embedding_2016_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',
     'e_trg_emb'),
    (loc+'/electron_TP_Data_2016_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta',
     'e_trg_AIso_data'),
    (loc+'/electron_TP_DY_2016_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta', 'e_trg_AIso_mc'),
    (loc+'/electron_TP_Embedding_2016_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta', 'e_trg_AIso_emb'),
     # electron lepton legs
    (loc+'/crosselectron_TP_Data_2016_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',      'e_trg_EleTau_Ele24Leg_kit_data'),
    (loc+'/crosselectron_TP_DY_2016_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',        'e_trg_EleTau_Ele24Leg_kit_mc'),
    (loc+'/crosselectron_TP_Embedding_2016_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',      'e_trg_EleTau_Ele24Leg_kit_embed'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])


wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_data', ['e_iso_data', 'e_AIso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_mc', ['e_iso_mc', 'e_AIso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_emb', ['e_iso_emb', 'e_AIso_emb'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_data', ['e_trg_data', 'e_trg_AIso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_mc', ['e_trg_mc', 'e_trg_AIso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_emb', ['e_trg_emb', 'e_trg_AIso_emb'])


for t in ['id', 'iso', 'AIso', 'iso_binned', 'trg', 'trg_AIso', 'trg_binned', 'trg_EleTau_Ele24Leg']:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))
    w.factory('expr::e_%s_ratio_emb("@0/@1", e_%s_data, e_%s_emb)' % (t, t, t))

for t in ['data', 'mc', 'emb', 'ratio', 'ratio_emb']:
    w.factory('expr::e_idiso_%s("@0*@1", e_id_%s, e_iso_%s)' % (t, t, t))

# addressing muon selection for embedding:
loc = 'inputs/2016/KIT'  # so far not remeasured for legacy
Sel_histsToWrap = [
    (loc+'/ZmmTP_Data_Fits_muon_Selection_EmbeddedID.root:muon_Selection_EmbeddedID',
     'm_sel_idEmb_data'),
    (loc+'/ZmmTP_Data_Fits_muon_Selection_VVLIso.root:muon_Selection_VVLIso',
     'm_sel_vvliso_data')
]
for task in Sel_histsToWrap:
    wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])
for t in ['sel_idEmb', 'sel_vvliso']:
    w.factory('expr::m_%s_ratio("(1.0)/@0", m_%s_data)' % (t, t))


# DESY electron/muon tag and probe results
# Muons
loc = 'inputs/2016/LeptonEfficiencies'

desyHistsToWrap = [
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IdIso.root',
     'MC',   'm_idiso_desy_mc'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IdIso.root',
     'Data', 'm_idiso_desy_data'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IsoMu22.root',
     'MC',   'm_trgIsoMu22_desy_mc'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IsoMu22.root',
     'Data', 'm_trgIsoMu22_desy_data'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IsoMu24.root',
     'MC',   'm_trgIsoMu24_desy_mc'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IsoMu24.root',
     'Data', 'm_trgIsoMu24_desy_data'),

    # old crosstrigger weights for now
    (loc+'/Muon/Run2016BtoH/Muon_Mu19leg_2016BtoH_eff.root',
     'MC', 'm_trgMu19leg_eta2p1_desy_mc'),
    (loc+'/Muon/Run2016BtoH/Muon_Mu19leg_2016BtoH_eff.root',
     'Data', 'm_trgMu19leg_eta2p1_desy_data'),
]

for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])
for t in ['idiso_desy', 'trgIsoMu22_desy', 'trgIsoMu24_desy', 'trgMu19leg_eta2p1_desy']:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))

# Electrons
desyHistsToWrap = [
    (loc+'/Electron/Run2016_legacy/Electron_Run2016_legacy_IdIso.root',
     'MC',   'e_idiso_desy_mc'),
    (loc+'/Electron/Run2016_legacy/Electron_Run2016_legacy_IdIso.root',
     'Data', 'e_idiso_desy_data'),
    (loc+'/Electron/Run2016_legacy/Electron_Run2016_legacy_Ele25.root',
     'MC',   'e_trgEle25_desy_mc'),
    (loc+'/Electron/Run2016_legacy/Electron_Run2016_legacy_Ele25.root',
     'Data', 'e_trgEle25_desy_data')
]
for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['idiso_desy', 'trgEle25_desy']:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))


loc_kit = "inputs/2016/KIT/embeddingselection/"

histsToWrap = [   
    (loc_kit+'embeddingselection_TP_Data_2016_Fits_Trg17_pt_eta_bins.root:Trg17_pt_eta_bins', 'm_sel_trg17_1_kit_data'),
    (loc_kit+'embeddingselection_TP_Data_2016_Fits_Trg8_pt_eta_bins.root:Trg8_pt_eta_bins', 'm_sel_trg8_1_kit_data'),

]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])
histsToWrap = [
    (loc_kit+'embeddingselection_TP_Data_2016_Fits_Trg17_pt_eta_bins.root:Trg17_pt_eta_bins', 'm_sel_trg17_2_kit_data'),
    (loc_kit+'embeddingselection_TP_Data_2016_Fits_Trg8_pt_eta_bins.root:Trg8_pt_eta_bins', 'm_sel_trg8_2_kit_data'),

]


for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

w.factory('expr::m_sel_trg_kit_data("(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_kit_data, m_sel_trg17_1_kit_data, m_sel_trg8_2_kit_data, m_sel_trg17_2_kit_data)')
w.factory('expr::m_sel_trg_kit_ratio("min(1./@0,2)", m_sel_trg_kit_data)')

# addressing muon selection for embedding:

Sel_histsToWrap = [
    (loc_kit+'embeddingselection_TP_Data_2016_Fits_EmbID_pt_eta_bins.root:EmbID_pt_eta_bins', 'm_sel_idemb_kit_data'),
    (loc_kit+'embeddingselection_TP_Data_2016_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins', 'm_sel_id_kit_data'),
]
for task in Sel_histsToWrap:
    wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])
for t in ['sel_id', "sel_idemb" ]:
    w.factory('expr::m_%s_kit_ratio("(1.0)/@0", m_%s_kit_data)' % (t, t))


# LO DYJetsToLL Z mass vs pT correction
histsToWrap = [
    ('inputs/2016/KIT/zpt_reweighting/zptm_weights_2016_kit.root:zptmass_histo', 'zptmass_weight_nom')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['z_gen_mass', 'z_gen_pt'],
                          GetFromTFile(task[0]), name=task[1])

##################
# IC electron and muon id, iso, and trigger SFs for MC and embedding
##################

loc = 'inputs/2016/ICSF/'

histsToWrap = [

    (loc+'singleElec/electron_SFs.root:data_trg_eff', 'e_trg_ic_data'),
    (loc+'singleElec/electron_SFs.root:ZLL_trg_eff', 'e_trg_ic_mc'),
    (loc+'singleElec/electron_SFs.root:embed_trg_eff', 'e_trg_ic_embed'),
    (loc+'singleElec/aiso1/electron_SFs.root:data_trg_eff', 'e_trg_aiso1_ic_data'),
    (loc+'singleElec/aiso1/electron_SFs.root:ZLL_trg_eff', 'e_trg_aiso1_ic_mc'),
    (loc+'singleElec/aiso1/electron_SFs.root:embed_trg_eff', 'e_trg_aiso1_ic_embed'),
    (loc+'singleElec/aiso2/electron_SFs.root:data_trg_eff', 'e_trg_aiso2_ic_data'),
    (loc+'singleElec/aiso2/electron_SFs.root:ZLL_trg_eff', 'e_trg_aiso2_ic_mc'),
    (loc+'singleElec/aiso2/electron_SFs.root:embed_trg_eff', 'e_trg_aiso2_ic_embed'),

    (loc+'singleElec/electron_SFs.root:data_iso_eff', 'e_iso_ic_data'),
    (loc+'singleElec/electron_SFs.root:ZLL_iso_eff', 'e_iso_ic_mc'),
    (loc+'singleElec/electron_SFs.root:embed_iso_eff', 'e_iso_ic_embed'),
    (loc+'singleElec/aiso1/electron_SFs.root:data_iso_eff', 'e_iso_aiso1_ic_data'),
    (loc+'singleElec/aiso1/electron_SFs.root:ZLL_iso_eff', 'e_iso_aiso1_ic_mc'),
    (loc+'singleElec/aiso1/electron_SFs.root:embed_iso_eff', 'e_iso_aiso1_ic_embed'),
    (loc+'singleElec/aiso2/electron_SFs.root:data_iso_eff', 'e_iso_aiso2_ic_data'),
    (loc+'singleElec/aiso2/electron_SFs.root:ZLL_iso_eff', 'e_iso_aiso2_ic_mc'),
    (loc+'singleElec/aiso2/electron_SFs.root:embed_iso_eff', 'e_iso_aiso2_ic_embed'),

    (loc+'EM_LO/electron_SFs.root:data_id_eff', 'e_id_ic_data'),
    (loc+'EM_LO/electron_SFs.root:ZLL_id_eff', 'e_id_ic_mc'),
    (loc+'EM_LO/electron_SFs.root:embed_id_eff', 'e_id_ic_embed'),

    (loc+'EM_HI/electron_SFs.root:data_trg_eff', 'e_trg_23_ic_data'),
    (loc+'EM_HI/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_ic_mc'),
    (loc+'EM_HI/electron_SFs.root:embed_trg_eff', 'e_trg_23_ic_embed'),
    (loc+'EM_LO/electron_SFs.root:data_trg_eff', 'e_trg_12_ic_data'),
    (loc+'EM_LO/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_ic_mc'),
    (loc+'EM_LO/electron_SFs.root:embed_trg_eff', 'e_trg_12_ic_embed'),

    (loc+'EM_HI/aiso/electron_SFs.root:data_trg_eff', 'e_trg_23_aiso_ic_data'),
    (loc+'EM_HI/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_aiso_ic_mc'),
    (loc+'EM_HI/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_23_aiso_ic_embed'),
    (loc+'EM_LO/aiso/electron_SFs.root:data_trg_eff', 'e_trg_12_aiso_ic_data'),
    (loc+'EM_LO/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_aiso_ic_mc'),
    (loc+'EM_LO/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_12_aiso_ic_embed'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])



wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_23_binned_ic_data', ['e_trg_23_ic_data', 'e_trg_23_aiso_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_23_binned_ic_mc', ['e_trg_23_ic_mc', 'e_trg_23_aiso_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_23_binned_ic_embed', ['e_trg_23_ic_embed', 'e_trg_23_aiso_ic_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_12_binned_ic_data', ['e_trg_12_ic_data', 'e_trg_12_aiso_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_12_binned_ic_mc', ['e_trg_12_ic_mc', 'e_trg_12_aiso_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_12_binned_ic_embed', ['e_trg_12_ic_embed', 'e_trg_12_aiso_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_binned_ic_data', ['e_trg_ic_data', 'e_trg_aiso1_ic_data', 'e_trg_aiso2_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_binned_ic_mc', ['e_trg_ic_mc', 'e_trg_aiso1_ic_mc', 'e_trg_aiso2_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_trg_binned_ic_embed', ['e_trg_ic_embed', 'e_trg_aiso1_ic_embed', 'e_trg_aiso2_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_iso_binned_ic_data', ['e_iso_ic_data', 'e_iso_aiso1_ic_data', 'e_iso_aiso2_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_iso_binned_ic_mc', ['e_iso_ic_mc', 'e_iso_aiso1_ic_mc', 'e_iso_aiso2_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.50],
                                   'e_iso_binned_ic_embed', ['e_iso_ic_embed', 'e_iso_aiso1_ic_embed', 'e_iso_aiso2_ic_embed'])



w.factory('expr::e_idiso_ic_data("@0*@1", e_iso_ic_data, e_id_ic_data)' % vars())
w.factory('expr::e_idiso_ic_mc("@0*@1", e_iso_ic_mc, e_id_ic_mc)' % vars())
w.factory('expr::e_idiso_ic_embed("@0*@1", e_iso_ic_embed, e_id_ic_embed)' % vars())

w.factory('expr::e_idiso_binned_ic_data("@0*@1", e_iso_binned_ic_data, e_id_ic_data)' % vars())
w.factory('expr::e_idiso_binned_ic_mc("@0*@1", e_iso_binned_ic_mc, e_id_ic_mc)' % vars())
w.factory('expr::e_idiso_binned_ic_embed("@0*@1", e_iso_binned_ic_embed, e_id_ic_embed)' % vars())

for i in ['trg', 'trg_12', 'trg_23', 'id', 'iso', 'idiso']:
  w.factory('expr::e_%(i)s_ic_ratio("@0/@1", e_%(i)s_ic_data, e_%(i)s_ic_mc)' % vars())
  w.factory('expr::e_%(i)s_ic_embed_ratio("@0/@1", e_%(i)s_ic_data, e_%(i)s_ic_embed)' % vars())
  w.factory('expr::e_%(i)s_binned_ic_ratio("@0/@1", e_%(i)s_binned_ic_data, e_%(i)s_binned_ic_mc)' % vars())
  w.factory('expr::e_%(i)s_binned_ic_embed_ratio("@0/@1", e_%(i)s_binned_ic_data, e_%(i)s_binned_ic_embed)' % vars())



##muon

loc = 'inputs/2016/ICSF/'

histsToWrap = [
    #single muon
    (loc+'singleMu/muon_SFs.root:data_trg_eff', 'm_trg_ic_data'),
    (loc+'singleMu/muon_SFs.root:ZLL_trg_eff', 'm_trg_ic_mc'),
    (loc+'singleMu/muon_SFs.root:embed_trg_eff', 'm_trg_ic_embed'),
    
    (loc+'singleMu/aiso1/muon_SFs.root:data_trg_eff', 'm_trg_aiso1_ic_data'),
    (loc+'singleMu/aiso1/muon_SFs.root:ZLL_trg_eff', 'm_trg_aiso1_ic_mc'),
    (loc+'singleMu/aiso1/muon_SFs.root:embed_trg_eff', 'm_trg_aiso1_ic_embed'),
    
    (loc+'singleMu/aiso2/muon_SFs.root:data_trg_eff', 'm_trg_aiso2_ic_data'),
    (loc+'singleMu/aiso2/muon_SFs.root:ZLL_trg_eff', 'm_trg_aiso2_ic_mc'),
    (loc+'singleMu/aiso2/muon_SFs.root:embed_trg_eff', 'm_trg_aiso2_ic_embed'),

    (loc+'singleMu/muon_SFs.root:data_iso_eff', 'm_iso_ic_data'),
    (loc+'singleMu/muon_SFs.root:ZLL_iso_eff', 'm_iso_ic_mc'),
    (loc+'singleMu/muon_SFs.root:embed_iso_eff', 'm_iso_ic_embed'),
    
    (loc+'singleMu/aiso1/muon_SFs.root:data_iso_eff', 'm_iso_aiso1_ic_data'),
    (loc+'singleMu/aiso1/muon_SFs.root:ZLL_iso_eff', 'm_iso_aiso1_ic_mc'),
    (loc+'singleMu/aiso1/muon_SFs.root:embed_iso_eff', 'm_iso_aiso1_ic_embed'),
    
    (loc+'singleMu/aiso2/muon_SFs.root:data_iso_eff', 'm_iso_aiso2_ic_data'),
    (loc+'singleMu/aiso2/muon_SFs.root:ZLL_iso_eff', 'm_iso_aiso2_ic_mc'),
    (loc+'singleMu/aiso2/muon_SFs.root:embed_iso_eff', 'm_iso_aiso2_ic_embed'),
    
    #mt
    (loc+'MT/muon_SFs.root:data_trg_eff', 'm_trg_19_ic_data'),
    (loc+'MT/muon_SFs.root:ZLL_trg_eff', 'm_trg_19_ic_mc'),
    (loc+'MT/muon_SFs.root:embed_trg_eff', 'm_trg_19_ic_embed'),
    
    (loc+'MT/aiso1/muon_SFs.root:data_trg_eff', 'm_trg_19_aiso1_ic_data'),
    (loc+'MT/aiso1/muon_SFs.root:ZLL_trg_eff', 'm_trg_19_aiso1_ic_mc'),
    (loc+'MT/aiso1/muon_SFs.root:embed_trg_eff', 'm_trg_19_aiso1_ic_embed'),
    
    (loc+'MT/aiso2/muon_SFs.root:data_trg_eff', 'm_trg_19_aiso2_ic_data'),
    (loc+'MT/aiso2/muon_SFs.root:ZLL_trg_eff', 'm_trg_19_aiso2_ic_mc'),
    (loc+'MT/aiso2/muon_SFs.root:embed_trg_eff', 'm_trg_19_aiso2_ic_embed'),
    
    #em high and low legs
    (loc+'EM_HI/muon_SFs.root:data_trg_eff', 'm_trg_23_ic_data'),
    (loc+'EM_HI/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_ic_mc'),
    (loc+'EM_HI/muon_SFs.root:embed_trg_eff', 'm_trg_23_ic_embed'),
    
    (loc+'EM_LO/muon_SFs.root:data_trg_eff', 'm_trg_8_ic_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_ic_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_trg_eff', 'm_trg_8_ic_embed'),
    
    (loc+'EM_LO/muon_SFs.root:data_iso_eff', 'm_looseiso_ic_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_ic_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_iso_eff', 'm_looseiso_ic_embed'),
    (loc+'EM_LO/aiso/muon_SFs.root:data_iso_eff', 'm_looseiso_aiso_ic_data'),
    (loc+'EM_LO/aiso/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_aiso_ic_mc'),
    (loc+'EM_LO/aiso/muon_SFs.root:embed_iso_eff', 'm_looseiso_aiso_ic_embed'),

    (loc+'EM_LO/muon_SFs.root:data_id_eff', 'm_id_ic_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_id_eff', 'm_id_ic_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_id_eff', 'm_id_ic_embed'),

    (loc+'EM_HI/aiso/muon_SFs.root:data_trg_eff', 'm_trg_23_aiso_ic_data'),
    (loc+'EM_HI/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_aiso_ic_mc'),
    (loc+'EM_HI/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_23_aiso_ic_embed'),
    
    (loc+'EM_LO/aiso/muon_SFs.root:data_trg_eff', 'm_trg_8_aiso_ic_data'),
    (loc+'EM_LO/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_aiso_ic_mc'),
    (loc+'EM_LO/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_8_aiso_ic_embed'),

    
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])


wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_23_binned_ic_data', ['m_trg_23_ic_data', 'm_trg_23_aiso_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_23_binned_ic_mc', ['m_trg_23_ic_mc', 'm_trg_23_aiso_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_23_binned_ic_embed', ['m_trg_23_ic_embed', 'm_trg_23_aiso_ic_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],

                                   'm_trg_8_binned_ic_data', ['m_trg_8_ic_data', 'm_trg_8_aiso_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_8_binned_ic_mc', ['m_trg_8_ic_mc', 'm_trg_8_aiso_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_8_binned_ic_embed', ['m_trg_8_ic_embed', 'm_trg_8_aiso_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_ic_data', ['m_looseiso_ic_data', 'm_looseiso_aiso_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_ic_mc', ['m_looseiso_ic_mc', 'm_looseiso_aiso_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_ic_embed', ['m_looseiso_ic_embed', 'm_looseiso_aiso_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_ic_data', ['m_trg_ic_data', 'm_trg_aiso1_ic_data', 'm_trg_aiso2_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_ic_mc', ['m_trg_ic_mc', 'm_trg_aiso1_ic_mc', 'm_trg_aiso2_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_ic_embed', ['m_trg_ic_embed', 'm_trg_aiso1_ic_embed', 'm_trg_aiso2_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_19_binned_ic_data', ['m_trg_19_ic_data', 'm_trg_19_aiso1_ic_data', 'm_trg_19_aiso2_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_19_binned_ic_mc', ['m_trg_19_ic_mc', 'm_trg_19_aiso1_ic_mc', 'm_trg_19_aiso2_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_19_binned_ic_embed', ['m_trg_19_ic_embed', 'm_trg_19_aiso1_ic_embed', 'm_trg_19_aiso2_ic_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_ic_data', ['m_iso_ic_data', 'm_iso_aiso1_ic_data', 'm_iso_aiso2_ic_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_ic_mc', ['m_iso_ic_mc', 'm_iso_aiso1_ic_mc', 'm_iso_aiso2_ic_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_ic_embed', ['m_iso_ic_embed', 'm_iso_aiso1_ic_embed', 'm_iso_aiso2_ic_embed'])


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

for i in ['trg', 'trg_19', 'trg_8', 'trg_23', 'id', 'iso', 'looseiso', 'idiso', 'idlooseiso']:
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

w.factory('expr::m_sel_trg_ic_data("0.9454*(@0*@3+@1*@2-@1*@3)", m_sel_trg_8_ic_1_data, m_sel_trg_17_ic_1_data, m_sel_trg_8_ic_2_data, m_sel_trg_17_ic_2_data)')
w.factory('expr::m_sel_trg_ic_ratio("min(1./@0,20)", m_sel_trg_ic_data)')

wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
                          GetFromTFile(loc+'MM_LO/muon_SFs.root:data_id_eff'), 'm_sel_id_ic_data')

w.factory('expr::m_sel_id_ic_ratio("min(1./@0,20)", m_sel_id_ic_data)')


### Tau Trigger scale factors from Tau POG

# MVA ID SFs

loc = 'inputs/2016/TauPOGTriggerSFs/'
tau_trg_file = ROOT.TFile(loc+'tauTriggerEfficiencies2016.root')
w.factory('expr::t_pt_trig("min(max(@0,20),450)" ,t_pt[0])')
tau_id_wps=['vloose','loose','medium','tight','vtight']

for wp in tau_id_wps:
  for dm in ['0','1','10']:
    histsToWrap = [
      (loc+'tauTriggerEfficiencies2016.root:ditau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:ditau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:ditau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:ditau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:mutau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:mutau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:mutau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:mutau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:etau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:etau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:etau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016.root:etau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_mc' % (wp,dm))
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

      w.factory('expr::t_trg_%s_%s_%s_up("min((@0+@1)*@2/@0,1)", t_trg_pt_%s_%s_%s, t_trg_pt_uncert_%s_%s_%s_up, t_trg_%s_%s_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
      w.factory('expr::t_trg_%s_%s_%s_down("max((@0-@1)*@2/@0,0)", t_trg_pt_%s_%s_%s, t_trg_pt_uncert_%s_%s_%s_down, t_trg_%s_%s_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

    w.factory('expr::t_trg_%s_%s_ratio_up("(sqrt(pow((@0-@1)/@1,2) + pow((@2-@3)/@3,2))+1.)*@4",t_trg_%s_%s_data_up, t_trg_%s_%s_data, t_trg_%s_%s_mc_up, t_trg_%s_%s_mc, t_trg_%s_%s_ratio)' % (wp, y, wp, y, wp, y, wp, y, wp, y, wp, y))

    w.factory('expr::t_trg_%s_%s_ratio_down("(1.-sqrt(pow((@1-@0)/@1,2) + pow((@3-@2)/@3,2)))*@4",t_trg_%s_%s_data_down, t_trg_%s_%s_data, t_trg_%s_%s_mc_down, t_trg_%s_%s_mc, t_trg_%s_%s_ratio)' % (wp, y, wp, y, wp, y, wp, y, wp, y, wp, y))

# deepTau ID SFs

loc = 'inputs/2016/TauPOGTriggerSFs/'
tau_trg_file = ROOT.TFile(loc+'2016_tauTriggerEff_DeepTau2017v2p1.root')
#tau_id_wps=['VVVLoose','VVLoose','VLoose','Loose','Medium','Tight','VTight','VVTight']
tau_id_wps=['Medium']#,'Tight']

for wp in tau_id_wps:
  for dm in ['0','1','10',11]:

    histsToWrap = [
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:data_ditau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_ditau_dm%s_data' % (wp.lower(),dm)),
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:mc_ditau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_ditau_dm%s_mc' % (wp.lower(),dm)),
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:sf_ditau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_ditau_dm%s_ratio' % (wp.lower(),dm)),
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:data_mutau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_mutau_dm%s_data' % (wp.lower(),dm)),
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:mc_mutau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_mutau_dm%s_mc' % (wp.lower(),dm)),
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:sf_mutau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_mutau_dm%s_ratio' % (wp.lower(),dm)),
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:data_etau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_etau_dm%s_data' % (wp.lower(),dm)),
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:mc_etau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_etau_dm%s_mc' % (wp.lower(),dm)),
      (loc+'2016_tauTriggerEff_DeepTau2017v2p1.root:sf_etau_%s_dm%s_fitted' % (wp,dm),  't_trg_pog_deeptau_%s_etau_dm%s_ratio' % (wp.lower(),dm)),
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
  for chan in ['mt','tt']:
    for dm in ['0','1','2','10',11]:
      if chan == 'et': chan_name = 'etau'
      if chan == 'mt': chan_name = 'mutau'
      if chan == 'tt': chan_name = 'ditau'

      if not dm=='2':
        histsToWrap = [
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_HPSDM_%(dm)s_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_HPSDM_%(dm)s_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_mc' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_HPSDM_%(dm)s_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_ratio' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_HPSDM_%(dm)s_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_embed_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_HPSDM_%(dm)s_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_embed' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_HPSDM_%(dm)s_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_dm%(dm)s_embed_ratio' % vars()),
        ]

      if dm in ['1','2']:
        histsToWrap += [
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_mvaDM_%(dm)s_NoHPS0_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_mvaDM_%(dm)s_NoHPS0_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_mc' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_mvaDM_%(dm)s_NoHPS0_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_ratio' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_mvaDM_%(dm)s_NoHPS0_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_mvaDM_%(dm)s_NoHPS0_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_mvaDM_%(dm)s_NoHPS0_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed_ratio' % vars()),
        ]
      else:
        histsToWrap += [
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_mvaDM_%(dm)s_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_mvaDM_%(dm)s_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_mc' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingMCSamples_mvaDM_%(dm)s_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_ratio' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_mvaDM_%(dm)s_EffOfData_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed_data' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_mvaDM_%(dm)s_EffOfMC_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed' % vars()),
          (loc+'trigger_SF_tauh.root:%(chan)sChannel_2016_PredUsingembedSamples_mvaDM_%(dm)s_SF_Fitted' % vars(), 't_trg_ic_deeptau_%(wp)s_%(chan_name)s_mvadm%(dm)s_embed_ratio' % vars()),
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


### Tau Trigger scale factors from KIT - for using with deeptau IDs and for embedded samples

loc = 'inputs/2016/KIT/tau_trigger/'
tau_trg_file = ROOT.TFile(loc+'tauTriggerEfficiencies2016KIT_deeptau.root')
w.factory('expr::t_pt_trig("min(max(@0,20),450)" ,t_pt[0])')
tau_id_wps=['vlooseDeepTau','looseDeepTau','mediumDeepTau','tightDeepTau','vtightDeepTau','vvtightDeepTau']

for wp in tau_id_wps:
  for dm in ['0','1','10', '11']:
    histsToWrap = [
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:ditau_%s_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:ditau_%s_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:ditau_%s_dm%s_EMB' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:ditau_%s_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:ditau_%s_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:ditau_%s_dm%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:mutau_%s_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:mutau_%s_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:mutau_%s_dm%s_EMB' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:mutau_%s_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:mutau_%s_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:mutau_%s_dm%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:etau_%s_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:etau_%s_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:etau_%s_dm%s_EMB' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_embed' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:etau_%s_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:etau_%s_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2016KIT_deeptau.root:etau_%s_dm%s_EMB_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_embed' % (wp,dm))
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

loc='inputs/2016/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2016.root:VLoose', 't_id_dm_vloose'), 
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2016.root:Loose',  't_id_dm_loose'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2016.root:Medium', 't_id_dm_medium'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2016.root:Tight',  't_id_dm_tight'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2016.root:VTight', 't_id_dm_vtight'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2016.root:VVTight', 't_id_dm_vvtight')
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

sf_funcs['vloose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0351641+ ( x > 25 && x <=30)*0.9901479+ ( x > 30 && x <=35)*0.9885759+ ( x > 35 && x <=40)*0.915416+ (x > 40 && x <=500)*1.03785416637+ (x > 500 && x <= 1000)*(0.994397720614 + 0.0434564457594*(x/500.))+ (x > 1000)*(0.994397720614 + 0.0869128915189)'
sf_funcs['vloose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.7769241+ ( x > 25 && x <=30)*0.8708439+ ( x > 30 && x <=35)*0.8951739+ ( x > 35 && x <=40)*0.815878+ (x > 40 && x <= 500)*0.916727586761+ (x > 500 && x <= 1000)*(0.994397720614 - 0.0776701338527*(x/500.))+ (x > 1000)*(0.994397720614 - 0.155340267705)'
sf_funcs['loose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9455127+ ( x > 25 && x <=30)*0.8846971+ ( x > 30 && x <=35)*0.9378086+ ( x > 35 && x <=40)*0.9071475+ (x >40)*0.93317687081'
sf_funcs['loose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0379527+ ( x > 25 && x <=30)*0.9562731+ ( x > 30 && x <=35)*0.9732536+ ( x > 35 && x <=40)*0.9369315+ (x > 40 && x <= 500)*0.970668391301+ (x > 500 && x <= 1000)*(0.93317687081 + 0.0374915204912*(x/500.))+ (x > 1000)*(0.93317687081 + 0.0749830409824)'
sf_funcs['loose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8530727+ ( x > 25 && x <=30)*0.8131211+ ( x > 30 && x <=35)*0.9023636+ ( x > 35 && x <=40)*0.8773635+ (x > 40 && x <= 500)*0.893490649713+ (x > 500 && x <= 1000)*(0.93317687081 - 0.0396862210967*(x/500.))+ (x > 1000)*(0.93317687081 - 0.0793724421934)'
sf_funcs['medium'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9738206+ ( x > 25 && x <=30)*0.8908505+ ( x > 30 && x <=35)*0.9291307+ ( x > 35 && x <=40)*0.9109252+ (x >40)*0.89185502389'
sf_funcs['medium_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0604636+ ( x > 25 && x <=30)*0.9352495+ ( x > 30 && x <=35)*0.9598017+ ( x > 35 && x <=40)*0.9377822+ (x > 40 && x <= 500)*0.922756928271+ (x > 500 && x <= 1000)*(0.89185502389 + 0.0309019043812*(x/500.))+ (x > 1000)*(0.89185502389 + 0.0618038087624)'
sf_funcs['medium_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8871776+ ( x > 25 && x <=30)*0.8464515+ ( x > 30 && x <=35)*0.8984597+ ( x > 35 && x <=40)*0.8840682+ (x > 40 && x <= 500)*0.862460980443+ (x > 500 && x <= 1000)*(0.89185502389 - 0.029394043447*(x/500.))+ (x > 1000)*(0.89185502389 - 0.058788086894)'
sf_funcs['tight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9378085+ ( x > 25 && x <=30)*0.9105335+ ( x > 30 && x <=35)*0.9130542+ ( x > 35 && x <=40)*0.896008+ (x >40)*0.928217208056'
sf_funcs['tight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0053955+ ( x > 25 && x <=30)*0.9501775+ ( x > 30 && x <=35)*0.9419702+ ( x > 35 && x <=40)*0.920895+ (x > 40 && x <=500)*0.965954742861+ (x > 500 && x <= 1000)*(0.928217208056 + 0.0377375348049*(x/500.))+ (x > 1000)*(0.928217208056 + 0.0754750696098)'
sf_funcs['tight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8702215+ ( x > 25 && x <=30)*0.8708895+ ( x > 30 && x <=35)*0.8841382+ ( x > 35 && x <=40)*0.871121+ (x > 40 && x <= 500)*0.887186977688+ (x > 500 && x <= 1000)*(0.928217208056 - 0.041030230368*(x/500.))+ (x > 1000)*(0.928217208056 - 0.082060460736)'
sf_funcs['vtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.935252+ ( x > 25 && x <=30)*0.9029805+ ( x > 30 && x <=35)*0.8998639+ ( x > 35 && x <=40)*0.8812731+ (x >40)*0.949507022093'
sf_funcs['vtight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.994107+ ( x > 25 && x <=30)*0.9357555+ ( x > 30 && x <=35)*0.9254669+ ( x > 35 && x <=40)*0.9055981+ (x > 40 && x <=500)*0.985309390622+ (x > 500 && x <= 1000)*(0.949507022093 + 0.035802368529*(x/500.))+ (x > 1000)*(0.949507022093 + 0.0716047370581)'
sf_funcs['vtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.876397+ ( x > 25 && x <=30)*0.8702055+ ( x > 30 && x <=35)*0.8742609+ ( x > 35 && x <=40)*0.8569481+ (x > 40 && x <=500)*0.900052228358+ (x > 500 && x <= 1000)*(0.949507022093 - 0.0494547937346*(x/500.))+ (x > 1000)*(0.949507022093 - 0.0989095874691)'
sf_funcs['vvtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.932887+ ( x > 25 && x <=30)*0.8966382+ ( x > 30 && x <=35)*0.9024921+ ( x > 35 && x <=40)*0.8745323+ (x >40)*0.907242313227'
sf_funcs['vvtight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.978589+ ( x > 25 && x <=30)*0.9225292+ ( x > 30 && x <=35)*0.9255871+ ( x > 35 && x <=40)*0.8996693+ (x > 40 && x <=500)*0.945560083676+ (x > 500 && x <= 1000)*(0.907242313227 + 0.0383177704498*(x/500.))+ (x > 1000)*(0.907242313227 + 0.0766355408996)'
sf_funcs['vvtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.887185+ ( x > 25 && x <=30)*0.8707472+ ( x > 30 && x <=35)*0.8793971+ ( x > 35 && x <=40)*0.8493953+ (x > 40 && x <=500)*0.865580126851+ (x > 500 && x <= 1000)*(0.907242313227 - 0.0416621863752*(x/500.))+ (x > 1000)*(0.907242313227 - 0.0833243727504)'

import re
for x in sf_funcs:
  func = re.sub('x','@0',sf_funcs[x])
  w.factory('expr::t_id_pt_%s("%s",t_pt[0])' % (x, func))

# PRELIMINARY differential tau ID SFs for deepTau ID from Yuta

# dm binned SFs

loc='inputs/2016/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy.root:VVVLoose', 't_deeptauid_dm_vvvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy.root:VVLoose',  't_deeptauid_dm_vvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy.root:VLoose',   't_deeptauid_dm_vloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy.root:Loose',    't_deeptauid_dm_loose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy.root:Medium',   't_deeptauid_dm_medium'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy.root:Tight',    't_deeptauid_dm_tight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy.root:VTight',   't_deeptauid_dm_vtight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy.root:VVTight',  't_deeptauid_dm_vvtight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy_EMB.root:VVVLoose', 't_deeptauid_dm_embed_vvvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy_EMB.root:VVLoose',  't_deeptauid_dm_embed_vvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy_EMB.root:VLoose',   't_deeptauid_dm_embed_vloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy_EMB.root:Loose',    't_deeptauid_dm_embed_loose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy_EMB.root:Medium',   't_deeptauid_dm_embed_medium'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy_EMB.root:Tight',    't_deeptauid_dm_embed_tight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy_EMB.root:VTight',   't_deeptauid_dm_embed_vtight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2p1VSjet_2016Legacy_EMB.root:VVTight',  't_deeptauid_dm_embed_vvtight')
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
tauid_pt_file = ROOT.TFile(loc+'/TauID_SF_pt_DeepTau2017v2p1VSjet_2016Legacy.root')
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
tauid_pt_file = ROOT.TFile(loc+'/TauID_SF_pt_DeepTau2017v2p1VSjet_2016Legacy_EMB.root')
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
tauid_pt_file = ROOT.TFile(loc+'/TauID_SF_pt_DeepTau2017v2p1VSjet_2016Legacy_tight_antie_EMB.root')
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
  ('inputs/2016/tauIDSF/result_TauIDSF_ttAndmt_MC_2016.root:h_MVA_lowpt', 't_deeptauid_mvadm_medium_lowpt'),
  ('inputs/2016/tauIDSF/result_TauIDSF_ttAndmt_MC_2016.root:h_MVA_highpt', 't_deeptauid_mvadm_medium_highpt'),
  ('inputs/2016/tauIDSF/result_TauIDSF_ttAndmt_embed_2016.root:h_MVA_lowpt', 't_deeptauid_mvadm_embed_medium_lowpt'),
  ('inputs/2016/tauIDSF/result_TauIDSF_ttAndmt_embed_2016.root:h_MVA_highpt', 't_deeptauid_mvadm_embed_medium_highpt'),
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

loc='inputs/2016/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2016Legacy.root:VVLoose', 't_id_vs_e_eta_vvloose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2016Legacy.root:VLoose', 't_id_vs_e_eta_vloose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2016Legacy.root:Loose',  't_id_vs_e_eta_loose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2016Legacy.root:Medium', 't_id_vs_e_eta_medium'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2016Legacy.root:Tight',  't_id_vs_e_eta_tight'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSe_2016Legacy.root:VTight', 't_id_vs_e_eta_vtight'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSmu_2016Legacy.root:VLoose', 't_id_vs_mu_eta_vloose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSmu_2016Legacy.root:Loose',  't_id_vs_mu_eta_loose'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSmu_2016Legacy.root:Medium', 't_id_vs_mu_eta_medium'),
  (loc+'/TauID_SF_eta_DeepTau2017v2p1VSmu_2016Legacy.root:Tight',  't_id_vs_mu_eta_tight'),

]

w.factory('expr::t_eta_bounded("min(2.3,TMath::Abs(@0))" ,t_eta[0])')

for task in histsToWrap:
  wsptools.SafeWrapHist(w, ['t_eta_bounded'], GetFromTFile(task[0]), name=task[1])
  uncert_hists = wsptools.UncertsFromHist(GetFromTFile(task[0]))
  wsptools.SafeWrapHist(w, ['t_eta_bounded'], uncert_hists[0], name=task[1]+'_abs_up')
  wsptools.SafeWrapHist(w, ['t_eta_bounded'], uncert_hists[1], name=task[1]+'_abs_down')
  w.factory('expr::%s_up("@1+@0",%s_abs_up,%s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_down("@1-@0",%s_abs_down,%s)' % (task[1],task[1],task[1]))


# em channel OS/SS factors from UW   
loc = "inputs/2016/em_osss/"

em_osss_fits = ROOT.TFile(loc+'/osss_em_2016.root')

# get linear funtions vs dR for each njets bin
for njet in [0,1,2]:
  for x in ['','_unc1_up','_unc1_down','_unc2_up','_unc2_down']:
    func = em_osss_fits.Get('OSSS_qcd_%(njet)ijet_2016%(x)s' % vars())
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
                      GetFromTFile(loc+'/closure_2016.root:correction'), 'em_qcd_osss_ss_corr')
wsptools.SafeWrapHist(w, ['m_pt', 'e_pt'],
                      GetFromTFile(loc+'/closure_2016.root:closureOS'), 'em_qcd_osss_os_corr')

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
w.writeToFile('output/htt_scalefactors_legacy_2016.root')
w.Delete()
