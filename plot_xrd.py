#!/usr/bin/env python

import plot_utils
import matplotlib.pyplot as plt
import numpy as np
import sys

def plot_xrd(ax, data):
    """
    Makes plot of xrd data in a stacked by 10% form

    Parameters
    ----------
    ax : Axes
        The axes to draw to

    data : list
        list of tuples of data in a format [(x0, y0, label0), (x1, y1, label1), ...]

    Returns
    -------
    out : list
        list of artists added
    """
    y0 = data[0][1]
    for x1, y1, label1 in data:
        y1n = plot_utils.stack_by_percent(y0, y1)
        ax.plot(x1, y1n, label = label1, linewidth = 1)
        y0 = y1n

    ax.set_xlim(20, 140)
    ax.set_xlabel('2θ, deg')
    ax.set_ylabel('Relative intensity')
    ax.grid(linestyle='--')
    ax.legend()

    out = ax.get_children()

    return out

def import_xrds(paths):
    """
    Imports xrd data exported in text format from Difrey-401 device

    Parameters
    ----------
    paths : dictionary
        Dictionary containing label, path-to-data-file pairs

    Returns
    -------
    data : list
        List of tuples of data in a format [(x0, y0, label0), (x1, y1, label1), ...]
    """
    data = list()
    paths_items = paths.items()
    for label, path in paths_items:
        x, y = np.loadtxt(fname = path, skiprows = 1, unpack = True)
        y_rel = y / y.max()
        data.append((x, y_rel, label))

    return data

# script starts here

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
