# -*- coding: utf-8 -*-
"""
FileIntro:Decorator

Created on Sat Aug  8 09:26:23 2020

@author: Archer Zhu
"""

import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print ('%r  %2.2f s' % \
                  (method.__name__, (te - ts)))
        return result
    return timed

