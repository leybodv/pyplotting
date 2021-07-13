#!/usr/bin/env python

import plot_utils
import plot_xrd_methods
import matplotlib.pyplot as plt
import sys

args = sys.argv.copy()
raw_data = list()
labels = list()
out = list()
while args:
    if args[0] == '--raw':
        args.pop(0)
        while not len(args) == 0 and '--' not in args[0]:
            raw_data.append(args.pop(0))
        print('raw_data:', raw_data)
    if args[0] == '--labels':
        args.pop(0)
        while not len(args) == 0 and '--' not in args[0]:
            labels.append(args.pop(0))
        print('labels:', labels)
    if args[0] == '--out':
        args.pop(0)
        out = args.pop(0)
        print('out:', out)
    if not len(args) == 0 and args[0] == '--help':
        print('Usage: plot_xrd --raw <paths-to-xrd-data-files> --labels <plot-labels> --out <path-to-output-figure>')
        quit()
    if not len(args) == 0:
        args.pop(0)

paths = dict(zip(labels, raw_data))
print("paths:", paths)
data = import_xrds(paths)
fig, ax = plt.subplots()
fig.set_size_inches(w = 1024/96, h = 768/96)
plot_xrd(ax, data)
fig.savefig(fname = out, dpi = 96, format = 'png')
