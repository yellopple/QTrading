# Backtest on Pairs Trading

We built a simple backtest class to track each trade individually, with each trade can have its own exit strategy, instead of using timely rebalance to achieve position closing-out.

## Structure

The backtest is constructed by

* Backtest class, which evaluated portfolio value, strategy performance, rebalancing, etc. Strategy function is inputed in Backtest instance.
* Trade class, which includes exit strategy, trade performance, etc.
* Wallet class, part of Backtest class, which counts value and holds portfolio positions within Backtest.
* strategy function, it's a function runs in Backtest to generate Trades timely.
* exit/stoploss/takeprofit function, it's part of Trade.

Steps to run backtest:
1. define strategy, 
   * let's say long 1 unit for single stock MA(10) up cross MA(5)
   * return a Trade which includes below exit strategy
2. define exit strategy for above strategy, let's say underlying stock MA(10) down cross MA(5)
3. Throw strategy function into Backtest, run monthly
4. What happens:
   1. In May, enter Trade1, Trade2 for 2 different stocks
   2. In June, signal says enter Trade1 again, but since current Trade1 hasn't closed out yet, therefore will not execute the Trade this month.
   3. In end of June, signal says exit strategy for Trade1 and Trade2, then close out both position.
