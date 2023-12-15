import pandas as pd
import numpy as np
from mysystem.portfolio_test import portfolio_construct

def show_contrib(portfolio):
    
    out_of_sample_line = int((1-portfolio.test_size)*portfolio.feature_ret.shape[0])
    
    n = portfolio.feature_ret.set_index('date').shape[1]
    
    contributions = pd.DataFrame(np.zeros((1,n)),['contribution'],portfolio.feature_ret.columns[1:])
    
    rets = portfolio.feature_ret.set_index('date')
    
    # 等权组合，贡献为各自收益
    if portfolio.method == 'equal_weight':
        print(np.array(rets.fillna(0).mean() / rets.fillna(0).mean().sum()))
        contributions.iloc[0,:] = np.array(rets.fillna(0).mean() / rets.fillna(0).mean().sum())
        
    # 有效前沿组合，按测试集上的权重乘以该段收益计算
    elif portfolio.method == 'effecient_frontier':
        
        weighted_oos_ret = rets.iloc[out_of_sample_line:].fillna(0) * portfolio.weight
        contributions.iloc[0,:] = np.array(weighted_oos_ret.mean() / weighted_oos_ret.mean().sum())
        
    # 机器学习组合，按边际贡献的比例分配
    else:
        margins = np.zeros(n)
        std_ret = portfolio.ls_ret.mean()

        for i in range(n):
            if i == n-1:
                cur_feature = portfolio.features[:-1]
                cur_rets = portfolio.feature_ret.set_index('date').iloc[:,:-1]
            else:
                cur_feature = portfolio.features[:i] + portfolio.features[i+1:]
                cur_rets = portfolio.feature_ret.set_index('date').iloc[:,:i] + portfolio.feature_ret.set_index('date').iloc[:,i+1:]
            test_portfolio = portfolio_construct.Portfolio\
                (portfolio.pct,cur_feature,cur_rets,portfolio.test_size)
            test_portfolio.construct_portfolio('ml')
            
            # 每个因子的边际贡献
            margins[i] = (std_ret - test_portfolio.ls_ret.mean())/std_ret
            
        print('因子贡献：')
        contributions.iloc[0,:] = margins / margins.sum()
        
    display(contributions)
    return contributions

        