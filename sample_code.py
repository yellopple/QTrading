# -*- coding: utf-8 -*-
"""
FileIntro:

Created on Wed Sep  9 00:31:42 2020

@author: Archer Zhu
"""

from backtest_data import Get_SP500, Data
import pandas as pd
from backtest_pairs_distance import get_trades

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

# generate backtest rules
sample_enter_trade = lambda date, used_data: get_trades(used_data, global_data=data, date=date)

pairs = Backtest(sample_enter_trade, data, universe, look_back_period=80)
freq = 'D'
st = '2014-01-12'
ed = '2015-04-28'
pairs.timely_trade(freq=freq, st=st, ed=ed)
pairs.current_date
print(pairs.strategy_pool)
for i in pairs.strategy_pool:
    print(i.status_hist)
pd.Series(pairs.NAV_all).plot(title='NAV')
pd.DataFrame(pairs.NAV_indi).T.plot(title='Holding Distribution by Asset')
pairs.holding_hist
