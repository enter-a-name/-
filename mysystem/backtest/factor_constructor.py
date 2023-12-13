import pandas as pd
import numpy as np

# 构建量价因子
def get_price_factor(data_list,agg_func):
    print('正在计算量价因子')
    columns = []
    i = 0
    cnt = len(data_list.keys())
    for stk in data_list.keys():
        i += 1
        if i%(cnt//5)==0:
            print('当前因子构建进度:{:.0f}%'.format(100*i/cnt))
        columns.append(agg_func(data_list[stk].set_index('date')).rename(stk))
    return pd.concat(columns,axis=1)

# 构建基本面因子
def get_finstat_factor(fin_stat,index,pct):
    cur_stat = fin_stat[index]
    factor = pd.DataFrame(np.nan,pct.index,pct.columns)
    for i in range(factor.shape[0]):
        # 防止日期越界
        try:
            factor.loc[cur_stat.iloc[i][1]][cur_stat.iloc[i][0]] = cur_stat.iloc[i][2]
        except:
            pass
    factor = factor.ffill()
    return factor
    
# 构建CTA时序策略
def get_serial_factor(data_serial,agg_func):
    pass