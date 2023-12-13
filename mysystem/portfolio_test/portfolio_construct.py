import pandas as pd
import numpy as np
import sklearn
import os

def load_features(ignore_deprecated = True):
    
    factors = os.listdir('./mysystem/factors')
    if ignore_deprecated:
        factors = [i for i in factors if i[0:2]!='DE']
        
    features = []
    
    for i in factors:
        
        path = './mysystem/factors/' + i
        lsret = pd.read_csv(path+'/lsreturn.csv').rename(columns={'0':i})
        cur_feature = pd.read_feather(path+'/value.feather')
        features.append(cur_feature)
        
        if i == factors[0]:
            all_rets = lsret
        else:
            all_rets = all_rets.merge(lsret)
    
    return features, all_rets

class Portfolio:
    
    def __init__(self,pct,features,rets,test_set_size=0.3):
        
        self.pct = pct
        self.features = features
        self.feature_ret = rets
        self.test_size = test_set_size
        self.weight_by_day = None
        
    # 用于数据降维和标准化
    def feature_preproc(self,method,k=None):
        
        if method == 'pca':
            pass
        elif method == 'selectK':
            if k == None:
                k = self.features.shape[1]//2
        elif method == 'standardize':
            pass
        else:
            print('不合法的降维方式，请选择pca/selectK/standardize')
        
        self.feature_ret = None
        
    def construct_portfolio(self,method,**kwargs):
        
        if method == 'equal_weight':
            _eq_construct(self)
        
        if method == 'effecient_frontier':
            _capm_construct(self,**kwargs)
        
        if method == 'ml':
            _ml_construct(self,**kwargs)
        
    def _eq_construct(self):
        pass
    
    def _capm_construct(self,**kwargs):
        if self.feature_ret == None:
            print('有效前沿组合的构造不能接受对因子的预处理，因为这会改变每个因子的收益')
            return
        pass
    
    def _ml_construct(self,**kwargs):
        pass