# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 04:22:35 2020

@author: yello
"""

class Trade:
    def __init__(self, position_dict, name, date,
                 strategy_exit=lambda date, data:None, 
                 strategy_takeprofit=lambda date, data:None, 
                 strategy_stoploss=lambda date, data:None):
        '''
        Args:
            position_dict: units of each asset, dict
            name: name of strategy, in purpose of no duplicate
            date: current date, the date of the trade
            strategy_exit: func
            strategy_takeprofit: func
            strategy_stoploss: func
        '''
        self.position = position_dict
        self.name = name # strategy name
        self.current_status = 'In Use'
        self.status_hist = {date: 'In Use'}
        # strategies
        self.exit_strategy = strategy_exit
        self.take_profit_strategy = strategy_takeprofit
        self.stop_loss_strategy = strategy_stoploss
        
    def status_update(self, date, data):
        exits = self.exit_strategy(date, data)
        if exits:
            self.current_status = 'Exit'
            self.status_hist[date] = self.current_status
        
        takeprofits = self.take_profit_strategy(date, data)
        if takeprofits:
            self.current_status = 'Take Profit'
            self.status_hist[date] = self.current_status
        
        stoploss = self.stop_loss_strategy(date, data)
        if stoploss:
            self.current_status = 'Stop Loss'
            self.status_hist[date] = self.current_status
    
if __name__ == '__main__':
    from backtest_data import Data
    # generate universe
    a1 = 'ACN'
    a2 = 'ADBE'
    universe = [a1, a2]
    data = Data(universe)
    # temp yr 2014-2016 stable relationship
    data0 = data.get_rolling('2016-06-01', universe, 500, shift_back=0)
    ratio = data0[a1]/data0[a2]
    ratio.plot()
    # data for check
    rolling_window = 100
    day1 = '2015-01-05'
    data1 = data.get_rolling(day1, universe, rolling_window, shift_back=0)
    day2 = '2018-01-05'
    data2 = data.get_rolling(day2, universe, rolling_window, shift_back=0)

    def sample_exit(date, data, threshold = 1.5):
        long = data[a1]
        short = data[a2]
        ratio = short/long
        std = ratio.std()
        avg = ratio.mean()
        Z = (ratio[-1] - avg)/std
        return abs(Z) <= threshold
    sample_exit(None, data1)
    
    # generate trade
    pair_exit = lambda date, data: sample_exit(date, data, 2)
    day1 = '2015-01-12'
    pair = Trade(
            position_dict = {a1:10, a2: -5}, 
            name = 'pairs:+ACN-AMD', 
            date = day1, 
            strategy_exit = pair_exit)
    pair.current_status
    
    # update trade
    day2 = '2015-03-24'
    data2 = data.get_rolling(day2, universe, rolling_window, shift_back=0)
    pair.status_update(day2, data2)
    pair.current_status
    pair.status_hist
