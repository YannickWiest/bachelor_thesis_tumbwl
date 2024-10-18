import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import stats
from tabulate import tabulate


def accumulate_daily_to_monthly_returns(daily_returns, data_index):
    data_index = pd.to_datetime(data_index[1:])
    returns_df = pd.DataFrame({'returns': daily_returns}, index=data_index)

    monthly_returns = returns_df['returns'].resample('ME').apply(lambda x: (1 + x).prod() - 1)

    return monthly_returns


def accumulate_daily_to_monthly_turnover(daily_turnover, data_index):
    data_index = pd.to_datetime(data_index[1:])
    turnover_df = pd.DataFrame({'turnover': daily_turnover}, index=data_index)

    monthly_turnover = turnover_df['turnover'].resample('ME').sum()

    return monthly_turnover


def generate_month_range(start_year):
    start_date = f"{start_year}-01-01"
    end_date = "2023-12-01"

    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    dates = dates.append(pd.to_datetime(['2023-12-29']))
    return dates


def printStats(results):

    data_to_plot = []

    n_excess = None
    n_mean = None
    n_std = None

    for strategyName, result in results:
        result_rows = []
        for params in result:
            sample, returns, rf_data, turnovers, shouldPlot, startYear, window_size, data_index, frequency = params
            rf_data = rf_data[window_size:-1]

            excessReturns = returns - rf_data

            if frequency == 'daily':
                monthly_returns = list(accumulate_daily_to_monthly_returns(returns, data_index))
                excessReturns = accumulate_daily_to_monthly_returns(excessReturns, data_index)
                turnovers = accumulate_daily_to_monthly_turnover(turnovers, data_index)
            else:
                monthly_returns = returns

            portfolioReturn = np.prod(np.array(monthly_returns) + 1) * 100 - 100  # Calculate portfolio return

            monthEndValue = np.zeros(len(monthly_returns) + 1)
            monthEndValue[0] = 100
            negativeIndex = -1
            for i in range(len(monthly_returns)):
                monthEndValue[i + 1] = monthEndValue[i] * (1 + monthly_returns[i])
                if monthEndValue[i] < 0:
                    negativeIndex = i
                    break
            if negativeIndex != -1:
                monthEndValue[negativeIndex:] = 0
                portfolioReturn = -100
            else:
                data_to_plot.append((strategyName, monthEndValue))

            if shouldPlot:
                #date_range = data_index
                date_range = generate_month_range(startYear.year)

                plt.figure(figsize=(10, 5))
                plt.plot(date_range, monthEndValue)
                plt.title(strategyName)  # Set the title of the plot to the strategy name
                plt.xlabel('Date')
                plt.ylabel('Portfolio Value')
                plt.grid(True)
                plt.show()

            p_value = -1
            if strategyName == '1/N':
                n_excess = excessReturns
                n_mean = np.mean(excessReturns)
                n_var = np.var(excessReturns)
                n_std = np.std(excessReturns)
            else:
                if n_excess is not None:
                    i_std = np.std(excessReturns)
                    i_mean = np.mean(excessReturns)
                    i_var = np.var(excessReturns)

                    cov = np.cov(excessReturns, n_excess)[0, 1]


                    term1 = 2 * i_var * n_var
                    term2 = -2 * i_std * n_std * cov
                    term3 = 0.5 * (i_mean ** 2) * n_var
                    term4 = 0.5 * (n_mean ** 2) * i_var
                    term5 = -((i_mean * n_mean) / (i_std * n_std)) * (cov ** 2)

                    ratio = (term1 + term2 + term3 + term4 + term5) / 168

                    z = ((i_mean * n_std) - (n_mean * i_std)) / np.sqrt(ratio)

                    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

            max_uptrend = np.nanmax(monthly_returns) * 100
            max_downtrend = np.nanmin(monthly_returns) * 100
            mean_return = np.nanmean(monthly_returns) * 100
            median_return = np.nanmedian(monthly_returns) * 100
            variance = np.nanvar(monthly_returns)
            std_deviation = np.nanstd(monthly_returns)
            sharpe_ratio = np.nanmean(excessReturns) / np.nanstd(excessReturns)
            annualized_return = ((1 + portfolioReturn / 100) ** (1 / (2024 - startYear.year)) - 1) * 100
            ceq = np.nanmean(excessReturns) - 0.5 * np.nanvar(excessReturns)
            mean_turnover = np.mean(turnovers)

            winning_trades = sum(1 for ret in monthly_returns if ret >= 0)
            winning_percentage = (winning_trades / len(monthly_returns)) * 100

            result_rows.append({
                strategyName: sample,
                #"Max Uptrend (%)": f"{max_uptrend:.2f}%",
                #"Max Downtrend (%)": f"{max_downtrend:.2f}%",
                # "Mean Return (%)": f"{mean_return:.2f}%",
                "Winning Trades (%)": f"{winning_percentage:.2f}%",
                # "Median Return (%)": f"{median_return:.2f}%",
                # "Variance": variance,
                # "Standard Deviation": std_deviation,
                "Sharpe Ratio": round(sharpe_ratio, 4),
                "CEQ": round(ceq, 4),
                "P-Value": round(p_value, 2),
                "Total Return (%)": f"{portfolioReturn:.2f}%",
                "Annualized Return (%)": f"{annualized_return:.2f}%",
                "Mean Turnover (%)": f"{mean_turnover:.4f}"

            })

        # Convert result_rows to DataFrame and print
        results_df = pd.DataFrame(result_rows)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        pd.set_option('display.float_format', '{:.2f}'.format)

        table_str = tabulate(results_df, headers='keys', tablefmt='grid', showindex=False)
        print(table_str)
        print()

    if False:
        color_dict = {}
        colors = plt.cm.tab10.colors
        # Plot
        date_range = generate_month_range(2010)
        plt.figure(figsize=(10, 5))
        for idx, (name, result_array) in enumerate(data_to_plot):
            if name not in color_dict:
                color_dict[name] = colors[len(color_dict) % len(colors)]  # Assign a new color if not already assigned
            plt.plot(date_range, result_array, label=name if name not in color_dict.values() else "",
                     color=color_dict[name])
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value')
        plt.grid(True)
        plt.legend()
        plt.savefig(f"plots/monthly_combined_returns_84.png", bbox_inches='tight')
