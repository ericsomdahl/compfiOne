__author__ = 'eric'

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

import numpy as np
import datetime as dt


class PortfolioInput(object):
    def __init__(self, csv_file, symbol):
        self.csv_file = csv_file
        self.symbol = symbol
        self.df_portfolio = None
        self.na_raw_input = None
        self.ldt_timestamps = None
        self.df_analysis_data = None
        self.internal_init()

    def internal_init(self):

        input_types = {'names': ('year', 'month', 'day', 'value'), 'formats': ('u4', 'u4', 'u4', 'f8')}

        self.na_raw_input = np.loadtxt(self.csv_file, dtype=input_types, delimiter=',', skiprows=0)
        self.na_raw_input = np.reshape(self.na_raw_input, (1, -1))

        dt_start, dt_end = self.get_date_range()

        #list of symbols we have orders for
        ls_symbols = [self.symbol]

        # We need closing prices so the timestamp should be hours=16.
        dt_timeofday = dt.timedelta(hours=16)

        # Get a list of trading days between the start and the end.
        self.ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

        # Creating an object of the dataaccess class with Yahoo as the source.
        c_dataobj = da.DataAccess('Yahoo')

        # Keys to be read from the data, it is good to read everything in one go.
        ls_keys = ['close']

        # Reading the data, now d_data is a dictionary with the keys above.
        # Timestamps and symbols are the ones that were specified before.
        self.df_analysis_data = c_dataobj.get_data(self.ldt_timestamps, ls_symbols, ls_keys)[0]

        #patch over any data problems
        self.df_analysis_data = self.df_analysis_data.fillna(method='ffill')
        self.df_analysis_data = self.df_analysis_data.fillna(method='bfill')
        self.df_analysis_data = self.df_analysis_data.fillna(1.0)

        # Getting the numpy ndarray of close prices.
        na_benchmark_price = self.df_analysis_data[self.symbol].values

        # Normalizing the prices to start at 1 and see relative returns
        na_benchmark_normalized_price = na_benchmark_price / na_benchmark_price[0]

        self.df_analysis_data['benchmark_normalized'] = na_benchmark_normalized_price
        na_benchmark_returns = na_benchmark_normalized_price.copy()
        tsu.returnize0(na_benchmark_returns)
        self.df_analysis_data['benchmark_returns'] = na_benchmark_returns

        f_get_value = lambda x: x[0][3]
        na_portfolio_values = np.apply_along_axis(f_get_value, 0, self.na_raw_input)

        #so we can calculate the cumulative performance of the benchmark
        #number of shares of the benchmark we'd have if we dumped all of our money
        #into it
        f_benchmark_shares = na_portfolio_values[0] / na_benchmark_price[0]

        self.df_analysis_data['benchmark_values'] = na_benchmark_price * f_benchmark_shares
        self.df_analysis_data['portfolio_values'] = na_portfolio_values
        na_portfolio_normalized = na_portfolio_values / na_portfolio_values[0]

        self.df_analysis_data['portfolio_normalized'] = na_portfolio_normalized
        na_portfolio_returns = na_portfolio_normalized.copy()
        tsu.returnize0(na_portfolio_returns)
        self.df_analysis_data['portfolio_returns'] = na_portfolio_returns

    def get_date_range(self):
        #pad the date range on the end so that it goes past the closing time on the last day of trading
        return self.get_raw_as_timestamp(0), self.get_raw_as_timestamp(-1) + dt.timedelta(days=1)

    def get_raw_as_timestamp(self, idx):
        val = self.na_raw_input[0][idx]
        return dt.datetime(val[0], val[1], val[2])

    def get_start_end_dates(self):
        return self.ldt_timestamps[0], self.ldt_timestamps[-1]