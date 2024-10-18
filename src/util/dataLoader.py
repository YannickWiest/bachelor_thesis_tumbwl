import numpy as np
import pandas as pd


from util import validMatrixGenerator

def __open_csv(path):
    csv = pd.read_csv(path, delimiter=',', decimal='.', index_col='Name')
    csv.index = pd.to_datetime(csv.index, format='%d/%m/%Y')
    return csv.apply(pd.to_numeric, errors='coerce')


def __apply_dynamic_screens(stock_returns_data, ri_data, frequency):
    if frequency == 'daily':
        stock_returns_data[stock_returns_data > 2] = 0
        stock_returns_data[ri_data > 1_000_000] = 0

        shifted_data = stock_returns_data.shift(1)

        condition1 = (stock_returns_data >= 1.0) | (shifted_data >= 1.0)
        condition2 = ((1 + shifted_data) * (1 + stock_returns_data) - 1) < 0.2

        combined_condition = condition1 & condition2

        mask = combined_condition | combined_condition.shift(-1)
        stock_returns_data[mask] = 0


    elif frequency == 'monthly':
        stock_returns_data[stock_returns_data > 9.9] = 0
        stock_returns_data[ri_data > 1_000_000] = 0

        shifted_data = stock_returns_data.shift(1)

        condition1 = (stock_returns_data >= 3.0) | (shifted_data >= 3.0)
        condition2 = ((1 + shifted_data) * (1 + stock_returns_data) - 1) < 0.5

        combined_condition = condition1 & condition2

        mask = combined_condition | combined_condition.shift(-1)
        stock_returns_data[mask] = 0

    else:
        print(f"Invalid frequency: {frequency} | No dynamic screens available")


    return stock_returns_data


"""
Opens passed csv files.
Returns 6 pd frames: price_data, ri_data, stock_returns_data, vo_data, rf_data, valid_matrix
"""
def load(priceDataPath, marketValueDataPath, returnIndexDataPath, volumeDataPath, rfDataPath, frequency):
    price_data = __open_csv(priceDataPath)
    ri_data = __open_csv(returnIndexDataPath)
    vo_data = __open_csv(volumeDataPath)
    rf_data = __open_csv(rfDataPath)
    mv_data = __open_csv(marketValueDataPath)

    vo_data.dropna(how='all', inplace=True)
    common_index = vo_data.index
    price_data = price_data.loc[common_index]
    ri_data = ri_data.loc[common_index]
    rf_data = rf_data.loc[common_index].iloc[:, 0].to_numpy()


    columns_to_drop = ri_data.columns[ri_data.columns.str.contains('#ERROR')]
    indices_to_drop = [ri_data.columns.get_loc(col) for col in columns_to_drop]

    columns_to_drop = vo_data.columns[vo_data.columns.str.contains('#ERROR')]
    indices_to_drop += [vo_data.columns.get_loc(col) for col in columns_to_drop]

    columns_to_drop = mv_data.columns[mv_data.columns.str.contains('#ERROR')]
    indices_to_drop += [mv_data.columns.get_loc(col) for col in columns_to_drop]


    price_data.drop(price_data.columns[indices_to_drop], axis=1, inplace=True)
    ri_data.drop(ri_data.columns[indices_to_drop], axis=1, inplace=True)
    vo_data.drop(vo_data.columns[indices_to_drop], axis=1, inplace=True)
    mv_data.drop(mv_data.columns[indices_to_drop], axis=1, inplace=True)

    price_data.columns = price_data.columns.str.replace(' - TOT RETURN IND', '', regex=False)
    ri_data.columns = price_data.columns
    vo_data.columns = price_data.columns
    mv_data.columns = price_data.columns

    # Calculating stock returns
    stock_returns_data = ri_data.pct_change().fillna(0)
    stock_returns_data = __apply_dynamic_screens(stock_returns_data, ri_data, frequency)


    column_sums = np.sum(stock_returns_data, axis=0)
    non_zero_columns = column_sums[column_sums != 0].index
    price_data = price_data[non_zero_columns]
    ri_data = ri_data[non_zero_columns]
    stock_returns_data = stock_returns_data[non_zero_columns]
    vo_data = vo_data[non_zero_columns]
    mv_data = mv_data[non_zero_columns]

    valid_matrix = validMatrixGenerator.createValidMatrix(ri_data)

    if 'daily' in frequency:
        rf_data = (1 + rf_data / 100) ** (1 / 256) - 1
    else:
        rf_data = (1 + rf_data / 100) ** (1 / 12) - 1

    return price_data, ri_data, stock_returns_data, vo_data, rf_data, mv_data, valid_matrix
