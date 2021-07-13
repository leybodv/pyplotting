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

def import_diff_peaks(filepath, wavelength, cardid = None, phasename = None):
    """
    Imports peaks from diff file in a form of d/intensity values and converts them to 2*thetta / relative intensity

    Parameters
    ----------
    filepath : str
        path to diff file with d/intensity columns

    wavelength : float
        wavelength of X-ray radiation in Angstroms

    cardid : str (default : None)
        card number in database of diffraction data

    phasename : str (default : None)
        phase name the peaks belong to

    Returns
    -------
    data : tuple
        tuple with data in a format (cardid, phasename, <2*thetta>, <i_rel>)

    2*thetta : ndarray
        array of 2*thetta values

    i_rel : ndarray
        array of relative intensity values
    """
    d, i = np.loadtxt(fname = filepath, unpack = True)
    i_rel = i / i.max()
    dthetta = 2 * np.arcsin(wavelength / 2 / d) * 180 / np.pi
    i_rel = i_rel[~np.isnan(dthetta)]
    dthetta = dthetta[~np.isnan(dthetta)]
    return (cardid, phasename, dthetta, i_rel)
