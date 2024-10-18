import cvxpy as cp


def name():
    return 'c-min'

def strategy(_, valid_returns_window, __, ___):

    valid_cov_matrix = valid_returns_window.cov()
    n = valid_cov_matrix.shape[0]

    w = cp.Variable(n)
    x = cp.Variable(n, boolean=True)

    psd_cov_matrix = cp.psd_wrap(valid_cov_matrix.values)
    portfolio_variance = cp.quad_form(w, psd_cov_matrix)

    M = 1_000_000
    constraints = [
        cp.sum(w) == 1,  # Weights sum to 1
        #cp.norm(w, 1) <= 5,
        w >= 0,
        #cp.sum(x) >= 10,
        #w <= M * x
    ]


    problem = cp.Problem(cp.Minimize(portfolio_variance), constraints)
    problem.solve(solver=cp.GUROBI, MIPGap=1e-9)
    return w.value, ___
