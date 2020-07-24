# -*- coding: utf-8 -*-
"""
FileIntro:

Created on Wed Jul 22 16:03:01 2020

@author: Archer Zhu
"""

import yfinance as yf
import pandas as pd
import numpy as np
import os
import time

file='StockData/'

def Get_SP500():
    '''
    return SP500 list from Wiki
    Note: somehow they give more than 500 stocks
    Warning: if Wiki change layout, function may fail to work
    '''
    link = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(link)
    SP500 = tables[0]['Symbol'].to_list()
    return SP500

def Get_ChinaConcept():
    '''China Concept in US
    table 1, 2 are NYSE, NASDAQ
    '''
    link = 'https://en.wikipedia.org/wiki/China_concepts_stock'
    tables = pd.read_html(link)
    CC = tables[0][1].to_list()[1:] + tables[1][1].to_list()[1:]
    return CC

def Get_US_Equity(symbol, kind = 'hist'):
    '''
    get US stock data from yfinance
    US market
    '''
    ticker = yf.Ticker(symbol)
    # ^ returns a named tuple of Ticker objects
    if kind == 'hist':
        # access each ticker using (example)
        return ticker.history('max').reset_index()

def Get_CN_Equity(symbol):
    '''
    NOTE: pending update
    get CN stock data from TuShare
    CN market
    '''
    return

def Get_existing():
    '''Get existing file names and return csv names
    '''
    names = os.listdir(file)
    csv_names = [x[:-4] for x in names if x[-3:] == 'csv']
    return csv_names
    

def Saving(names):
    got = Get_existing()
    name_update = list(set(names)-set(got))
    n = len(name_update)
    print('total names require update: {}.'.format(n))
    for i, name in enumerate(name_update):
        # status check
        if i % 10 == 0:
            print(f'{i}/{n}')
        # name download
        if name not in got:
            time.sleep(0.1)
            df = Get_US_Equity(symbol=name, kind = 'hist')
            if len(df) > 0: # may get fail
                df.to_csv(file+name+'.csv', index=False)

if __name__ == '__main__':
    # sp500 names
    SP500 = Get_SP500()
    # china concept stock names
    ChinaConcept = Get_ChinaConcept()
#    # sample get price
#    symbol = 'MMM'
#    us1 = Get_US_Equity(symbol)
    
    # batch get
    names = ChinaConcept
    Saving(names)

