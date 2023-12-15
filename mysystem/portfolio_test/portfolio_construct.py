import pandas as pd
import numpy as np
import sklearn
import os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.optimize import minimize
import lightgbm as lgb

# 加载因子，控制是否忽略被打回的
def load_features(ignore_deprecated = True):
    
    factors = os.listdir('./mysystem/factors')
    if ignore_deprecated:
        factors = [i for i in factors if i[0:2]!='DE']
        
    features = []
    
    for i in factors:
        
        path = './mysystem/factors/' + i
        lsret = pd.read_csv(path+'/lsreturn.csv').rename(columns={'0':i})
        cur_feature = pd.read_feather(path+'/value.feather')
        features.append(cur_feature.set_index('date'))
        
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
        self.ls_ret = None
        self.weight = None
        self.method = None
        self.modified = False
        
    # 用于数据降维和标准化
    def feature_preproc(self,method,n_components = 3):
        
        # pca降维
        if method == 'pca':
            
            self.feature_preproc('standardize')
            
            dataframes_list = self.features
            ans = [pd.DataFrame(np.nan,dataframes_list[0].index,dataframes_list[0].columns) for i in range(n_components)]
            print('正在进行PCA')

            # 按日标准化
            for i in range(dataframes_list[0].shape[0]):
                
                if i%(dataframes_list[0].shape[0]//10) == 0:
                    print('当前进度{:.0f}%'.format(i/dataframes_list[0].shape[0]*100))
                    
                cur_fact = []
                for j in range(len(dataframes_list)):
                    cur_fact.append(dataframes_list[j].fillna(0).iloc[i,:])
                cur_fact_arr = np.vstack(cur_fact)
                    
                # 判断有值的比例是否超过阈值
                if np.count_nonzero(cur_fact_arr) / cur_fact_arr.flatten().shape[0] >= 0.5:
                    model = PCA(n_components=n_components)
                    model.fit(cur_fact_arr.T)
                    transformed_arr = model.transform(cur_fact_arr.T)
                    for j in range(n_components):
                        ans[j].iloc[i,:] = transformed_arr[:,j]
            
            self.modified = True
            self.features = ans
            self.feature_preproc('standardize')
              
        # 数据标准化  
        elif method == 'standardize':
            for i in range(len(self.features)):
                scaler = StandardScaler()
                scaler.fit(self.features[i])
                cur = pd.DataFrame(scaler.transform(self.features[i]),columns=self.features[i].columns)
                cur.index = self.features[i].index
                self.features[i] = cur
            
        else:
            print('不合法的降维方式，请选择pca/standardize')
        
    # 构建组合的整体接口
    def construct_portfolio(self,method):
        
        self.method = method
        
        if method == 'equal_weight':
            self._eq_construct()
            self.method = 'equal_weight'
        elif method == 'effecient_frontier':
            self._capm_construct()
            self.method = 'effecient_frontier'
        elif method == 'ml':
            self._ml_construct()
            self.method = 'ml'
        else:
            print('不合法的组合构建方式，请选择equal_weight/effecient_frontier/ml')
        
    # 等权组合
    def _eq_construct(self):
        
        if self.modified == True:
            print('等权组合的构造不能接受对因子的预处理，因为这会改变每个因子的收益')
            return
        
        self.ls_ret = self.feature_ret.set_index('date').mean(axis=1)
        n =  self.feature_ret.shape[1] - 1
        self.weight = np.array([1/n for i in range(n)])
        
    # 有效前沿组合
    def _capm_construct(self):
        
        # 最大化样本内夏普率
        def objective_function(w, r, C):
            
            mean_return = np.dot(w, r)
            std_dev = np.sqrt(np.dot(np.dot(w, C), w))
            return -mean_return / std_dev
        
        if self.modified == True:
            print('有效前沿组合的构造不能接受对因子的预处理，因为这会改变每个因子的收益')
            return
        
        n =  self.feature_ret.shape[1] - 1
        initial_guess = np.ones(n) / n # 初始化权重
        
        # 样本内调参
        in_sample_feature_ret = self.feature_ret.set_index('date')\
            .iloc[:int((1-self.test_size)*self.feature_ret.shape[0])]
            
        r = in_sample_feature_ret.mean(axis=0)
        C = in_sample_feature_ret.corr()
        
        # 优化算法
        bounds = tuple((0, 1) for i in range(n))
        result = minimize(objective_function, initial_guess, args=(r, C),\
            bounds=bounds)

        self.weight = result.x / result.x.sum()
        self.ls_ret = (self.weight * self.feature_ret.set_index('date')).sum(axis=1)
    
    # 机器学习组合
    def _ml_construct(self):
        
        # 这里仅以lgboost为例，以后应该加入更多选择
        num_round = 100
        
        Xtrain = np.array([i.shift(1).iloc[int((1-self.test_size)*self.feature_ret.shape[0]):].values\
            for i in self.features]).reshape(4,-1)
        Xtot = np.array([i.shift(1).values for i in self.features]).reshape(4,-1)
        
        Ytrain = (((self.pct>0).astype('int') - (self.pct<0).astype('int')))\
            .iloc[int((1-self.test_size)*self.feature_ret.shape[0]):].values.reshape((1,-1))
        
        train_data = lgb.Dataset(Xtrain.T, label=Ytrain.flatten() + 1)
        
        params = {
            'boosting_type': 'gbdt',
            'objective': 'multiclass', 
            'metric': 'multi_logloss',  
            'num_class': 3, 
            'learning_rate': 0.1,
            'num_leaves': 31,
            'max_depth': -1,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'verbose': 0
        }
        
        bst = lgb.train(params, train_data, num_round)
        
        y_pred = bst.predict(Xtot.T,num_iteration=bst.best_iteration)
        
        holdings = (np.argmax(y_pred,axis=1)).reshape(self.pct.shape) - 1
        holdings = holdings / abs(holdings).sum(axis=1)[:,np.newaxis]
        
        self.ls_ret = (self.pct * holdings).sum(axis=1)