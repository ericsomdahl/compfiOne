__author__ = 'eric'

from port_input import PortfolioInput
import numpy as np
import matplotlib.pyplot as plt


def look_at(portfolio_input):
    i_trading_days = 252

    dt_start, dt_end = portfolio_input.get_start_end_dates()
    s_date_format = "%Y-%m-%d %H:%M:%S"

    na_benchmark_returns = portfolio_input.df_analysis_data['benchmark_returns']
    f_benchmark_stddev = np.std(na_benchmark_returns)
    f_benchmark_avg_daily_return = np.mean(na_benchmark_returns)
    f_benchmark_sharpe_ratio = (np.sqrt(i_trading_days) * f_benchmark_avg_daily_return) / f_benchmark_stddev

    na_portfolio_returns = portfolio_input.df_analysis_data['portfolio_returns']
    f_portfolio_stddev = np.std(na_portfolio_returns)
    f_portfolio_avg_daily_return = np.mean(na_portfolio_returns)
    f_portfolio_sharpe_ratio = (np.sqrt(i_trading_days) * f_portfolio_avg_daily_return) / f_portfolio_stddev

    na_benchmark_total_returns = portfolio_input.df_analysis_data['benchmark_normalized']
    f_benchmark_total_return = na_benchmark_total_returns[-1]
    na_portfolio_total_returns = portfolio_input.df_analysis_data['portfolio_normalized']
    f_portfolio_total_return = na_portfolio_total_returns[-1]

    # we only want to graph the cumulative returns
    plt.clf()
    fig = plt.figure()
    fig.add_subplot(111)
    plt.plot(portfolio_input.df_analysis_data['portfolio_values'])
    plt.plot(portfolio_input.df_analysis_data['benchmark_values'], alpha=0.4)
    ls_names = ['Portfolio', portfolio_input.symbol]
    plt.legend(ls_names)
    plt.ylabel('Cumulative Returns')
    plt.xlabel('Trading Day')
    fig.autofmt_xdate(rotation=45)
    plt.savefig('hw3.pdf', format='pdf')

    print "The final value of the portfolio using the sample file is -- {0:s}".format(portfolio_input.na_raw_input[0][-1])
    print "Details of the Performance of the portfolio :"
    print "Date Range: {0:s} to {1:s}".format(dt_start.strftime(s_date_format), dt_end.strftime(s_date_format))
    print "\nSharpe Ratio of Fund: {0:f}\nSharpe Ratio of {1:s}: {2:f}"\
        .format(f_portfolio_sharpe_ratio, portfolio_input.symbol, f_benchmark_sharpe_ratio)
    print "\nTotal Return of Fund: {0:f}\nTotal Return of {1:s}: {2:f}"\
        .format(f_portfolio_total_return, portfolio_input.symbol, f_benchmark_total_return)
    print "\nStandard Deviation of Fund: {0:f}\nStandard Deviation of {1:s}: {2:f}"\
        .format(f_portfolio_stddev, portfolio_input.symbol, f_benchmark_stddev)
    print "\nAverage Daily Return of Fund: {0:f}\nAverage Daily Return of {1:s}: {2:f}"\
        .format(f_portfolio_avg_daily_return, portfolio_input.symbol, f_benchmark_avg_daily_return)


def main(input_args):
    import os
    values_csv = '{0:s}/{1:s}'.format(os.path.dirname(os.path.realpath(__file__)), input_args.values_csv)
    portfolio_input = PortfolioInput(values_csv, input_args.benchmark)
    look_at(portfolio_input)
    pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Analyze a portfolios returns and compare it against a specified benchmark')
    parser.add_argument('values_csv', help='(input) CSV file specifying the daily value of the portfolio')
    parser.add_argument('benchmark', help='symbol of the benchmark to use in comparison')

    args = parser.parse_args()

    main(args)