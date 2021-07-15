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
        wavelength, absorbance = np.loadtxt(path, delimiter = '\t', encoding = 'utf-8', unpack = True)
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
    """
    tauc_data = list()
    for label, wavelength, absorbance in data:
        y_tauc = ((absorbance * (10**2) * spc.h * (spc.c * (10 ** 9) / wavelength)) / spc.e) ** power # (eV / m)^power
        x_tauc = (spc.h * spc.c * (10 ** 9) / wavelength) / spc.e # eV
        tauc_data.append((label, x_tauc, y_tauc))
    for label, x_tauc, y_tauc in tauc_data:
        ax.plot(x_tauc, y_tauc, label = label)
    ax.set_xlabel('E, eV')
    ax.set_ylabel(f'$\mathregular{{(αE)^{{{power}}}}}$')
    ax.grid(linestyle = '--')
    ax.legend()
    return ax
