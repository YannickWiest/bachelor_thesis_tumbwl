import time

import pandas as pd


def is_valid(stock_name, index):
    date_str = stock_name[-8:]
    stock_date = pd.to_datetime(date_str, format='%d/%m/%y', errors='coerce')
    if pd.isna(stock_date):
        return True
    return stock_date >= index

def createValidMatrix(stockData: pd.DataFrame):
    validMatrix = stockData.notna()
    stock_dates_str = [col[-8:] for col in stockData.columns]
    stock_dates = pd.to_datetime(stock_dates_str, format='%d/%m/%y', errors='coerce')
    for col, stock_date in zip(stockData.columns, stock_dates):
        if pd.isna(stock_date):
            continue
        validMatrix[col] = validMatrix[col] & (stockData.index <= stock_date)

    true_count = validMatrix.values.sum()
    total_elements = validMatrix.size
    percentage_true = (true_count / total_elements) * 100
    #print(f"Percentage of valid stock returns in the dataframe: {percentage_true:.2f}%")
    time.sleep(0.1)

    return validMatrix
