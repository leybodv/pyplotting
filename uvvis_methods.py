import numpy as np
import scipy.constants as spc
import matplotlib.pyplot as plt
import plot_utils

def import_data(labels, paths):
    """
    Imports uv-vis data from text file

    Parameters
    ----------
    labels : list
        list of labels of corresponding uv-vis spectra

    paths : list
        list of paths of corresponding raw uv-vis spectra file

    Returns
    -------
    data : list
        list of tuples in a format (label, wavelength, absorbance)

        label : str
            label of spectrum
        wavelength : ndarray
            array of wavelengths
        absorbance : ndarray
            array of absorbances
    """
#    print(f'labels: {labels}')
#    print(f'paths: {paths}')
    data = list()
    for label, path in zip(labels, paths):
#        print(f'label: {label}')
#        print(f'path: {path}')
#        with open(file = path, mode = 'r', encoding = 'utf-8') as f:
#            for line in f:
#                print(line.replace('\t', '->').replace('\n', '¶').replace('\r', '|'))
        wavelength, absorbance = np.loadtxt(path, delimiter = '\t', skiprows = 1, usecols = (0, 1), encoding = 'utf-8', unpack = True)
        data.append((label, wavelength, absorbance))
    return data

def plot_uvvis(ax, data):
    """
    Plot uv-vis data

    Parameters
    ----------
    ax : Axes
        axes object to draw to

    data : list
        list of tuples in a format (label, wavelength, absorbance)
        label : str
            label to place in a legend
        wavelength : ndarray
            array of wavelengths
        absorbance : ndarray
            array of absorbances

    Returns
    -------
    ax : Axes
        axes object with drawn curves
    """
    x_min = 10000
    x_max = 0
    tmp_absorbance = data[0][2]
    for i in range(len(data)):
        label, wavelength, absorbance = data[i]
        if i != 0:
            absorbance = plot_utils.stack_by_percent(tmp_absorbance, absorbance, percent = 20)
            tmp_absorbance = absorbance
        if wavelength.max() > x_max:
            x_max = wavelength.max()
        if wavelength.min() < x_min:
            x_min = wavelength.min()
        ax.plot(wavelength, absorbance, label = label)
    ax.set_xlim(left = x_min, right = x_max)
    ax.set_xlabel('Wavelength, nm')
    ax.set_ylabel('Absorbance, $\mathregular{cm^{-1}}$')
    ax.grid(linestyle = '--')
    ax.legend()
    return ax

def plot_tauc(ax, data, power):
    """
    Plots uv-vis data in Tauc coordinates:
        (<absorbance> * <energy>)^power vs. <energy>

    Parameters
    ----------
    ax : Axes
        axes to plot to

    data : list
        list of tuples in a format (<label>, <wavelength>, <absorbance>)
        <label> : str
            label of the plot
        <wavelength> : ndarray
            array of wavelength in nm
        <absorbance> : ndarray
            array of absorbances in cm^(-1)

    power : float
        power in the Tauc's equation:
            1/2 - for direct transitions
            2 - for indirect transitions
    """
    tauc_data = list()
    for label, wavelength, absorbance in data:
        energy = (spc.h * spc.c * 10**9 / wavelength) / spc.e # in eV
        y_tauc = (absorbance * 10**2 * energy) ** power # in [eV / m]^power
        x_tauc = energy # in eV
        tauc_data.append((label, x_tauc, y_tauc))
    for label, x_tauc, y_tauc in tauc_data:
        ax.plot(x_tauc, y_tauc, label = label)
    ax.set_xlabel('E, eV')
    ax.set_ylabel(f'$\mathregular{{(αE)^{{{power}}}}}$')
    if power == 2:
        ax.set_title("Indirect transitions")
    if power == 0.5:
        ax.set_title("Direct transitions")
    ax.grid(linestyle = '--')
    ax.legend()
    return ax
