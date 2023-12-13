import configparser
import os
import shutil
import seaborn as sns
import pandas as pd
import math

# 清空因子
def delete_all_factors():
    print('确定永久清空所有因子？y/n')
    if input() == 'y':
        files = os.listdir('./mysystem/factors')
        for f in files:
            shutil.rmtree('./mysystem/factors/'+f)
        print('清空成功')
    else:
        print('已取消')

# 展示所有因子        
def view_all_factors(require_return = False):

    factors = os.listdir('./mysystem/factors')
    ans = pd.DataFrame(columns=['夏普率','提交人','注释'],index=factors)
    for i in factors:
        path = './mysystem/factors/' + i
        lsret = pd.read_csv(path+'/lsreturn.csv').rename(columns={'0':i})
        
        if i == factors[0]:
            all_rets = lsret
        else:
            all_rets = all_rets.merge(lsret)
        
        ans.loc[i]['夏普率'] = lsret[i].mean()*math.sqrt(252)/lsret[i].std()
        with open(path+'/comments.txt', 'r') as file:
            ans.loc[i]['注释'] = file.readline()[:-1]
            ans.loc[i]['提交人'] = file.readline()[13:]   
    display(ans)
    print('相关性图:')
    sns.heatmap(all_rets.set_index('date').corr(),annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    
    if require_return:
        return all_rets, ans
 
# 设置入库标准   
def set_threshold(item,value):
    config = configparser.ConfigParser()
    config.read('./mysystem/config.ini')
    config.set('settings',item,str(value))
    with open('./mysystem/config.ini', 'w') as configfile:
        config.write(configfile)
    print('更新成功')
    
# 打回因子
def rebute(factor,reason):
    message = '因子{}被打回，原因是“{}”，请您尽快修改，感谢理解'.format(factor,reason)
    with open('./mysystem/messages/'+factor+'_rebuttal.txt', 'w') as file:
        file.write(message)
    os.rename('./mysystem/factors/'+factor,'./mysystem/factors/DEPRECATED_'+factor)
    print('打回成功')