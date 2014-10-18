__author__ = 'eric'

from simulate.order_input import OrdersInput
from simulate.market_struct import MarketStructure


def simulate(df_market_struct, ls_symbols):
    num_trading_days = len(df_market_struct)
    #iterate over each trading day
    for day in xrange(num_trading_days):
        na_orders = df_market_struct['orders'][day]
        na_positions = df_market_struct['positions'][day]
        f_available_cash = df_market_struct['available_cash'][day]

        #update holdings for each day based on orders
        for order_dict in na_orders:
            a_trade = order_dict['trade']
            s_symbol = a_trade['symbol'][0]
            f_close_price = df_market_struct[s_symbol][day]
            i_current_position = na_positions[s_symbol]
            i_trade_volume = a_trade['volume'][0]
            f_trade_cost = i_trade_volume * f_close_price
            if a_trade['type'] == 'BUY':
                na_positions[s_symbol] = i_current_position + i_trade_volume
                f_available_cash = f_available_cash - f_trade_cost
            else:
                na_positions[s_symbol] = i_current_position - i_trade_volume
                f_available_cash = f_available_cash + f_trade_cost

        #set the cash available and overall position for the next trading day
        if day + 1 < num_trading_days:
            df_market_struct['available_cash'][day+1] = f_available_cash
            df_market_struct['positions'][day+1] = na_positions.copy()

        #update end of day portfolio value based on new position sizes
        f_daily_value = f_available_cash
        for s_symbol in ls_symbols:
            f_close_price = df_market_struct[s_symbol][day]
            i_position_size = df_market_struct['positions'][day][s_symbol]
            f_daily_value = f_daily_value + (f_close_price * i_position_size)

        df_market_struct['closing_value'][day] = f_daily_value
    pass


def output(values_file, df_market_struct):
    f = open(values_file, 'w')

    num_trading_days = len(df_market_struct)
    for day in xrange(num_trading_days):
        value = df_market_struct['closing_value'][day]
        timestamp = df_market_struct['dates'][day]
        f.write('{0:4d}, {1:2d}, {2:2d}, {3:7d}\n'
                .format(timestamp.year, timestamp.month, timestamp.day, int(round(value, 0))))
        pass

    f.close()


def main(input_args):
    import os
    orders_csv = '{0:s}/{1:s}'.format(os.path.dirname(os.path.realpath(__file__)), input_args.orders_csv)
    values_csv = '{0:s}/{1:s}'.format(os.path.dirname(os.path.realpath(__file__)), input_args.values_csv)
    order_input = OrdersInput(orders_csv)
    market_struct = MarketStructure(order_input, input_args.starting_cash)
    simulate(market_struct.df_market_struct, order_input.get_symbol_list())
    output(values_csv, market_struct.df_market_struct)
    print "Done"


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Simulate the market over a given time period')
    parser.add_argument('starting_cash', type=int, help='cash to start the trading period with')
    parser.add_argument('orders_csv', help='(input) CSV file specifying dates or order execution')
    parser.add_argument('values_csv', help='(output) CSV file specifying the daily value of the portfolio')

    args = parser.parse_args()

    main(args)