__author__ = 'eric'

import pandas as pd
import numpy as np
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import copy

data_obj = None
ldt_timestamps = None
ldf_data = None
d_data = None


def main(in_args):
    load_data(in_args.ls_symbols)
    if in_args.indicator == 'bbands':
        df_indicator = calc_bollinger_bands(in_args.ls_symbols)
    else:
        df_indicator = calc_macd(in_args.ls_symbols)

    output_result(df_indicator, in_args.ls_symbols)


def output_result(df_indicator, ls_symbols):
    header = '                   '
    for s_symbol in ls_symbols:
        header = header + '{:>11s}'.format(s_symbol)

    print header
    global ldt_timestamps
    s_date_format = "%Y-%m-%d %H:%M:%S"

    for i in xrange(0, len(ldt_timestamps)):
        row = '{0:s}'.format(df_indicator.index[i].strftime(s_date_format))
        for s_symbol in ls_symbols:
            row = row + '  {0:>9.6f}'.format(df_indicator[s_symbol].ix[i])
        print row


def calc_bollinger_bands(ls_symbols):
    df_close = d_data['close']
    print "Calculating Bollinger Bands"

    df_bbands = copy.deepcopy(df_close)
    df_bbands = df_bbands * np.NAN
    look_back = 20

    for s_sym in ls_symbols:
        df_mean = pd.rolling_mean(df_close[s_sym], window=look_back, min_periods=look_back)
        df_std = pd.rolling_std(df_close[s_sym], window=look_back, min_periods=look_back)
        df_bbands[s_sym] = (df_close[s_sym] - df_mean) / df_std

    return df_bbands


def calc_macd(ls_symbols):
    pass


def load_data(ls_symbols):
    global data_obj, ldt_timestamps, ldf_data, d_data

    data_obj = da.DataAccess('Yahoo')
    print "Scratch Directory: ", data_obj.scratchdir

    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    print "Grabbing data for {0}".format(ls_symbols)
    ls_keys = ['close']
    ldf_data = data_obj.get_data(ldt_timestamps, ls_symbols, ls_keys)

    print "Got data for {0}, scrubbing it".format(ls_symbols)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Calculate indicators fro a symbol over a given range of dates')
    parser.add_argument('indicator', help='one of (bbands, macd)')
    parser.add_argument('plot_file', help='(output) PDF showing the values of the indicator')
    parser.add_argument('-s', '--ls_symbols', nargs='*', help='equity symbols')

    args = parser.parse_args()

    main(args)