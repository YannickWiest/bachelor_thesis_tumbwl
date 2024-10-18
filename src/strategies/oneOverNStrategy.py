import numpy as np

def name():
    return '1/N'

def strategy(_, valid_returns_window, __, ___):
    n_valid_stocks = valid_returns_window.shape[1]
    return np.ones(n_valid_stocks) / n_valid_stocks, ___
