import numpy as np
import scipy.constants as spc
import scipy.optimize as spopt
import scipy.signal as spsig
import matplotlib.pyplot as plt
import plot_utils

def linear_func(x, k, b):
    """
    """
    return k * x + b

def differentiate(x, y):
    """
    """
    dx = list()
    dydx = list()
    for i in range(len(x))[1:-1]:
        dx.append(x[i])
        dydx.append((y[i+1]-y[i-1])/(x[i+1]-x[i-1]))
    return (dx, dydx)

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

def calculate_tauc(raw_data, power):
    """
    Calculate data for Tauc plot:
        (<absorbance> * <energy>)^power vs. <energy>

    Parameters
    ----------
    raw_data : list
        list of tuples in a format (<label>, <wavelength>, <absorbance>)
        <label> : str
            label of the data
        <wavelength> : ndarray
            array of wavelength in nm
        <absorbance> : ndarray
            array of absorbances in cm^(-1)

    power : float
        power in the Tauc's equation:
            1/2 - for direct transitions
            2 - for indirect transitions

    Returns
    -------
    tauc_data : list
        list of tuples in a format (<label>, <x_tauc>, <y_tauc>, <power>)
        <label> : str
            label of the data
        <x_tauc> : ndarray
            array of <energy> values in eV
        <y_tauc> : ndarray
            array of (<absorbance> * <energy>)^power values in (eV/m)^power
        <power> : float
            power in Tauc's equation
    """
    tauc_data = list()
    for label, wavelength, absorbance in raw_data:
        energy = (spc.h * spc.c * 10**9 / wavelength) / spc.e # in eV
        y_tauc = (absorbance * 10**2 * energy) ** power # in [eV / m]^power
        x_tauc = energy # in eV
        tauc_data.append((label, x_tauc, y_tauc, power))
    return tauc_data

def calculate_tauc_diff(raw_data, power):
    """
    Calculates numerical first derivative of Tauc's plot:
        d[(<absorbance> * <energy>)^power] / d[<energy>]

    Parameters
    -----------
    raw_data : list
        list of tuples in a format (<label>, <wavelength>, <absorbance>)
        <label> : str
            label of the data
        <wavelength> : ndarray
            array of wavelength in nm
        <absorbance> : ndarray
            array of absorbances in cm^(-1)

    power : float
        power in the Tauc's equation:
            1/2 - for direct transitions
            2 - for indirect transitions

    Returns
    -------
    tauc_data_diff : list
        list of tuples in a format (<label>, <x_tauc>, <y_tauc_diff>, <power>)
        <label> : str
            label of the data
        <x_tauc> : ndarray
            array of <energy> values in eV
        <y_tauc> : ndarray
            array of d[(<absorbance> * <energy>)^power]/d[<energy>] values
        <power> : float
            power in Tauc's equation
    """
    tauc_data_diff = list()
    tauc_data = calculate_tauc(raw_data, power)
    for label, x_tauc, y_tauc, power in tauc_data:
        x_diff, y_diff = differentiate(x_tauc, y_tauc)
        tauc_data_diff.append((label, x_diff, y_diff, power))
    return tauc_data_diff

def fit_tauc_linear(x, y, low_x, high_x):
    """
    """
    print(f'uvvis_methods.fit_tauc_linear:') # LOG
    print(f'{x = }') # LOG
    print(f'{x.size = }') # LOG
    print(f'{y = }') # LOG
    print(f'{y.size = }') # LOG
    print(f'{low_x = }') # LOG
    print(f'{high_x = }') # LOG
    print(f'{x >= low_x = }') # LOG
    print(f'{(x >= low_x).size = }') # LOG
    print(f'{x <= high_x = }') # LOG
    print(f'{(x <= high_x).size = }') # LOG
    x_lim = x[np.logical_and(x >= low_x, x <= high_x)]
    y_lim = y[np.logical_and(x >= low_x, x <= high_x)]
    fitted_data = spopt.curve_fit(linear_func, x_lim, y_lim)
    return fitted_data

def plot_tauc(ax, data, power, baseline_low_x = None, baseline_high_x = None, bandgap_low_x = None, bandgap_high_x = None):
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
    print(f'plot_uvvis.plot_tauc:') # LOG
    tauc_data = calculate_tauc(data, power)
    tmp_y_tauc = tauc_data[0][2]
    for i in range(len(tauc_data)):
        label, x_tauc, y_tauc, power = tauc_data[i]
        if baseline_low_x != None and baseline_high_x != None and bandgap_low_x != None and bandgap_high_x != None:
            bandgap, baseline, bandgap_line = calculate_bandgap(x_tauc, y_tauc, baseline_low_x, baseline_high_x, bandgap_low_x, bandgap_high_x)
            bandgap_x, bandgap_y = bandgap
            baseline_x, baseline_y = baseline
            bandgap_line_x, bandgap_line_y = bandgap_line
        if i != 0:
            y_tauc = plot_utils.stack_by_percent(tmp_y_tauc, y_tauc)
            delta_y = y_tauc - tmp_y_tauc
            tmp_y_tauc = y_tauc
            if baseline_low_x != None and baseline_high_x != None and bandgap_low_x != None and bandgap_high_x != None:
                bandgap_y = bandgap_y + delta_y
                baseline_y = baseline_y + delta_y
                bandgap_line_y = bandgap_line_y + delta_y
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][i]
        ax.plot(x_tauc, y_tauc, label = label, color = color)
    ax.set_xlabel('E, eV')
    ax.set_ylabel(f'$\mathregular{{(αE)^{{{power}}}}}$')
    if power == 2:
        ax.set_title("Indirect transitions")
    if power == 0.5:
        ax.set_title("Direct transitions")
    ax.grid(linestyle = '--')
    ax.legend()
    return ax

def calculate_bandgap(x_tauc, y_tauc, baseline_low_x, baseline_high_x, bandgap_low_x, bandgap_high_x):
    """
    """
    baseline_fitted_data = fit_tauc_linear(x_tauc, y_tauc, baseline_low_x, baseline_high_x)
    bandgap_fitted_data = fit_tauc_linear(x_tauc, y_tauc, bandgap_low_x, bandgap_high_x)
    k_baseline = baseline_fitted_data[0][0]
    b_baseline = baseline_fitted_data[0][1]
    k_bandgap = bandgap_fitted_data[0][0]
    b_bandgap = bandgap_fitted_data[0][1]
    bandgap_x = (b_baseline - b_bandgap) / (k_bandgap - k_baseline)
    bandgap_y = linear_func(bandgap_x, k_bandgap, b_bandgap)
    baseline = (x_tauc, linear_func(x_tauc, k_baseline, b_baseline))
    bandgap_line = (x_tauc, linear_func(x_tauc, k_bandgap, b_bandgap))
    return ((bandgap_x, bandgap_y), baseline, bandgap_line)

def plot_tauc_diff(ax, data, power):
    """
    """
    tauc_data_diff = calculate_tauc_diff(data, power)
    tmp_y = tauc_data_diff[0][2]
    for i in range(len(tauc_data_diff)):
        l, x, y, p = tauc_data_diff[i]
        if i != 0:
            y = plot_utils.stack_by_percent(tmp_y, y)
            tmp_y = y
        ax.plot(x, y, label = l)
    ax.set_xlabel('E, eV')
    ax.set_ylabel(f'$\mathregular{{d[(αE)^{{{power}}}]/d[E]}}$')
    if power == 2:
        ax.set_title("Indirect transitions")
    if power == 0.5:
        ax.set_title("Direct transitions")
    ax.grid(linestyle = '--')
    ax.legend()
    return ax
