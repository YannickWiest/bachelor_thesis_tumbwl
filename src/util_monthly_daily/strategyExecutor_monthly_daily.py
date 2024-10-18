import numpy as np
import pandas as pd

from tqdm import tqdm

def __cut_out_window(current_iteration, price_data, stock_returns, rf_data, valid_matrix, vo_data, window_size, mv_data, i, vo_data_monthly):
    returns_window = stock_returns.iloc[current_iteration - window_size + 1:current_iteration + 1]
    price_data_window = price_data.iloc[current_iteration - window_size + 1:current_iteration + 1]
    valid_rf_data = rf_data[current_iteration - window_size + 1:current_iteration + 1]

    valid_start = valid_matrix.iloc[current_iteration - window_size]
    valid_end = valid_matrix.iloc[current_iteration]
    valid_stocks = valid_start & valid_end

    current_mv_data = mv_data.iloc[current_iteration]
    valid_mv_stocks = valid_matrix.iloc[current_iteration]

    average_my_values = current_mv_data
    valid_mv_values = average_my_values[valid_mv_stocks]

    mv_25_percentile = valid_mv_values.quantile(0.25)
    valid_mv_filter = valid_mv_values > mv_25_percentile
    previously_valid_stocks = valid_stocks.copy()

    valid_stocks = (valid_stocks & valid_mv_filter)

    excluded_stocks_by_mv = previously_valid_stocks & ~valid_stocks
    excluded_stocks_list = excluded_stocks_by_mv[excluded_stocks_by_mv].index.tolist()
    #print(valid_matrix.iloc[current_iteration]['EXENSE DEAD - 22/04/09'])
    #print("Excluded stocks by market value filter:", excluded_stocks_list)

    if window_size == 1250:
        size = 60
    elif window_size == 125:
        size = 6
    elif window_size == 40:
        size = 2
    else:
        size = 84

    volume_window_big = vo_data_monthly.iloc[i - size: i]
    valid_volume_big = volume_window_big.count(axis=0) >= int(size * 0.95)
    valid_stocks = valid_stocks & valid_volume_big


    valid_returns_window = returns_window.loc[:, valid_stocks]
    valid_price_data = price_data_window.loc[:, valid_stocks]

    return valid_stocks, valid_price_data, valid_returns_window, valid_rf_data

def __optimize_weights(current_iteration, price_data, stock_returns, rf_data, valid_matrix, vo_data, strategy, window_size, mv_data, old_weights, i, vo_data_monthly):
    valid_stocks, valid_price_data, valid_returns_window, valid_rf_data = (
        __cut_out_window(current_iteration, price_data, stock_returns, rf_data, valid_matrix, vo_data, window_size, mv_data, i, vo_data_monthly))


    valid_cov_matrix = valid_returns_window.cov()

    optimized_weights, old_weights = strategy(valid_price_data, valid_returns_window, valid_rf_data, old_weights)
    portfolio_variance = np.dot(optimized_weights, np.dot(valid_cov_matrix, optimized_weights))
    #full_weights = np.zeros(stock_returns.shape[1])

    full_weights = pd.Series(np.zeros(stock_returns.shape[1]), index=price_data.columns)

    full_weights[valid_stocks] = optimized_weights

    return full_weights, portfolio_variance, old_weights


def executeStrategy(price_data, stock_returns, valid_matrix, volume_data, rf_data, strategy, window_size, should_plot, frequency, start_year, sample, mv_data, stock_returns_data_monthly, rf_data_monthly, vo_data_monthly):
    monthly_returns = []
    turnovers = []
    currentPortfolio = []

    currentMonth = 0
    offset = 0
    old_weights = pd.Series([])
    i = 85

    print(stock_returns.index[window_size])

    for start in tqdm(range(window_size, len(stock_returns)), f"Sample: {sample}; Strategy: {strategy.name()}"):

        if stock_returns.index[start].year < start_year:
            # print('Start Year > ' + str(stock_returns.index[start]))
            offset += 1
            continue


        if start != len(stock_returns) - 1 and currentMonth == stock_returns.index[start].month:
            continue
        else:
            weights, variance, old_weights = __optimize_weights(start, price_data, stock_returns, rf_data, valid_matrix, volume_data, strategy.strategy, window_size, mv_data, old_weights, i, vo_data_monthly)
            currentMonth = stock_returns.index[start].month

        # Calculate profit from last iteration
            if len(currentPortfolio) != 0:
                currentReturns = currentPortfolio * stock_returns_data_monthly.iloc[i]

                monthlyReturn = np.sum(currentReturns)


                cash_before = 1 - np.sum(currentPortfolio)

                currentPortfolio += currentReturns

                norm_factor = abs(np.sum(currentPortfolio) + cash_before)
                cash_normed = cash_before / norm_factor

                # currentPortfolio /= np.sum(abs(currentPortfolio))
                currentPortfolio /= norm_factor
                cash_after = 1 - np.sum(weights)


                monthly_returns.append(monthlyReturn)

                turnovers.append(0.5 * np.sum(np.abs(weights - currentPortfolio)) + 0.5 * abs(cash_after - cash_normed))
                i += 1

            currentPortfolio = weights

    return sample, monthly_returns, rf_data_monthly, turnovers, should_plot, price_data.index[window_size + offset], window_size + offset, price_data.index[window_size + offset:], frequency
