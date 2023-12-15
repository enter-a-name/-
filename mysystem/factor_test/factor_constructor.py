import pandas as pd
import numpy as np
import datetime

# 构建量价因子
def get_price_factor(data_list,agg_func,startdate=None,enddate=None):
    print('正在计算量价因子')
    columns = []
    i = 0
    cnt = len(data_list.keys())
    for stk in data_list.keys():
        i += 1
        if i%(cnt//5)==0:
            print('当前因子构建进度:{:.0f}%'.format(100*i/cnt))
        columns.append(agg_func(data_list[stk].set_index('date')).rename(stk))
    factor = pd.concat(columns,axis=1)
    
    if startdate!=None:
        if enddate == None:
            print('请同时指定开始和结束时间，否则请求将被忽略')
        else:
            try:
                start = list(factor.index.values).index(np.datetime64(datetime.datetime.strptime(startdate, '%Y%m%d')))
                end = list(factor.index.values).index(np.datetime64(datetime.datetime.strptime(enddate, '%Y%m%d')))
                factor.iloc[:start,:] = np.nan
                factor.iloc[end:,:] = np.nan
            except:
                print('输入日期为非交易日或超出范围，已忽略')
    
    return factor

# 构建基本面因子
def get_finstat_factor(fin_stat,index,pct,startdate=None,enddate=None):
    
    cur_stat = fin_stat[index]
    factor = pd.DataFrame(np.nan,pct.index,pct.columns)
    for i in range(factor.shape[0]):
        # 防止日期越界
        try:
            factor.loc[cur_stat.iloc[i][1]][cur_stat.iloc[i][0]] = cur_stat.iloc[i][2]
        except:
            pass
    factor = factor.ffill()
    
    if startdate!=None:
        if enddate == None:
            print('请同时指定开始和结束时间，否则请求将被忽略')
        else:
            try:
                start = list(factor.index.values).index(np.datetime64(datetime.datetime.strptime(startdate, '%Y%m%d')))
                end = list(factor.index.values).index(np.datetime64(datetime.datetime.strptime(enddate, '%Y%m%d')))
                factor.iloc[:start,:] = np.nan
                factor.iloc[end:,:] = np.nan
            except:
                print('输入日期为非交易日或超出范围，已忽略')
    
    return factor