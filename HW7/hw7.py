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


def write_order(symbol, open_tstamp, close_tstamp, s_orders_csv):
    global f
    global orders_csv

    if f is None:
        f = open('{0:s}/{1:s}'.format(os.path.dirname(os.path.realpath(__file__)), s_orders_csv), 'w')

    f.write('\n{0:4d}, {1:02d}, {2:02d}, {3:s}, BUY, 100'
            .format(open_tstamp.year, open_tstamp.month, open_tstamp.day, symbol))
    f.write('\n{0:4d}, {1:02d}, {2:02d}, {3:s}, SELL, 100'
            .format(close_tstamp.year, close_tstamp.month, close_tstamp.day, symbol))


def find_bband_events(ls_symbols, d_data, s_orders_csv):
    ''' Finding the event dataframe '''
    df_close = d_data['close']

    print "Start Finding BBand Events"

    df_b_bands = calc_bollinger_bands(ls_symbols, d_data)

    print "Finished calculating BBand, Finding Events"
    # Time stamps for the event range
    ldt_timestamps = df_close.index
    last_possible_close_idx = len(ldt_timestamps) - 1
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_today_spy_band = df_b_bands['SPY'].ix[ldt_timestamps[i]]
            f_today_sym_band = df_b_bands[s_sym].ix[ldt_timestamps[i]]
            f_yest_sym_band = df_b_bands[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if today's band <= -2, prev day is >= -2 and SPY >=1
            if f_today_spy_band >= 1.0 and f_today_sym_band <= -2.0 and f_yest_sym_band >= -2.0:
                close_idx = min((i+5), last_possible_close_idx)
                write_order(s_sym, ldt_timestamps[i], ldt_timestamps[close_idx], s_orders_csv)


def find_macd_events(ls_symbols, d_data, s_orders_csv):
    ''' Finding the event dataframe '''
    df_close = d_data['close']

    print "Starting Finding MACD Events"
    df_macd = calc_macd(ls_symbols, d_data)

    print "Calculated MACD, Finding Events"
    # Time stamps for the event range
    ldt_timestamps = df_close.index
    last_possible_close_idx = len(ldt_timestamps) - 1
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_today_spy_macd = df_macd['SPY'].ix[ldt_timestamps[i]]
            f_today_sym_macd = df_macd[s_sym].ix[ldt_timestamps[i]]
            f_yest_sym_macd = df_macd[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if today's macd <= -2, prev day is >= -2 and SPY >=1
            if f_today_spy_macd >= 1.0 and f_today_sym_macd <= -2.0 and f_yest_sym_macd >= -2.0:
                close_idx = min((i+5), last_possible_close_idx)
                write_order(s_sym, ldt_timestamps[i], ldt_timestamps[close_idx], s_orders_csv)


def create_study(ls_symbols, ldt_timestamps, s_event, s_orders_csv):
    global dataObj, f

    print "Grabbing data to perform {0}".format(s_event)
    ls_keys = ['close']
    ldf_data = dataObj.get_data(ldt_timestamps, ls_symbols, ls_keys)

    print "Got data for study {0}".format(s_event)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    if s_event == 'bbands':
        find_bband_events(ls_symbols, d_data, s_orders_csv)
    else:
        find_macd_events(ls_symbols, d_data, s_orders_csv)
    if f is not None:
        f.close()


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


def calc_macd(ls_symbols, d_data):
    df_close = d_data['close']
    print "Calculating MACD"

    df_macd = copy.deepcopy(df_close)
    df_macd = df_macd * np.NAN
    i_long_period = 26
    i_short_period = 12
    i_signal_period = 9
    i_look_back = 20

    for s_sym in ls_symbols:
        df_long_mean = pd.ewma(df_close[s_sym], min_periods=i_long_period, span=12.5)
        df_short_mean = pd.ewma(df_close[s_sym], min_periods=i_short_period, span=5.5)
        df_macd_tmp = df_short_mean - df_long_mean
        df_signal = pd.ewma(df_macd_tmp, min_periods=i_signal_period, span=4)
        df_divergence = df_macd_tmp - df_signal
        df_divergence_std = pd.rolling_std(df_divergence, window=i_look_back, min_periods=i_look_back)
        df_macd[s_sym] = df_divergence / df_divergence_std

    return df_macd


def main(s_event, s_orders_csv):
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    global dataObj

    ls_symbols_2012 = dataObj.get_symbols_from_list('sp5002012')
    ls_symbols_2012.append('SPY')

    create_study(ls_symbols_2012, ldt_timestamps, s_event, s_orders_csv)
    print "Finished"


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate event study based on events')
    parser.add_argument('event', help='one of "bbands" or "macd"')
    parser.add_argument('orders_csv', help='(output) CSV file specifying dates of order execution')
    args = parser.parse_args()

    main(args.event, args.orders_csv)