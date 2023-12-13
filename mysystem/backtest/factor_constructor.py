import pandas as pd
import numpy as np

def get_independent_factor(data_list,agg_func):
    columns = []
    i = 0
    cnt = len(data_list.keys())
    for stk in data_list.keys():
        i += 1
        if i%(cnt//5)==0:
            print('当前因子构建进度:{:.0f}%'.format(100*i/cnt))
        columns.append(agg_func(data_list[stk].set_index('date')).rename(stk))
    return pd.concat(columns,axis=1)

def get_finstat_factor(fin_stat,index,pct):
    factor = pd.DataFrame(np.nan,pct.index,pct.columns)
    
    
def get_serial_factor(data_serial,agg_func):
    pass