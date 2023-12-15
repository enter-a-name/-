import pandas as pd
import numpy as np
from mysystem.portfolio_test import _exposure_reg, _conrtib_margin
from mysystem.factor_test import factor_test

def wrapped_portfolio_test(portfolio,require_return = False, detailed=False):
    
    if portfolio.method == 'equal_weight':
        
        # 只是复用一下函数接口，减少代码量，跟CTA没有任何关系
        factor_test.show(portfolio.ls_ret,detailed, cta = True)
        
    else:
        
        print('样本外：')
        
        # 只是复用一下函数接口，减少代码量，跟CTA没有任何关系
        factor_test.show(portfolio.ls_ret.iloc[int((1-portfolio.test_size)*portfolio.feature_ret.shape[0]):],detailed, cta = True)

    if detailed:
        
        df0,df1 = _exposure_reg._calc_exposure(portfolio.ls_ret)
        _exposure_reg._show_exposure(df0,df1)
        
        contributions = _conrtib_margin.show_contrib(portfolio)
        
    if require_return:
        if detailed:
            return df0,df1,contributions
        else:
            print('必须选择detailed选项才能返回')
    