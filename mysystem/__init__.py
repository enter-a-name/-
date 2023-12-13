import matplotlib.pyplot as plt
import os
import warnings

warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

print('欢迎使用回测系统')

if 'messages' not in os.listdir('./mysystem'):
    os.makedirs('./mysystem/messages/')

files = os.listdir('./mysystem/messages')
for f in files:
    with open('./mysystem/messages/'+f, 'r') as file:
        content = file.read()
        print(content)
        
if len(files) == 0:
    print('因子全部处于正常状态，没有新的消息')