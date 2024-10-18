import numpy as np
import pandas as pd


def name():
    return 'bol'


def strategy(valid_price_data_window, _, __, old_weights):

    num_std_dev = 2  # number of standard deviations for the bands

    num_stocks = valid_price_data_window.shape[1]


    weights = pd.Series(np.zeros(num_stocks), index=valid_price_data_window.columns)
    for col in old_weights.index:
        if col in weights:
            if old_weights[col] < 0:
                weights[col] = -1
            elif old_weights[col] > 0:
                weights[col] = 1

    # Calculate Bollinger Bands for each stock
    for col in weights.index:

        stock_price_data = valid_price_data_window[col]

        # Calculate the moving average
        sma = np.mean(stock_price_data)

        # Calculate the standard deviation
        std_dev = np.std(stock_price_data)

        # Calculate the upper and lower Bollinger Bands
        upper_band = sma + num_std_dev * std_dev
        lower_band = sma - num_std_dev * std_dev



        # Implement a simple strategy:
        # Buy if the current price is below the lower band
        # Sell if the current price is above the upper band
        lastPrice = stock_price_data.iloc[-2]
        current_price = stock_price_data.iloc[-1]

        if current_price < lower_band:
            weights[col] = 1  # Buy signal
        elif current_price > upper_band:
            weights[col] = -1  # Sell signal
        else:
            if weights[col] < 0 and current_price > sma:
                weights[col] = 0  # Hold/No action
            elif weights[col] > 0 and current_price < sma:
                weights[col] = 0


    if np.sum(abs(weights)) > 0:
        weights /= np.sum(abs(weights))
    return weights.values, weights
