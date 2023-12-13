import numpy as np
import pandas as pd
import os
import logging
import configparser
from mysystem.backtest import factor_constructor
import math
import matplotlib.pyplot as plt
from scipy.stats import t

# 对因子进行一站式测试
def wrapup_test(pctdf,data,agg_func,require_returns = False, require_submit = False, cta = False):
    
    if not cta:
        factor = factor_constructor.get_price_factor(data,agg_func)
        results = single_factor_backtest(pctdf,factor,num_bins=5)
        show(results)
        
    else:
        pass
    
    if require_submit:
        submit(factor,results,'未命名','研究员使用了默认测试提交，因此未给出说明')
        
    if require_returns:
        return factor, results
    

# 对截面因子进行分组回测
def single_factor_backtest(pctdf,factor,num_bins=10):
    
    print('正在计算分组收益')
    # 计算分组收益
    factor = factor.shift(1)
    stock_num = (factor.shape[1] - factor.isna().sum(axis=1))/num_bins
    factor_rank = factor.rank(na_option='keep',axis=1)
    bin = num_bins - factor_rank.divide(stock_num,axis=0).replace([np.inf, -np.inf], np.nan)
    bin = bin.applymap(lambda x: int(x) if not pd.isna(x) else x)
    for j in range(num_bins):
        pctdf['group '+str(j)] = np.nan
    for i in pctdf.index:
        for j in range(num_bins):
            pctdf['group '+str(j)][i] = pctdf.loc[i].iloc[:-num_bins][bin.loc[i]==j].mean()
    ans = pctdf.iloc[:,-num_bins:]
    ans = ans.dropna()
    for j in range(num_bins):
        del pctdf['group '+str(j)]
    
    print('正在计算IC')
    # 计算IC/rankIC
    rankic = pd.Series([pctdf.iloc[i].corr(factor_rank.iloc[i]) for i in range(len(pctdf))])
    rankic.index = pctdf.index
    ans['rankIC'] = rankic
    
    ic = pd.Series([pctdf.iloc[i].corr(factor.iloc[i]) for i in range(len(pctdf))])
    ic.index = pctdf.index
    ans['IC'] = ic
    
    return ans

# 展示截面因子回测结果
def show(results, detailed = False):
    
    returns = results.iloc[:,:-2]
    IC = results.iloc[:,-2:]
    
    ls_ret = (returns.iloc[:,0] - returns.iloc[:,-1]).dropna()
    print('多空组合',end='')
    mean,sd,sr,dd = get_stats(ls_ret,show=True)
    print('纯多头超额收益{:.2f}%, 多头'.format((returns.dropna().iloc[:,0].mean() - returns.dropna().mean().mean())\
        *100),end='')
    mean,sd,sr,dd = get_stats(returns.iloc[:,0].dropna(),show=True)
    
    tstat = IC['IC'].mean() * np.sqrt(IC['IC'].shape[0]) / IC['IC'].std()
    pval = t.sf(abs(tstat), IC['IC'].shape[0])
    
    print('RankIC均值{:.4f}，RankIC标准差{:.4f}，IC均值{:.4f}，IC标准差{:.4f}，T统计量{:.4f}，显著性水平(p-value){:.4f}'.format(\
        IC['rankIC'].mean(),IC['rankIC'].std(),IC['IC'].mean(),IC['IC'].std(),tstat,pval))
    
    if detailed:
        plot(returns)

# 提交因子
def submit(factor,results,name,comment,cta=False):
    
    if not cta:
        returns = results.iloc[:,:-2]
        ls_ret = returns.iloc[:,0] - returns.iloc[:,-1]
        mean,sd,sr,dd = get_stats((returns.iloc[:,0] - returns.iloc[:,-1]).dropna())
    else:
        mean,sd,sr,dd = get_stats((returns.iloc[0]).dropna())
        ls_ret = results.iloc[:,0]
        
    corr = 0
    print('正在检验相关性和收益情况')
    corr = get_corr(ls_ret)
    
    corr_barrier = 0.7
    sr_bar = 0.3
    
    # 判断是否符合入库条件
    if corr>corr_barrier:
        print('相关性过高！拒绝入库')
    elif sr<sr_bar:
        print('收益过低！拒绝入库')
        
    # 入库
    else:
        os.makedirs('./mysystem/factors/'+str(name))
        factor.reset_index().to_feather('./mysystem/factors/'+str(name)+'/value.feather')
            
        ls_ret.to_csv('./mysystem/factors/'+str(name)+'/lsreturn.csv')
        file = open('./mysystem/factors/'+str(name)+'/comments.txt','w')
        file.write(comment+'\nContributer: '+'a')
        file.close()
        print('Submit Success')
   
################################# 辅助函数 #################################        

def plot(results,cta = False):
    
    clean_results = results.dropna()
    if not cta:
        (clean_results+1).cumprod().plot(legend=True,title='分组收益',figsize=(12,4))
        pd.DataFrame((clean_results.iloc[:,0] - clean_results.iloc[:,-1]+1).cumprod())\
            .plot(legend=False,title='多空收益',figsize=(12,4))
    else:
        pd.DataFrame((clean_results+1).cumprod()).plot(legend=False,title='多空收益',figsize=(12,4))

def get_stats(x,show=False,ret=True):
    
    mean = x.mean()*252
    sd = x.std()*math.sqrt(252)
    sr = mean/sd
    tmp = (1+x).cumprod()
    dd = ((tmp.cummax()-tmp)/tmp.cummax()).max()
    if show:
        print('年化{:.2f}%，波动{:.2f}%，夏普{:.2f}，回撤{:.2f}%'.format(mean*100,sd*100,sr,dd*100))
    if ret:
        return mean,sd,sr,dd

def get_corr(lsret):
    
    candidates = os.listdir('./mysystem/factors/')
    corr = 0
    for i in candidates:
        old_ret = pd.read_csv('./mysystem/factors/'+i+'/lsreturn.csv').rename(columns={'0':'old'})
        old_ret['date'] = pd.to_datetime(old_ret['date'])
        new_ret = pd.DataFrame(lsret).reset_index().rename(columns={0:'new'})
        tmp = old_ret.merge(new_ret).dropna()[['old','new']].corr().iloc[1,0]
        corr = max(abs(tmp),corr)
    print('最大相关性:{:.3f}'.format(corr))
    return corr