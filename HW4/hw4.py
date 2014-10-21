__author__ = 'eric'

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import os

orders_csv = None
f = None
dataObj = da.DataAccess('Yahoo')
print "Scratch Directory: ", dataObj.scratchdir


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if on 2 consecutive closes the price went from
            # greater than or equal to 5.00 to less than 5.00
            if f_symprice_yest >= 5.0 and f_symprice_today < 5.0:
                write_order(s_sym, ldt_timestamps[i])
                #df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


def write_order(symbol, tstamp):
    global f
    global orders_csv

    if f is None:
        f = open('{0:s}/{1:s}'.format(os.path.dirname(os.path.realpath(__file__)), orders_csv), 'w')

    f.write('{0:4d}, {1:02d}, {2:02d}, {3:s}, BUY, 100'.format(tstamp.year, tstamp.month, tstamp.day, symbol))
    five_days_later = dt.timedelta(days=5)
    close_tstamp = tstamp + five_days_later
    f.write('{0:4d}, {1:02d}, {2:02d}, {3:s}, SELL, 100'
            .format(close_tstamp.year, close_tstamp.month, close_tstamp.day, symbol))
    pass


def create_study(ls_symbols, ldt_timestamps, s_study_name):
    global dataObj, f

    print "Grabbing data to perform {0}".format(s_study_name)
    ls_keys = ['close', 'actual_close']
    ldf_data = dataObj.get_data(ldt_timestamps, ls_symbols, ls_keys)

    print "Got data for study {0}".format(s_study_name)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)
    if f is not None:
        f.close()

    #print "Creating Study"
    #ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
    #                 s_filename=s_study_name, b_market_neutral=True, b_errorbars=True,
    #                 s_market_sym='SPY')


def main():
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    global dataObj

    ls_symbols_2012 = dataObj.get_symbols_from_list('sp5002012')
    #ls_symbols_2012.append('SPY')

    create_study(ls_symbols_2012, ldt_timestamps, '2012Study2.pdf')
    print "Finished"

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate trading events based on the $5 event')
    parser.add_argument('orders_csv', help='(output) CSV file specifying dates of order execution')
    args = parser.parse_args()

    orders_csv = args.orders_csv
    main()