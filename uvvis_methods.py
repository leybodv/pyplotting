import numpy as np
import scipy.constants as spc
import scipy.optimize as spopt
import scipy.signal as spsig
import matplotlib.pyplot as plt
import plot_utils
import math

def linear_func(x, k, b):
    """
    Calculates values of linear function k * x + b

    Parameters
    ----------
    x : float or list or ndarray
        values of independent variables
    k : float
        coefficient in an equation k * x + b
    b : float
        coefficient in an equation k * x + b

    Returns
    -------
    y : float or list or ndarray
        values of dependent variable
    """
    return k * x + b

def differentiate(x, y):
    """
    Finds first derivative from (x, y) data points numerically as dy/dx|x[i] = (y[i+1] - y[i-1]) / (x[i+1] - x[i-1])

    Parameters:
    -----------
    x : ndarray
        abscissa values
    y : ndarray
        ordinate values

    Returns:
    --------
    dx : ndarray
        x values, size of new array decreased by 2 elements from the beginning and the end of initial array
    dydx : ndarray
        dy/dx values
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
    Fits part of Tauc's plot data by line

    Parameters:
    -----------
    x : ndarray
        Tauc's x coordinates
    y : ndarray
        Tauc's y coordinates
    low_x : float
        lower x limit to fit data from
    high_x : float
        higher x limit to fit data to

    Retutns:
    --------
    popt : array
        Optimal values for the parameters k, b of linear function k * x + b calculated by least squares method (See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html)
    pcov: 2-D array
        The estimated covariance of popt (See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html)
    """
    print(f'uvvis_methods.fit_tauc_linear:') # LOG
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
            1/2 - for indirect transitions
            2 - for direct transitions
    """
    print(f'plot_uvvis.plot_tauc:') # LOG
    tauc_data = calculate_tauc(data, power)
    tmp_y_tauc = tauc_data[0][2]
    y_lim_bottom = math.inf
    y_lim_top = -math.inf
    for i in range(len(tauc_data)):
        print(f'{i = }') # LOG
        label, x_tauc, y_tauc, power = tauc_data[i]
        if baseline_low_x != None and baseline_high_x != None and bandgap_low_x != None and bandgap_high_x != None:
            bandgap, baseline, bandgap_line = calculate_bandgap(x_tauc, y_tauc, baseline_low_x[i], baseline_high_x[i], bandgap_low_x[i], bandgap_high_x[i])
            bandgap_x, bandgap_y = bandgap
            baseline_x, baseline_y = baseline
            bandgap_line_x, bandgap_line_y = bandgap_line
        if i != 0:
            y_tauc_raised = plot_utils.stack_by_percent(tmp_y_tauc, y_tauc)
            delta_y = y_tauc_raised - y_tauc
            y_tauc = y_tauc_raised
            tmp_y_tauc = y_tauc
            if baseline_low_x != None and baseline_high_x != None and bandgap_low_x != None and bandgap_high_x != None:
                bandgap_y = bandgap_y + delta_y[0]
                baseline_y = baseline_y + delta_y
                bandgap_line_y = bandgap_line_y + delta_y
        if y_tauc.max() > y_lim_top:
            y_lim_top = y_tauc.max()
        if y_tauc.min() < y_lim_bottom:
            y_lim_bottom = y_tauc.min()
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][i]
        ax.plot(x_tauc, y_tauc, label = label, color = color)
        if baseline_low_x != None and baseline_high_x != None and bandgap_low_x != None and bandgap_high_x != None:
            ax.plot(baseline_x, baseline_y, color = color, linestyle = '--', linewidth = 0.5)
            ax.plot(bandgap_line_x, bandgap_line_y, color = color, linestyle = '--', linewidth = 0.5)
            ax.vlines(x = bandgap_x, ymin = y_lim_bottom * 0.95, ymax = bandgap_y, color = color, linestyle = '--', linewidth = 0.5)
            ax.annotate(text = f'{bandgap_x:.2f}', xy = (bandgap_x, y_lim_bottom * 0.95), verticalalignment = 'top', horizontalalignment = 'center', rotation = 'vertical')
    ax.set_ylim(bottom = y_lim_bottom * 0.95, top = y_lim_top * 1.05)
    ax.set_xlabel('E, eV')
    ax.set_ylabel(f'$\mathregular{{(αE)^{{{power}}}}}$')
    if power == 2:
        ax.set_title("Direct transitions")
    if power == 0.5:
        ax.set_title("Indirect transitions")
    ax.grid(linestyle = '--')
    ax.legend()
    return ax

def calculate_bandgap(x_tauc, y_tauc, baseline_low_x, baseline_high_x, bandgap_low_x, bandgap_high_x):
    """
    Calculates Tauc's bandgap as intersection of baseline line and linear fit of the part of Tauc's data

    Parameters:
    -----------
    x_tauc : ndarray
        x values of Tauc's data
    y_tauc : ndarray
        y values of Tauc's data
    baseline_low_x : float
        lower limit of x to fit Tauc's data by line for baseline
    baseline_high_x : float
        higher limit of x to fit Tauc's data by line for baseline
    bandgap_low_x : float
        lower limit of x to fit Tauc's data
    bandgap_high_x : float
        higher limit of x to fit Tauc's data

    Returns:
    -------
    (bandgap_x, bandgap_y) : tuple
        bandgap_x : float
        bandgap_y : float
            coordinate of intersection of baseline with fitted line of the part of Tauc's data, x is the bandgap value
    (baseline_x, baseline_y) : tuple
        baseline_x : ndarray
        baseline_y : ndarray
            coordinates of baseline
    (bandgap_line_x, bandgap_line_y) : tuple
        bandgap_line_x : ndarray
        bandgap_line_y : ndarray
            coordinates of fitted line of the part of Tauc's data
    """
    print(f'uvvis_methods.calculate_bandgap') # LOG
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
    print(f'{bandgap_x = }') # LOG
    return ((bandgap_x, bandgap_y), baseline, bandgap_line)

def plot_tauc_diff(ax, data, power, smooth = False):
    """
    Plots first derivative of Tauc's data. The plot can be used for more accurate choise of limits for linear fit of Tauc's data

    Parameters:
    -----------
    ax : Axes
        axes object to draw to
    data : list
        raw uv-vis data, list of tuples in a format (<label>, <wavelength>, <absorbance>)
        <label> : str
            label of the plot
        <wavelength> : ndarray
            array of wavelength in nm
        <absorbance> : ndarray
            array of absorbances in cm^(-1)
    power : float
        power in the Tauc's equation:
            1/2 - for indirect transitions
            2 - for direct transitions
    smooth : boolean
        whether to use smoothing by Savitzky-Golay method with window_length = 15 and polyorder = 5 (See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html), smoothed curve is drawn on top of unsmoothed one

    Returns:
    -------
    ax : Axes
        axes object with first derivative of Tauc's data plot
    """
    tauc_data_diff = calculate_tauc_diff(data, power)
    tmp_y = tauc_data_diff[0][2]
    if smooth:
        tmp_y_smooth = spsig.savgol_filter(tauc_data_diff[0][2], 15, 5)
    for i in range(len(tauc_data_diff)):
        l, x, y, p = tauc_data_diff[i]
        if smooth:
            y_smooth = spsig.savgol_filter(y, 15, 5)
        if i != 0:
            y = plot_utils.stack_by_percent(tmp_y, y)
            if smooth:
                y_smooth = plot_utils.stack_by_percent(tmp_y_smooth, y_smooth)
            tmp_y = y
        ax.plot(x, y, label = l)
        if smooth:
            ax.plot(x, y_smooth)
    ax.set_xlabel('E, eV')
    ax.set_ylabel(f'$\mathregular{{d[(αE)^{{{power}}}]/d[E]}}$')
    if power == 2:
        ax.set_title("Indirect transitions")
    if power == 0.5:
        ax.set_title("Direct transitions")
    ax.grid(linestyle = '--')
    ax.legend()
    return ax
