import pandas as pd
import numpy as np
import datetime
import sys

# 用于处理财务报表的类
class FinStat:
    
    def __init__(self,valueFrame,Mapping):
        
        self.frame = valueFrame
        self.map = Mapping.set_index('item')

    def __getitem__(self, key):
        
        try:
            map_list = self.map.loc[key].values
        except:
            sys.exit('指标不存在')
            
        table = self.frame[map_list[0]]
        index = map_list[1]
        cur_table = table[['stk_id','publish_date',index]]
        
        return cur_table

# 加载财务报表
def load_3sheets():
    
    balance = pd.read_feather('./data/stk_fin_balance.feather')
    income = pd.read_feather('./data/stk_fin_income.feather')
    cashflow = pd.read_feather('./data/stk_fin_cashflow.feather')
    
    mapping = pd.read_feather('./data/stk_fin_item_map.feather')
    
    income = income[(income['publish_date']>=datetime.datetime(2020,1,2))&\
        (income['publish_date']<=datetime.datetime(2022,12,31))]
    balance = balance[(balance['publish_date']>=datetime.datetime(2020,1,2))&\
        (balance['publish_date']<=datetime.datetime(2022,12,31))]
    cashflow = cashflow[(cashflow['publish_date']>=datetime.datetime(2020,1,2))&\
        (cashflow['publish_date']<=datetime.datetime(2022,12,31))]
    
    frame = {'income':income,'balance':balance,'cashflow':cashflow}
    
    return FinStat(frame,mapping)


# 加载不复权的价格
def load_original_prices():
    
    return pd.read_feather('./data/stk_daily.feather')

# 加载价格/高开低收数据并计算复权后的百分比变化
def load_processed_prices():
    
    data = pd.read_feather('./data/stk_daily.feather')
    d = {id:df for id,df in data.groupby('stk_id')}
    pct_cols = []
    for i in d.keys():
        d[i]['pct'] = np.log(d[i]['close']*d[i]['cumadj']).diff()
        pct_cols.append(d[i].set_index('date')['pct'].rename(i))
    return pd.concat(pct_cols,axis=1),d