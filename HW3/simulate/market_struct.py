__author__ = 'eric'


# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import numpy as np

# Third Party Imports
import datetime as dt


class MarketStructure(object):

    def __init__(self, order_input, starting_cash):
        self.order_input = order_input
        self.df_market_struct = None
        self.starting_cash = starting_cash
        self.init_data()

    def init_data(self):
        #date range of orders we are simulating.  The last day is already padded with an additional day
        dt_start, dt_end = self.order_input.get_date_range()

        #list of symbols we have orders for
        ls_symbols = self.order_input.get_symbol_list()

        # We need closing prices so the timestamp should be hours=16.
        dt_timeofday = dt.timedelta(hours=16)

        # Get a list of trading days between the start and the end.
        ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

        # Creating an object of the dataaccess class with Yahoo as the source.
        c_dataobj = da.DataAccess('Yahoo')

        # Keys to be read from the data, it is good to read everything in one go.
        ls_keys = ['close']

        # Reading the data, now d_data is a dictionary with the keys above.
        # Timestamps and symbols are the ones that were specified before.
        df_close_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)[0]

        #patch over any data problems
        df_close_data = df_close_data.fillna(method='ffill')
        df_close_data = df_close_data.fillna(method='bfill')
        df_close_data = df_close_data.fillna(1.0)

        self.df_market_struct = df_close_data.copy()
        i_df_length = len(self.df_market_struct)

        #copy the time index to a place where it is more easily accessible.
        #this is probably unnecessary (learn more pandas!)
        self.df_market_struct['dates'] = self.df_market_struct.index.copy()
        #populate the orders column
        self.df_market_struct['orders'] = self.df_market_struct['dates'].map(self.order_input.get_trades_for_date)
        #a dictionary representing 0 allocation to all of the trading symbols
        d_empty_allocation = dict(zip(ls_symbols, [0 for k in range(len(ls_symbols))]))
        #create series to store allocation of every trading day
        self.df_market_struct['positions'] = np.array([d_empty_allocation.copy() for k in range(i_df_length)])
        #create series to store available cash.  Start with the input cash, the rest of the values will be 0
        self.df_market_struct['available_cash'] = \
            np.array([self.starting_cash * 1.0] + [0.0 for k in range(i_df_length-1)])
        #create series to store the closing daily value, init to 0
        self.df_market_struct['closing_value'] = 0
