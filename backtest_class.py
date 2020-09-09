# -*- coding: utf-8 -*-
"""

self define function: get_position(data) -> target position, (dict){'asset name':position}
data is object for getting data relevant info

Created on Thu Sep  3 14:28:14 2020

@author: yello

增加
评价指标函数
仓位统计(目前使用存量统计，为了效能，可以考虑统计增量)
stoploss
"""

from wallet import Wallet

def reshuffle_dates(freq, all_dates):
    '''reshuffle dates according to frequency requirements
    '''
    assert freq in ['m','M','monthly','daily','D'], 'freq should be "M" or "D".'
    if freq in  ['daily','D']:
        return all_dates
    elif freq in ['m','M','monthly']:
        dates = [all_dates[0]]
        for i in all_dates:
            if i[:7] != dates[-1][:7]:
                dates.append(i)
        return dates

class Backtest:
    def __init__(self, start_new_trades, data, universe, look_back_period=80):
        '''
        args:
            start_new_trades: a function for getting trades, must return a list of trades
            data: Data object
            universe: a list of tick names
            look_back_period: backtest period
        '''
        self.setup_backtest()
        self.setup_manual(start_new_trades, data, universe, look_back_period)

    def setup_backtest(self):
        # spot info
        self.wallet = Wallet()
        self.current_date = None
        self.strategy_pool = []
        # hist info
        self.num_trades = 0
        self.trading_hist = []
        self.holding_hist = []
        # statistical info
        self.NAV_all = {}
        self.NAV_indi = {}
    
    def setup_manual(self, start_new_trades, data, universe, look_back_period):
        self.lookback_period = look_back_period # rolling period
        self.start_new_trades = start_new_trades # get position, input=data, output = target position
        self.data = data # class, support get asset daily data
        self.universe = universe
        
    def timely_trade(self, freq, st=None, ed=None):
        '''timely initiate new trades
        '''
        all_dates = self.data.get_all_trading_days()
        if st is not None:
            all_dates = [x for x in all_dates if x > st]
        if ed is not None:
            all_dates = [x for x in all_dates if x < ed]
        # adjust frequency for all_dates
        trading_dates = reshuffle_dates(freq, all_dates)
        # execution
        for i, date in enumerate(all_dates):
            if i%(len(all_dates)//10)==0:
                print('{}/{} running...'.format(i, len(all_dates)))
            if date in trading_dates:
                self.actions(date)
            self.daily_summary()
            
    def daily_summary(self):
        '''generate summary statistics for current day
        '''
        today = self.current_date
        current_holding = self.wallet.current_holding()
        NAV = {
                x: current_holding[x] * self.data.get_asset_price_daily(x, today) 
                for x in current_holding if x != 'cash'
                }
        NAV['cash'] = current_holding['cash']
        self.NAV_indi[today] = NAV
        self.NAV_all[today] = sum(NAV.values())
        
    def actions(self, date):
        '''
        main function, responsible for daily issues
        flow:
            1. get relevant data
            2. get position
                old status check
                new add in
                sum position
            3. identify trades and validate trades
            4. trade execution
        '''
        self.current_date = date
        # 1. get data
        used_data = self.data.get_rolling(date, self.universe, self.lookback_period)
        
        '''
        mark: room to improve in c: count only the additional and sum them up
            
        # 2. get position
        a. for existing trades, update status
        b. add new trades to current pool
        c. calculate total units of position
        final output is units of position
        '''
        # a. update status
        active_strategies = [x for x in self.strategy_pool if x.current_status == 'In Use']
        for trade in active_strategies:
            trade.status_update(date, used_data)
        # b. open new trades
        # only open if currently not using same strategy
        new_trades = self.start_new_trades(date, used_data) # f(data), return dictionary, key=asset, value = units
        active_names = [x.name for x in active_strategies]
        for trade_i in new_trades:
            if trade_i.name not in active_names:
                self.strategy_pool.append(trade_i) 
        # c. sum target positions
        active_strategies = [x for x in self.strategy_pool if x.current_status == 'In Use']
        total_positions = [trade.position for trade in active_strategies]
        target_position = {} 
        for trade_pos in total_positions:
            for asset in trade_pos:
                if asset not in target_position:
                    target_position[asset] = trade_pos[asset] 
                else:
                    target_position[asset] += trade_pos[asset] 
#        print(date, target_position)
        
        # 3. identify trades, validate trades
        daily_trades = self.identify_trades(target_position) 
#        print(daily_trades)
        if len(daily_trades) > 0:
            self.trading_hist.append(daily_trades) 
            
        # 4. trade execution
        self.trades_execution(daily_trades, date) 
        
        #5. saving
        if len(daily_trades) > 0:
            holding_log = self.wallet.current_holding() 
            holding_log['date'] = date 
            self.holding_hist.append(holding_log) 

    def identify_trades(self, target_position):
        '''identify trades from targetposition and current position
        input:
            target position
        reff:
            current position
        return:
            trades to make in day
        '''
        daily_trades = []
        for i in self.wallet.current_holding():
            if i not in target_position and i != 'cash':
                target_position[i] = 0
        for i in target_position:
            current_pos = self.wallet.get_position(i)
            target_pos = target_position[i]
            # check tradable
            if not self.tradable(i, self.current_date):
                continue
            # trading info generation
            price = self.data.get_asset_price_daily(i, self.current_date)
            trade = {
                     'asset': i,
                     'date': self.current_date,
                     'price' : price
                     }
            if current_pos > target_pos:
                trade['direction'] = 'close'
                trade['quantity'] = current_pos - target_pos
                daily_trades.append(trade)
            elif current_pos < target_pos:
                trade['direction'] = 'open'
                trade['quantity'] = target_pos - current_pos
                daily_trades.append(trade)
        return daily_trades
    
    def tradable(self, asset, date):
        '''check if price exist for the day
        '''
        if self.data.get_asset_price_daily(asset, date) is not None: # asset has price info on the day
            return True
        else:
            return False

    def trades_execution(self, trades, date):
        '''execution
        trade = {'direction':'open',
                 'asset': 'cash',
                 'quantity': 100}
        trades = [trade1, trade2, ...]
        '''
        for trade in trades:
            self.open_trade(trade)
    
    def open_trade(self, trade):
        '''trading entry execution
        '''
        if trade['direction'] == 'open':
            self.wallet.buy(trade['asset'], trade['quantity'], trade['price'])
            self.num_trades += 1
            return
        elif trade['direction'] == 'close':
            self.wallet.sell(trade['asset'], trade['quantity'], trade['price'])
            self.num_trades += 1
            return


if __name__ == '__main__':
    from backtest_data import Data    # generate universe
    from trade_class import Trade
    import pandas as pd
    a1 = 'ACN'
    a2 = 'ADBE'
    universe = [a1, a2]
    data = Data(universe)
    def sample_exit(date, data, threshold=1.1):
        long = data[a1]
        short = data[a2]
        ratio = short/long
        std = ratio.std()
        avg = ratio.mean()
        Z = (ratio[-1] - avg)/std
        return abs(Z) <= threshold

    def sample_enter_trade(date, data, threshold=2, exit_strategy = sample_exit):
        long = data[a1]
        short = data[a2]
        ratio = short/long
        std = ratio.std()
        avg = ratio.mean()
        Z = (ratio[-1] - avg)/std
        if abs(Z) >= threshold:
            pair = Trade(
                    position_dict = {a1:-1, a2: 1}, 
                    name = 'pairs:+{}-{}'.format(a1, a2), 
                    date = date, 
                    strategy_exit = exit_strategy
                    )
            return [pair]
        else:
            return []
        
    pairs = Backtest(sample_enter_trade, data, universe, look_back_period=80)
    freq = 'D'
    st = '2015-01-12'
    ed = '2015-04-28'
    pairs.timely_trade(freq=freq, st=st, ed=ed)
    pairs.current_date
    print(pairs.strategy_pool)
    for i in pairs.strategy_pool:
        print(i.status_hist)
    pd.Series(pairs.NAV_all).plot(title='NAV')
    pd.DataFrame(pairs.NAV_indi).T.plot(title='Holding Distribution by Asset')
    pairs.holding_hist
    