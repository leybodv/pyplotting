import plot_utils
import matplotlib.pyplot as plt
import numpy as np

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
