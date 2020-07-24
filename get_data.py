# -*- coding: utf-8 -*-
"""
FileIntro:

Created on Wed Jul 22 16:03:01 2020

@author: Archer Zhu
"""

import yfinance as yf
import pandas as pd
import numpy as np

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
SP500 = Get_SP500()

def Get_ChinaConcept():
    '''China Concept in US
    table 1, 2 are NYSE, NASDAQ
    '''
    link = 'https://en.wikipedia.org/wiki/China_concepts_stock'
    tables = pd.read_html(link)
    CC = tables[0][1].to_list()[1:] + tables[1][1].to_list()[1:]
    return CC
ChinaConcept = Get_ChinaConcept()

symbol = 'MMM'
def Get_US_Equity(symbol, kind = 'hist'):
    '''
    get US stock data from yfinance
    US market
    '''
    ticker = yf.Ticker(symbol)
    # ^ returns a named tuple of Ticker objects
    if kind == 'hist':
        # access each ticker using (example)
        return ticker.history('max')
us1 = Get_US_Equity(symbol)

def Get_CN_Equity(symbol):
    '''
    get CN stock data from TuShare
    CN market
    '''
    return




