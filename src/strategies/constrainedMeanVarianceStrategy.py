import cvxpy as cp
import numpy as np

def name():
    return 'c-mv'

def strategy(_, valid_returns_window, risk_free_rates, ___):
    valid_cov_matrix = valid_returns_window.cov()
    expected_returns = np.mean(valid_returns_window, axis=0).values
    expected_returns -= risk_free_rates[-1]
    n = valid_cov_matrix.shape[0]

    if n == 0:
        return []

    w = cp.Variable(n)
    x = cp.Variable(n, boolean=True)

    psd_cov_matrix = cp.psd_wrap(valid_cov_matrix.values)
    portfolio_variance = cp.quad_form(w, psd_cov_matrix)
    portfolio_return = expected_returns @ w

    M = 1_000_000
    constraints = [
        cp.sum(w) == 1,  # Weights sum to 1
        #cp.norm(w, 1) <= 5,
        w >= 0,
        #cp.sum(x) >= 10,
        #w <= M * x
    ]
    gamma = 0.5  # gamma / 2
    problem = cp.Problem(cp.Maximize(portfolio_return - gamma * portfolio_variance), constraints)
    problem.solve(solver=cp.GUROBI, MIPGap=1e-9)
    return w.value, ___


