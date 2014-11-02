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

f = None
dataObj = da.DataAccess('Yahoo')
print "Scratch Directory: ", dataObj.scratchdir


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['close']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    df_b_bands = calc_bollinger_bands(ls_symbols, d_data)

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    #last_possible_close_idx = len(ldt_timestamps) - 1
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_today_spy_band = df_b_bands['SPY'].ix[ldt_timestamps[i]]
            f_today_sym_band = df_b_bands[s_sym].ix[ldt_timestamps[i]]
            f_yest_sym_band = df_b_bands[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if today's band <= -2, prev day is >= -2 and SPY >=1
            if f_today_spy_band >= 1.0 and f_today_sym_band <= -2.0 and f_yest_sym_band >= -2.0:
                #close_idx = min((i+5), last_possible_close_idx)
                #write_order(s_sym, ldt_timestamps[i], ldt_timestamps[close_idx])
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


def create_study(ls_symbols, ldt_timestamps, s_study_name):
    global dataObj, f

    print "Grabbing data to perform {0}".format(s_study_name)
    ls_keys = ['close']
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

    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                     s_filename=s_study_name, b_market_neutral=True, b_errorbars=True,
                     s_market_sym='SPY')


def calc_bollinger_bands(ls_symbols, d_data):
    df_close = d_data['close']
    print "Calculating Bollinger Bands"

    df_bbands = copy.deepcopy(df_close)
    df_bbands = df_bbands * np.NAN
    i_look_back = 20

    for s_sym in ls_symbols:
        df_mean = pd.rolling_mean(df_close[s_sym], window=i_look_back, min_periods=i_look_back)
        df_std = pd.rolling_std(df_close[s_sym], window=i_look_back, min_periods=i_look_back)
        df_bbands[s_sym] = (df_close[s_sym] - df_mean) / df_std

    return df_bbands


def main():
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    global dataObj

    ls_symbols_2012 = dataObj.get_symbols_from_list('sp5002012')
    ls_symbols_2012.append('SPY')

    create_study(ls_symbols_2012, ldt_timestamps, '2012Study-BBand.pdf')
    print "Finished"

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate event study based on Bollinger Bands')
    #parser.add_argument('orders_csv', help='(output) CSV file specifying dates of order execution')
    args = parser.parse_args()

    #orders_csv = args.orders_csv
    main()