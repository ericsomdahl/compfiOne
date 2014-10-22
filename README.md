compfiOne
=========

## Computational Finance Part I -- Georgia Tech/Coursera

Here are the bits of my homework -- no copying!! :)

Link to the course: https://www.coursera.org/course/compinvesting1

All of these depend on having the Quant Software ToolKit install (http://wiki.quantsoftware.org/index.php?title=QuantSoftware_ToolKit)

We are building a tool-chain that looks at the stock market for
  * certain events in the price history of an equity
  * operationalize the events by ouputting a list of trades
  * simulate the outcomes of the trades by backtesting
  * analyze the outcome of the event-trading strategy by comparing to $SPX performace

###HW1
HW1 is a brute-force portfolio optimizer.  Given an arbitrary list of equities, it finds a set of allocations that maximizes Sharpe Ratio.  It only considers long positions.

###HW2
HW2 performs event studies.  It is currently looking for instances of equities crossing below the $5 at the close of trading.  It then outputs a PDF sudy showing the average price change and standard deviation of the next few trading days

###HW3
HW3 comes in two parts, a market simulator/backtester, and a performance analyzer.

####Sim
The simulator takes as input a CSV file specifying trades to be executed.  It assumes executing the orders at adjusted closing price for a trading day.  It outputs a CSV that lists the daily closing value of assets held in the portfolio.

####Analyzer
The Analyzer takes the Sim output and compares it against a specified benchmark.  It looks at Sharpe Ratio and risk (standard deviation of returns), Average daily returns, and total return.

###HW4
HW4 is derived from HW2.  It performs the same event study analysis as HW2 but instead of creating the event study, it outputs a CSV file of trades that can be fed into the HW3 Sim/Analyzer chain.


