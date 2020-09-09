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

def Get_SP500(existing=True, output='ticker'):
    '''
    return SP500 list from Wiki
    Note: somehow they give more than 500 stocks
    Warning: if Wiki change layout, function may fail to work
    '''
    name = 'Universe_SP500'
    if existing:
        table = pd.read_csv(file+name+'.csv')
    else:
        link = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(link)[0]
        table.to_csv(file+name+'.csv', index=False)
    SP500 = table['Symbol'].to_list()
    if output=='ticker':
        return SP500
    elif output == 'all':
        return table

def Get_ChinaConcept(skip=True):
    '''China Concept in US
    table 1, 2 are NYSE, NASDAQ
    '''
    if skip:
        return pd.DataFrame()
    link = 'https://en.wikipedia.org/wiki/China_concepts_stock'
    tables = pd.read_html(link)
    CC = tables[0][1].to_list()[1:] + tables[1][1].to_list()[1:]
    return CC

# sp500 names
SP500 = Get_SP500(existing=True)
# china concept stock names
ChinaConcept = Get_ChinaConcept(skip=True)

def Get_US_Equity(symbol, kind = 'hist', st='2010-01-01', ed='2020-07-29'):
    '''
    get US stock data from yfinance
    Symbols:
        * US market: APPL
        * HK market: 0002.hk
    '''
    # ^ returns a named tuple of Ticker objects
    if kind == 'hist':
        # history OCHL, adj Close, Volume
        return yf.download(symbol, start=st, end=ed).reset_index()
    elif kind == 'hist_div':
        # history OCHL, dividend(no adj Close)
        return yf.Ticker(symbol).history('max').reset_index()
    elif kind == 'info':
        # information of stock
        return yf.Ticker(symbol).info
    elif kind == 'option':
        return yf.Ticker(symbol).options

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

def GetData(segment=None,names=[]):
    '''for calling data
    segment: str, in ['sp500','cc']
        sp500: sp500 stocks
        cc: china concept stocks
    names: ['MMM'], stock tickers
    '''
    rst = {}
    got = Get_existing()
    if len(names) > 0:
        name_got = list(set(names)&set(got))
        name_new = list(set(names)-set(got))
    elif segment is not None:
        names = {'sp500':SP500,'cc':ChinaConcept}[segment] # use existing instead of calling recursively
        name_got = list(set(names)&set(got))
        name_new = list(set(names)-set(got))
    # get
    for name in name_got:
        rst[name] = pd.read_csv(file + name +'.csv')
    for name in name_new:
        temp = Get_US_Equity(name, kind = 'hist')
        if len(temp) > 0:
            rst[name] = temp
            temp.to_csv(file+name+'.csv', index=False)
    return rst

if __name__ == '__main__':
    # sample get price
    if False:
        symbol = 'MMM'
        us1 = Get_US_Equity(symbol)
    
    # batch get
    if False:
        names = ChinaConcept
        Saving(names)

    # get data
    if False:
        rst = GetData(segment='sp500')
