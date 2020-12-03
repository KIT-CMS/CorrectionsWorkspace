#!/usr/bin/env python
import argparse
import os

import ROOT

p0_ = { # constant parameter
              "2016" : {
                  "0j" : {"nom": "1.956", "up": "2.018", "down": "1.894"},
                  "1j" : {"nom": "1.890", "up": "1.930", "down": "1.850"},
                  "2j" : {"nom": "1.753", "up": "1.814", "down": "1.692"},
              },
              "2017" : {
                  "0j" : {"nom": "1.928", "up": "1.993", "down": "1.863"},
                  "1j" : {"nom": "2.020", "up": "2.060", "down": "1.980"},
                  "2j" : {"nom": "1.855", "up": "1.914", "down": "1.796"},
              },
              "2018" : {
                  "0j" : {"nom": "1.963", "up": "2.010", "down": "1.916"},
                  "1j" : {"nom": "2.014", "up": "2.045", "down": "1.983"},
                  "2j" : {"nom": "1.757", "up": "1.794", "down": "1.720"},
              }
}
p1_ = { # linear parameter
              "2016" : {
                  "0j" : {"nom": "-0.2287", "up": "-0.1954", "down": "-0.262"},
                  "1j" : {"nom": "-0.3251", "up": "-0.2972", "down": "-0.353"},
                  "2j" : {"nom": "-0.2802", "up": "-0.2402", "down": "-0.3202"},
              },
              "2017" : {
                  "0j" : {"nom": "-0.1949", "up": "-0.1617", "down": "-0.2281"},
                  "1j" : {"nom": "-0.3685", "up": "-0.3445", "down": "-0.3925"},
                  "2j" : {"nom": "-0.3531", "up": "-0.3154", "down": "-0.3908"},
              },
              "2018" : {
                  "0j" : {"nom": "-0.1644", "up": "-0.1402", "down": "-0.1886"},
                  "1j" : {"nom": "-0.3172", "up": "-0.2977", "down": "-0.3367"},
                  "2j" : {"nom": "-0.3627", "up": "-0.3389", "down": "-0.3865"},
              }
}
p2_ = { # quadratic parameter
              "2016" : {
                  "0j" : {"nom": "-0.1138", "up": "-0.0922", "down": "-0.1354"},
                  "1j" : {"nom": "-0.07938","up": "-0.06242", "down": "-0.09634"},
                  "2j" : {"nom": "-0.02602","up": "-0.00307", "down": "-0.04897"},
              },
              "2017" : {
                  "0j" : {"nom": "-0.1430", "up": "-0.12", "down": "-0.166"},
                  "1j" : {"nom": "-0.05544","up": "-0.03986", "down": "-0.07102"},
                  "2j" : {"nom": "0.03128","up": "0.05409", "down": "0.00847"},
              },
              "2018" : {
                  "0j" : {"nom": "-0.1249", "up": "-0.1083", "down": "-0.1415"},
                  "1j" : {"nom": "-0.04374","up": "-0.03139", "down": "-0.05609"},
                  "2j" : {"nom": "-0.00606","up": "0.005143", "down": "-0.024355"},
              }
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--era", help="Experiment era.")
    return parser.parse_args()


def main(args):
    path = "inputs/{}/em_osss/DESY/".format(args.era)
    input_file = ROOT.TFile(os.path.join(path, "QCDweights.root"), "read")
    out_file = ROOT.TFile(os.path.join(path, "input_qcd_weights.root"), "recreate")
    func = ROOT.TF1("transfer function", "[2]*((x-3)^2-3)+[1]*(x-3)+[0]", 0.3, 6)
    combinations = {
            "": ("nom", "nom", "nom"),
            "_shape_up": ("nom", "up", "nom"),
            "_shape2_up": ("nom", "nom", "up"),
            "_shape_down": ("nom", "down", "nom"),
            "_shape2_down": ("nom", "nom", "down"),
            "_rate_up": ("up", "nom", "nom"),
            "_rate_down": ("down", "nom", "nom"),
        }
    for njet in [0, 1, 2]:
        for name, shifts in combinations.items():
            func.SetParameter(0, float(p0_[args.era]["%ij"%njet][shifts[0]]))
            func.SetParameter(1, float(p1_[args.era]["%ij"%njet][shifts[1]]))
            func.SetParameter(2, float(p2_[args.era]["%ij"%njet][shifts[2]]))
            func.SetName("OS_SS_transfer_factors_%ijet%s" % (njet, name))
            func.Write()
    for hname in ["NonClosureCorrection", "IsolationCorrection"]:
        hist = input_file.Get(hname)
        hist.Write()
    out_file.Close()
    input_file.Close()
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
