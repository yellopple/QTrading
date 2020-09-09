# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 16:34:12 2020

Data class for back testing purpose

@author: yello
"""

from get_data import GetData, Get_SP500
import pandas as pd


class Data:
    def __init__(self, universe, price_to_use='Adj Close'):
        # get data
        self.data_raw = GetData(names=universe)
        self.universe = universe
        # price to use
        self.price_to_use = price_to_use
    
    def get_rolling_one(self, date, asset, rolling_window, shift_back=1):
        '''get rolling info for one asset
        shift_back is for backwarding dates:
            shift_back == 0: including data on date
            shift_back == 1: does not include data on date
        return Series
        '''
        # tradable on the day
        check = self.get_asset_price_daily(asset, date)
        if check is not None:
            dates = self.data_raw[asset].Date.to_list()
            idx = dates.index(date)
            if idx-rolling_window < 0:
                return None
            dates_to_use = dates[max(0, idx-rolling_window):max(1,idx+1-shift_back)]
            return self.data_raw[asset][['Date',self.price_to_use]].set_index('Date')[dates_to_use[0]:dates_to_use[-1]][self.price_to_use]
        else:
            return None
    
    def get_rolling(self, date, universe, rolling_window, shift_back=1):
        '''get rolling info for all assets in universe
        '''
        rolling_rst = {}
        for asset in universe:
            temp = self.get_rolling_one(date, asset, rolling_window, shift_back=shift_back)
            if temp is not None:
                rolling_rst[asset] = temp
        return rolling_rst
    
    def get_asset_price_daily(self, asset, date):
        '''get asset price for the day, if not exist, return None
        '''
        data = self.data_raw[asset]
        if date in data.Date.to_list():
            return data[['Date',self.price_to_use]].set_index('Date')[self.price_to_use][date]
        else:
            return None
    
    def get_all_trading_days(self):
        '''get all trading days from self.data_raw
        defination: if any asset in universe has value, then it's a trading day.
            if can obtain any index from yfinance, then should use index date as trading day
        '''
        date_set = set()
        for asset in self.data_raw:
            date_set = date_set|set(self.data_raw[asset].Date.to_list())
        date_list = list(date_set)
        date_list.sort()
        return date_list
    
if __name__ == '__main__':
    # sample sector
    spinfo = Get_SP500(output='all').set_index('Symbol').to_dict()
    temp = pd.Series(spinfo['GICS Sector']).reset_index()
    temp.columns=['id','indust']
    universe = temp[temp['indust'] == 'Information Technology'].id.to_list()[:10]
    # get data
#    data_raw = GetData(names=universe)
    
    # samples
    rolling_window = 30
    date = '2013-10-07'
    asset = 'ACN'
    a = Data(universe)
    a.get_all_trading_days()
    a.get_rolling(date, universe, rolling_window)
    a.get_rolling_one(date, asset, rolling_window, shift_back=0)
    a.get_asset_price_daily(asset, date)
    