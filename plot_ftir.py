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
for i in range(len(sys.argv)):
    if sys.argv[i] == '--specs':
        specs = sys.argv[i+1].split(sep = ',')
        print('specs:', specs)
    elif sys.argv[i] == '--labels':
        labels = sys.argv[i+1].split(sep = ',')
        print('labels:', labels)
    elif sys.argv[i] == '--out':
        out = sys.argv[i+1]
        print('out:', out)

paths = dict(zip(labels, specs))
print(paths)
data = import_ftirs(paths)
fig, ax = plt.subplots()
plot_ftir(ax, data)
plt.savefig(fname = out)
