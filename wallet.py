# -*- coding: utf-8 -*-
"""
FileIntro:Wallet, control balance

Created on Fri Aug 21 20:42:39 2020

@author: Archer Zhu
"""
import numpy as np

class Wallet:
    '''For saving holding positions, count in units
    '''
    def __init__(self, initial_cash = 100):
        self.holding={'cash':initial_cash}
        
    def buy(self, asset, quantity, price):
        if asset not in self.holding:
            self.holding[asset] = 0
        self.holding[asset] += quantity
        self.holding['cash'] -= price*quantity
        
    def sell(self, asset, quantity, price):
        if asset not in self.holding:
            # it's possible to open a non-covered short position
            self.holding[asset] = 0
        self.holding[asset] -= quantity
        self.holding['cash'] += price*quantity

    def current_holding(self):
        '''return current holding and values'''
        current_holding = {}
        for i in self.holding:
            if self.holding[i] != 0:
                current_holding[i] = self.holding[i]
        return current_holding
    
    def get_position(self, asset):
        if asset not in self.holding:
            print('Asset:{} not in current wallet.'.format(asset))
            return 0
        else:
            return self.holding[asset]
            
if __name__ == '__main__':
    # sample
    Wallet(1000).holding
