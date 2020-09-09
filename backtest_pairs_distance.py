# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 01:03:25 2020

function shoud return an object that includes callable exit strategy

@author: yello
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from spikes import SpikesCalculations
from trade_class import Trade # for marking exit strategy, names, etc

def pairs_distance_one(s1, s2, stationary_p=0.05):
    '''
    calculating pairs relevant info through distance measure
    s1, s2 are stock price series
    
    calibrated info:
        - Z score
        - stationarity(ADF)
        - spikes
    
    >>> s1 = rst['DPZ']
    >>> s2 = rst['MCD']
    >>> pairs_distance_one(s1, s2)
    '''
    idx = set(s1.index)&set(s2.index)
#    if len(idx) <= 100:
#        return {'std':np.nan,'avg':np.nan,'current':np.nan, 'ratio': np.nan,'ADF':False,'len':np.nan}
    #0 formatting-align index
    a1 = s1[idx].sort_index().dropna()
    a2 = s2[idx].sort_index().dropna()
    #1 normalize price
    a1 = a1/a1[-1]
    a2 = a2/a2[-1]
    #2 distence detection
    diff = a1/a2-1
    diff[diff==np.inf]=np.nan # make inf -> nan, should be form data error
    #3 stationarity
    diff = diff.dropna()
    result = adfuller(diff)
    p = result[1] # p-value
    if p > stationary_p:
        stationary = False
##        print('non-stationary')
#        return None
    else:
        stationary = True
    #4 STD
    std = diff.std()
    avg = diff.mean()
    current = (0-avg)/std
    #5 Spikes calculations
    spike_days = SpikesCalculations(diff)
    spike_count = len(spike_days)
    if spike_count == 0:
        spike_days_avg = np.nan
    else:
        spike_days_avg = sum(spike_days)/len(spike_days)
    return {
            'std':std,'avg':avg,'current':current, 'ratio': diff,'ADF':stationary,'len':len(diff), 
            'spike_count':spike_count, 'spike_days':spike_days_avg, 'spike_detail':spike_days
            }

def pairs_distance_all(used_data, max_pair=50):
    # generate all pairs in universe
    ticks = list(used_data.keys())
    pairs = []
    for i in range(len(ticks)-1):
        for j in range(i+1, len(ticks)):
            pairs.append((ticks[i],ticks[j]))
            
    # cal pairs indicators for each candidate
    pairs_rst = []
    for i, names in enumerate(pairs):
        # log
        if i % 500==0:
            print('{}/{}, {}'.format(i, len(pairs), len(pairs_rst)))
        # calculation
        s1 = used_data[names[0]]
        s2 = used_data[names[1]]
        pair_rst = pairs_distance_one(s1, s2) # dictionary
        pair_rst['names'] = names
        pairs_rst.append(pair_rst)
        if len(pairs_rst) >= max_pair:
            break
    
    # check candidates from std
    DF = pd.DataFrame(pairs_rst)
#    DF['len'] = [len(x) if x is not np.nan else 0 for x in DF.ratio ]
#    DF1 = DF[DF['len']>1500]
    DF = DF.sort_values('std')
    return DF

def pairs_tradable(info_DF_pairs):
    # 1. ADF = True
    DF = info_DF_pairs[info_DF_pairs['ADF']==True]
    # 2. std 2 std away
    DF['Z'] = (DF.current - DF.avg)/DF['std']
    DF = DF[DF['Z'] > 2]
    # 3. spike > 3
    DF_spike = DF[DF['spike_count'] > 3]
    # 4. returning probability
    return DF_spike

def exit_strategy(long_name, short_name, data, threshold):
    s1 = data[long_name]
    s2 = data[short_name]
    idx = set(s1.index)&set(s2.index)
#    if len(idx) <= 100:
#        return {'std':np.nan,'avg':np.nan,'current':np.nan, 'ratio': np.nan,'ADF':False,'len':np.nan}
    #0 formatting-align index
    a1 = s1[idx].sort_index().dropna()
    a2 = s2[idx].sort_index().dropna()
    #1 normalize price
    a1 = a1/a1[-1]
    a2 = a2/a2[-1]
    #2 distence detection
    diff = a1/a2-1
    diff[diff==np.inf]=np.nan # make inf -> nan, should be form data error
    #4 STD
    std = diff.std()
    avg = diff.mean()
    current = (0-avg)/std
    return abs(current) < threshold

def pairs_weights(pairs_tradable_DF, global_data, date):
    # ratio = S1/S2, if Z too high, meaning S1/S2 will revert, long S2, short S1
    # for negative Z, long S1, short S2
    # 1. identify long/short position from sign of Z
    names = pairs_tradable_DF.names.to_list()
    orders = pairs_tradable_DF.Z.to_list()
    names_ordered = []
    for pair, order in zip(names, orders):
        if order < 0:
            names_ordered.append(pair[-1:])
        else:
            names_ordered.append(pair)
    # 2. assign weight from price
    final_trades = []
    for pairs in names_ordered:
        short, long = pairs
        short_price = global_data.get_asset_price_daily(short, date)
        long_price = global_data.get_asset_price_daily(long, date)
        # 3. transfer to percentage
        pair = Trade(
                position_dict = {short: -1/short_price, long: 1/long_price}, 
                name = 'pairs:+{}-{}'.format(long, short), 
                date = date, 
                strategy_exit = lambda date, data: exit_strategy(long_name=long, short_name=short, data=data, threshold=2)
                )
        final_trades.append(pair)
    return final_trades[:2]

def get_trades(used_data, global_data, date):
    '''entering trades rules
    '''
    # 1. pairs info
    info_DF_pairs = pairs_distance_all(used_data, max_pair=50)
    # 2. pairs trading target
    pairs_tradable_DF = pairs_tradable(info_DF_pairs)
    # 3. determine weights
    target_weights = pairs_weights(pairs_tradable_DF, global_data, date)
    return target_weights

if __name__ == '__main__':
    from backtest_data import Get_SP500, Data
    from backtest_class import Backtest
    
    # generate universe
    spinfo = Get_SP500(output='all').set_index('Symbol').to_dict()
    temp = pd.Series(spinfo['GICS Sector']).reset_index()
    temp.columns=['id','indust']
    universe = temp[temp['indust'] == 'Information Technology'].id.to_list()[:10]
    
    # generate data object
    rolling_window = 100
    date = '2020-06-16'
    data = Data(universe)
    
    # data for check
    used_data = data.get_rolling(date, universe, rolling_window, shift_back=1)
    global_data = data
    get_trades(used_data, global_data, date)
    

    