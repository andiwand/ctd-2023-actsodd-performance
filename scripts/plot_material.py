#!/usr/bin/env python3

import uproot
import matplotlib.pyplot as plt
import mplhep
import argparse

from mycommon.plot_style import myPlotStyle


plt.rcParams["ytick.right"] = plt.rcParams["xtick.top"] = True
plt.rcParams["xtick.direction"] = "in"
plt.rcParams["ytick.direction"] = "in"
plt.rcParams["font.size"] = 12.0
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["legend.frameon"] = False
plt.rcParams["legend.columnspacing"] = 0.2
plt.rcParams["legend.handletextpad"] = 0.2
plt.rcParams["legend.labelspacing"] = 0.2
plt.rcParams["legend.borderpad"] = 0
plt.rcParams["legend.handlelength"] = 1.0


myPlotStyle()

parser = argparse.ArgumentParser(description="Make material composition plots")
parser.add_argument("x", choices=["eta", "pt"])
parser.add_argument("y", choices=["l0", "x0"])
parser.add_argument("input", help="Input root file with histograms")
parser.add_argument("--output")
args = parser.parse_args()

args.output.mkdir(parents=True, exist_ok=True)

rf = uproot.open(args.input)

names = {
    "all": "Full detector",
    "beampipe": "Beam pipe",
    "sstrips": "Short Strips",
    "lstrips": "Long Strips",
    "pixel": "Pixel",
    "solenoid": "Solenoid",
    "ecal": "EM Calorimeter",
}

y_label = {"l0": r"$\lambda_0$", "x0": "$X_0$"}[args.y]

hists = []
labels = []

for k in rf:
    name, _ = k.split(";", 1)
    if not name.endswith("all"):
        continue
    if not args.y in name:
        continue
    if not args.x in name:
        continue
    if name.startswith("detector"):
        continue

    o = rf[k].to_hist()
    o.axes[0].label = args.x
    hists.append(o)
    l, _ = k.split("_", 1)
    l = names[l]
    labels.append(l)

ax = plt.gcf().subplots()
mplhep.histplot(hists, ax=ax, stack=True, histtype="fill", label=labels)
ymin, ymax = ax.get_ylim()
ax.set_xlim(hists[0].axes[0].edges[0], hists[0].axes[0].edges[-1])
ax.set_ylim(top=1.2 * ymax)
ax.set_ylabel(y_label)
ax.legend(ncol=3)

if args.output:
    plt.savefig(args.output)
else:
    plt.show()