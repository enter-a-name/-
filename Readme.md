
# 使用方法

首先需要按照requirements.txt安装需要的包，主要包括numpy,pandas,configparser,sklearn，然后可以仿照test.ipynb给出的例子进行使用，所有的函数接口都在test.ipynb进行了详细展示

## 数据加载

加载基本面数据:  fin_stat = internal_data_loader.load_3sheets()
加载量价数据:  pctdf,data = internal_data_loader.load_processed_prices()

## 单因子回测

对于不希望干预过多细节的研究员，建议使用一站式服务接口：factor_test.wrapup_test(pctdf,data,factor_function,require_submit=True,detailed=True)，这个函数会自动完成所有测试，给出详细结果，并且尝试向因子库提交

对于希望逐步完成得到中间结果的研究员，建议使用：

截面策略：
factor = factor_constructor.get_price_factor(data,rolling5) 或是 factor=factor_constructor.get_finstat_factor(fin_stat,info_name,pctdf)
returns = factor_test.single_factor_backtest(pctdf,factor)
factor_test.show(returns)
factor_test.submit(factor,returns,'因子名','因子说明')

CTA策略（假设买入/卖出阈值分别为buy_threshold，sell_threshold）：
factor = factor_constructor.get_price_factor(data,rolling5) 或是 factor=factor_constructor.get_finstat_factor(fin_stat,info_name,pctdf)
returns = factor_test.single_factor_backtest(pctdf,factor,cta=True,sell_threshold=bound1,buy_threshold=bound2)
factor_test.show(returns)
factor_test.submit(factor,returns,'因子名','因子说明')


## 因子库管理

## 组合回测

因子预处理：

# 数据来源
手动下载的rice quant数据，包含了每个个股每日的风格敞口和行业，手动用mysytem./preproc/preproc.ipynb整理成风格收益和行业收益，存储在newdata文件夹