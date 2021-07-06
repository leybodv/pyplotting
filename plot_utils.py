#!/usr/bin/env python

import numpy as np

def stack_by_percent(y0, y1, percent = 10):
    """
    Raise y1 above y0 on percent * (max(y0) - min(y0)) / 100

    Parameters
    ----------
    y0 : ndarray
        relative to this plot y1 will be raised up

    y1 : ndarray
        this plot will be raised up

    percent : int, default: 10
        how high will y1 be raised up relative to y0

    Returns
    -------
    y1n : ndarray
        array with new values of y1 raised relative to y0 OR y1 if all elements in y0 and y1 are equal
    """
    if (y0 == y1).all():
        return y1
    delta0 = (y1 - y0).min()
    delta1 = (y0.max() - y0.min()) * percent / 100
    y1n = y1 - delta0 + delta1
    return y1n
