from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt
import pandas as pd

def _calc_exposure(cur_ret):
    
    # input format: 索引为date，日度收益
    risk_ret = pd.read_csv('./newdata/daily_risk.csv').rename(columns={'Unnamed: 0':'date'})
    tot_df = risk_ret.merge(cur_ret.reset_index()).dropna()

    X_style = tot_df.iloc[:,1:11]
    X_ind = tot_df.iloc[:,11:-1]
    y = tot_df.iloc[:,-1]
    
    # style exposure
    model = Ridge(1e-2)
    model.fit(X_style,y)
    style_exposure = pd.DataFrame(model.coef_).rename(columns={0:'exposure'}).T
    style_exposure.columns = X_style.columns.values

    # industry exposure
    model = Ridge(1e-2)
    model.fit(X_ind,y)
    industry_exposure = pd.DataFrame(model.coef_).rename(columns={0:'exposure'}).T
    industry_exposure.columns = X_ind.columns.values
    
    return style_exposure, industry_exposure

def _show_exposure(style_exposure, industry_exposure):
    
    top_columns = industry_exposure.abs().sum().nlargest(10).index.tolist()
    industry_exposure[top_columns].plot(kind='bar',figsize=(12,3))
    plt.title('行业敞口')
    plt.legend(loc='lower right', ncol=2)  
    plt.show()

    style_exposure.plot(kind='bar',figsize=(12,3))
    plt.title('风格敞口')
    plt.legend(loc='lower right', ncol=2) 
    plt.show()