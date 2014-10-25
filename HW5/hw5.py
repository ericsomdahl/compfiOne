__author__ = 'eric'

import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
import datetime as dt

data_obj = None
ldt_timestamps = None
ldf_data = None
d_data = None

def main(in_args):
    load_data(in_args.symbol)
    pass


def load_data(symbol):
    global data_obj, ldt_timestamps, ldf_data, d_data

    data_obj = da.DataAccess('Yahoo')
    print "Scratch Directory: ", data_obj.scratchdir

    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    print "Grabbing data for {0}".format(symbol)
    ls_keys = ['close']
    ldf_data = data_obj.get_data(ldt_timestamps, [symbol], ls_keys)

    print "Got data for {0}, scrubbing it".format(symbol)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    pass


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Calculate indicators fro a symbol over a given range of dates')
    parser.add_argument('symbol', help='equity symbol')
    parser.add_argument('indicator', help='one of (bbands, macd)')
    parser.add_argument('plot_file', help='(output) PDF showing the values of the indicator')

    args = parser.parse_args()

    main(args)