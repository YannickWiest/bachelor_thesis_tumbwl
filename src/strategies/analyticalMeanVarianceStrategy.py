import numpy as np

def name():
    return 'meanVariance Strategy'

def strategy(_, valid_returns_window, risk_free_rates, __):
    valid_cov_matrix = valid_returns_window.cov()
    expected_returns = np.mean(valid_returns_window, axis=0).values
    expected_returns -= risk_free_rates[-1]

    inv_valid_cov_matrix = np.linalg.inv(valid_cov_matrix)

    numerator = np.dot(inv_valid_cov_matrix, expected_returns)
    one_vector = np.ones(len(expected_returns))
    denominator = np.dot(valid_cov_matrix, one_vector)
    w = numerator / denominator


    return w, __


