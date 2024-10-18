import util.dataLoader as dataLoader
import util.strategyExecutor as strategyExecutor

from strategies import constrainedMeanVarianceStrategy, minimumVarianceStrategy, oneOverNStrategy, momentumStrategy, \
    bollingerBandStrategy, meanVarianceStrategy, constrainedMinimumVarianceStrategy, analyticalMeanVarianceStrategy
from util import statsPrinterCombined

start_year = 2010

#######################################
# Toggle samples that should be evaluated
# This file will use monthly data with monthly rebalancing and daily data with daily rebalancing.
# The combination of daily data monthly rebalancing is done by main_monthly_daily.py
# Important: P-Values only will be correct if one sample is exclusively selected.
samples = {
    "monthly/Combined": True,
    "monthly/Norway": True,
    "monthly/Belgium": True,
    "daily/Combined": True,
    "daily/Norway": True,
    "daily/Belgium": True
}
#######################################


#######################################
# Configure evaluation frequencies. 
# Monthly estimation window is used for all samples starting with monthly.
# Daily estimation window is used for all samples starting with daily.
monthly_estimation_window = 84
daily_estimation_window = 40
#######################################

strategies = {
    oneOverNStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},

    minimumVarianceStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},
    meanVarianceStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},


    constrainedMinimumVarianceStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},
    constrainedMeanVarianceStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},

    momentumStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},

    bollingerBandStrategy: {'monthly': (monthly_estimation_window, False), 'daily': (daily_estimation_window, False)},

}

results = []

for strategy, d in strategies.items():

    print("---------------------------------")
    print(f"Executing {strategy.name()}.")
    print("---------------------------------")

    strategy_result = []
    for sample, should_evaluate in samples.items():
        if should_evaluate:
            frequency = 'monthly'
            if 'daily' in sample:
                frequency = 'daily'

            price_data, ri_data, stock_returns_data, vo_data, rf_data, mv_data, valid_matrix = dataLoader.load(
                f'data/{sample}/RIData_{sample.replace("/", "")}.csv',
                f'data/{sample}/MVData_{sample.replace("/", "")}.csv',
                f'data/{sample}/RIData_{sample.replace("/", "")}.csv',
                f'data/{sample}/VOData_{sample.replace("/", "")}.csv',
                #f'data/{sample}/RFData_{sample.replace("/", "")}.csv', frequency)
                f'data/{sample}/RFData_{sample.replace("/", "")}.csv', frequency)


            window_size, should_plot = d[frequency]
            result = strategyExecutor.executeStrategy(ri_data, stock_returns_data, valid_matrix, vo_data, rf_data,
                                                      strategy, window_size, should_plot, frequency, start_year, sample, mv_data)

            strategy_result.append(result)

    results.append((strategy.name(), strategy_result))

statsPrinterCombined.printStats(results)
