import pandas as pd
import numpy as np
from mysystem.portfolio_test import _exposure_reg, _conrtib_margin
from mysystem.factor_test import factor_test

def wrapped_portfolio_test(portfolio,detailed=False):
    
    if portfolio.method == 'equal_weight':
        factor_test.show(portfolio.ls_ret,detailed, cta = True)
    else:
        print('样本外：')
        factor_test.show(portfolio.ls_ret.iloc[int((1-portfolio.test_size)*portfolio.feature_ret.shape[0]):],detailed, cta = True)

    if detailed:
        
        df0,df1 = _exposure_reg._calc_exposure(portfolio.ls_ret)
        _exposure_reg._show_exposure(df0,df1)
    
def distribute_contibution(portfolio):
    
    contributions = _conrtib_margin(portfolio)

def portfolio_performance_show(portfolio):
    
    pass