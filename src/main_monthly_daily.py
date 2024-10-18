import util_monthly_daily.dataLoader_monthly_daily as dataLoader
import util_monthly_daily.strategyExecutor_monthly_daily as strategyExecutor

from strategies import constrainedMeanVarianceStrategy, minimumVarianceStrategy, oneOverNStrategy, momentumStrategy, \
    bollingerBandStrategy, meanVarianceStrategy, constrainedMinimumVarianceStrategy, analyticalMeanVarianceStrategy
from util_monthly_daily import statsPrinterCombined_monthly_daily as statsPrinterCombined

start_year = 2010

#######################################
# Toggle samples that should be evaluated
# This is daily data with monthly rebalancing.
samples = {
    "daily/Combined": True,
    "daily/Norway": True,
    "daily/Belgium": True
}
#######################################

#######################################
# Configure evaluation frequency.
# Daily estimation window is used for all samples starting with daily.
daily_estimation_window = 1250
#######################################


monthly_estimation_window = -1
strategies = {
    oneOverNStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, True)},

    minimumVarianceStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},
    meanVarianceStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},

    constrainedMinimumVarianceStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},
    constrainedMeanVarianceStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},

    momentumStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},

    bollingerBandStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},
}

results = []

for strategy, _ in strategies.items():

    print("---------------------------------")
    print(f"Executing {strategy.name()}.")
    print("---------------------------------")

    strategy_result = []
    for sample, should_evaluate in samples.items():
        if should_evaluate:
            frequency = 'monthly'
            if 'daily' in sample:
                frequency = 'daily'

            price_data, ri_data, stock_returns_data, vo_data, rf_data, mv_data, valid_matrix, stock_returns_data_monthly, rf_data_monthly, vo_data_monthly = dataLoader.load(
                f'data/{sample}/RIData_{sample.replace("/", "")}.csv',
                f'data/{sample}/MVData_{sample.replace("/", "")}.csv',
                f'data/{sample}/RIData_{sample.replace("/", "")}.csv',
                f'data/{sample}/VOData_{sample.replace("/", "")}.csv',
                #f'data/{sample}/RFData_{sample.replace("/", "")}.csv', frequency)
                f'data/{sample}/RFData_{sample.replace("/", "")}.csv', frequency,
                f'data/{sample.replace("daily", "monthly")}/RIData_{sample.replace("/", "").replace("daily", "monthly")}.csv',
                f'data/{sample.replace("daily", "monthly")}/RFData_{sample.replace("/", "").replace("daily", "monthly")}.csv',
                f'data/{sample.replace("daily", "monthly")}/VOData_{sample.replace("/", "").replace("daily", "monthly")}.csv',

            )

            should_plot = False
            window_size = daily_estimation_window

            result = strategyExecutor.executeStrategy(ri_data, stock_returns_data, valid_matrix, vo_data, rf_data,
                                                      strategy, window_size, should_plot, frequency, start_year, sample, mv_data, stock_returns_data_monthly, rf_data_monthly, vo_data_monthly)

            strategy_result.append(result)

    results.append((strategy.name(), strategy_result))

statsPrinterCombined.printStats(results)
