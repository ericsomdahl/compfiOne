__author__ = 'eric'

import numpy as np
import datetime as dt


def convert_to_datetime_ordinal(na_in):
    dt_in = dt.datetime(na_in['year'], na_in['month'], na_in['day'])
    return dt_in.toordinal()


def markup_with_datetime_ordinal(na_in):
    dt_in = dt.datetime(na_in['year'], na_in['month'], na_in['day'])
    return {'ordinal': dt_in.toordinal(), 'trade': na_in}


class OrdersInput(object):
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.na_raw_orders = None
        self.na_trade_dates = None
        self.na_symbols = None
        self.na_marked_trades = None
        self.internal_init()

    def internal_init(self):
        p_string_cleanup = lambda s: s.strip().upper()

        order_type = {'names': ('year', 'month', 'day', 'symbol', 'type', 'volume'),
                      'formats': ('u4', 'u4', 'u4', 'S10', 'S4', 'u4')}

        #read in the raw data
        self.na_raw_orders = np.loadtxt(self.csv_file, dtype=order_type, delimiter=',', skiprows=0,
                                        converters={3: p_string_cleanup, 4: p_string_cleanup})
        #convert to a 1xN array, so a single row per order
        self.na_raw_orders = np.reshape(self.na_raw_orders, (1, -1))
        #create an array of all of the dates on which trades take place
        self.na_trade_dates = np.apply_along_axis(convert_to_datetime_ordinal, 0, self.na_raw_orders)
        self.na_trade_dates.sort()

        #create an array of all of the symbols.  There will be repeats
        self.na_symbols = self.na_raw_orders['symbol']
        #remove dupes
        self.na_symbols = np.unique(self.na_symbols)

        #find all of the orders that occur on the given date
        #first add date ordinals to all of the trades
        na_marked_trades = np.apply_along_axis(markup_with_datetime_ordinal, 0, self.na_raw_orders)
        self.na_marked_trades = na_marked_trades[0].flatten()

    def get_date_range(self):
        #we are already sorted so the first element is the earliest, last is greatest
        dt_start = dt.datetime.fromordinal(self.na_trade_dates[0])
        dt_end = dt.datetime.fromordinal(self.na_trade_dates[-1])
        #add a day to the end to allow the simulate to run for at least a day against the last trade
        dt_end = dt_end + dt.timedelta(days=1)
        return dt_start, dt_end

    def get_trade_dates(self):
        ldt_trade_dates = []
        for an_ordinal in self.na_trade_dates:
            ldt_trade_dates.append(dt.datetime.fromordinal(an_ordinal))
        return ldt_trade_dates

    def get_trades_for_date(self, dt_trade):
        #the CSV only specifies the day of the trade so hack the
        #time elements off of the incoming timestamp value
        d_trade = dt_trade.replace(hour=0).replace(minute=0)
        i_ordinal = d_trade.toordinal()
        p_date_filter = lambda x: True if x['ordinal'] == i_ordinal else False

        #filter orders based on the date entered
        na_temp = np.array(filter(p_date_filter, self.na_marked_trades))
        return na_temp

    def get_symbol_list(self):
        return  self.na_symbols.copy()