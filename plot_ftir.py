#!/usr/bin/env python

import plot_utils
import matplotlib.pyplot as plt
import numpy as np
import sys

def plot_ftir(ax, data):
    """
    Makes plot of ftir data in a stacked by 10% form

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

    ax.set_xlim(400, 4000)
    ax.set_xlabel('Wavenumber, $\mathregular{cm^{-1}}$')
    ax.set_ylabel('Transmittance')
    ax.grid(linestyle='--')
    ax.invert_xaxis()
    ax.legend()

    out = ax.get_children()

    return out

def import_ftirs(paths):
    """
    Imports ftir data exported in text format from Bruker Vertex 70 device

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
        x, y = np.loadtxt(fname = path, delimiter = '\t', unpack = True)
        data.append((x, y, label))

    return data

# script starts here

args = sys.argv.copy()
specs = list()
labels = list()
out = list()
while args:
    if args[0] == '--specs':
        args.pop(0)
        while not len(args) == 0 and '--' not in args[0]:
            specs.append(args.pop(0))
        print('specs:', specs)
    if args[0] == '--labels':
        args.pop(0)
        while not len(args) == 0 and '--' not in args[0]:
            labels.append(args.pop(0))
        print('labels:', labels)
    if args[0] == '--out':
        args.pop(0)
        out = args.pop(0)
        print('out:', out)
    if not len(args) == 0:
        args.pop(0)

paths = dict(zip(labels, specs))
print("paths:", paths)
data = import_ftirs(paths)
fig, ax = plt.subplots()
fig.set_size_inches(w = 1024/96, h = 768/96)
plot_ftir(ax, data)
fig.savefig(fname = out, dpi = 96, format = 'png')
