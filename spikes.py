# -*- coding: utf-8 -*-
"""
FileIntro:Spikes

Created on Sat Aug 22 11:14:21 2020

@author: Archer Zhu
"""

def Stage_Digitalize(c, U_in, U_out, D_in, D_out):
    '''
    cal stage code
    '''
    if c > U_out:
        return 2
    elif c > U_in:
        return 1
    elif c > D_in:
        return 0
    elif c > D_out:
        return -1
    else:
        return -2

def SpikeCleansing(Series):
    '''Identify trading part from Series
    A valid spike is defined as starting from first trading entery signal(2/-2) to reverting to mean level(end)
    If entery signal(2/-2) is not hit in Series, return None
    '''
    if Series.max() == 2:
        # identify 2
        for j, i in enumerate(Series):
            if i == 2:
                return Series[j:]
    elif Series.min() == -2:
        # identify -2
        for j, i in enumerate(Series):
            if i == -2:
                return Series[j:]
    else:
        return None

def SpikesCalculations(Series, in_std=0.2, out_std=1):
    '''Calculate Spikes numbers and average days from pairs time series
    '''
#    in_std, out_std = 0.2, 1 # 如何判断？ 根据distribution判断？
    std = Series.std()
    avg = Series.mean()
    # 1 digitalize stage
    U_in = avg + in_std*std
    U_out = avg + out_std*std
    D_in = avg - in_std*std
    D_out = avg - out_std*std
    temp_dig = Series.apply(lambda c: Stage_Digitalize(c, U_in, U_out, D_in, D_out))

    # 2 pattern identification
    # divide by 0
    # 定位分割点
    record = []
    for i in range(len(temp_dig)-1):
        val0 = temp_dig[i]
        val1 = temp_dig[i+1]
        if val0 * val1 <= 0: # 方向转变或者没用，需要分割
            record.append(i) 
    
    # 3 split region
    temp_rst = []
    last = 0
    for i in record:
        if i>=last:
            temp_rst.append(temp_dig[last:i+2]) # need to keep the day after 
            last = i+1
    
    # 4 statistics calculation
    spike_days = []
    for i in temp_rst:
        # 识别是否满足条件
        # 条件： 第1个2(-2) 到最后(第一次hit回0)
        Series_clean = SpikeCleansing(i)
        if Series_clean is not None:
            spike_days.append(len(Series_clean))
#    count_spikes = len(spike_days)
#    average_spike_days = sum(spike_days)/count_spikes
    return spike_days