import numpy as np

def name():
    return 'mom'

def strategy(_, valid_returns_window, __, ___):

    expected_returns = np.prod(1 + valid_returns_window, axis=0) - 1

    n = len(expected_returns)
    n_ten_percent = max(1, n // 10)

    top_indices = np.argsort(expected_returns)[-n_ten_percent:]
    bottom_indices = np.argsort(expected_returns)[:n_ten_percent]

    #print(np.average(expected_returns[top_indices]), np.average(expected_returns[bottom_indices]))

    weights = np.zeros(n)
    weights[top_indices] = 1 / n_ten_percent
    weights[bottom_indices] = - 1 / n_ten_percent

    return weights, ___
