作者：胡沛骅

# 使用方法

首先需要按照requirements.txt安装需要的包，主要包括numpy,pandas,matplotlib,configparser,sklearn,lightgbm，然后可以仿照test.ipynb给出的例子进行使用，所有的函数接口都在test.ipynb进行了详细展示

使用前，请先import系统：

from mysystem.factor_test import internal_data_loader, factor_constructor, factor_test

from mysystem import managing

from mysystem.portfolio_test import portfolio_backtest, portfolio_construct

## 数据加载

加载基本面数据:  fin_stat = internal_data_loader.load_3sheets()

加载量价数据:  pctdf,data = internal_data_loader.load_processed_prices()

## 单因子回测

### 量价策略一站式测试提交

对于不希望干预过多细节的研究员，建议使用一站式服务接口：factor_test.wrapup_test(pctdf,data,factor_function,require_submit=True,detailed=True)

这个函数会自动完成所有测试，给出详细结果，并且尝试向因子库提交，默认为截面策略，CTA(时序)策略只需设置可选参数cta=True，并设置买入卖出阈值即可

对于希望逐步完成得到中间结果的研究员，建议使用：

### 截面策略：

量价因子：factor = factor_constructor.get_price_factor(data,factor_function) 

基本面因子：factor=factor_constructor.get_finstat_factor(fin_stat,info_name,pctdf)

其中，指定时间区间请用可选参数startdate，enddate指定，详见test.ipynb的例子

returns = factor_test.single_factor_cta_backtest(pctdf,factor)

factor_test.show(returns)

factor_test.submit(factor,returns,'因子名','因子说明')


### CTA策略（假设买入/卖出阈值分别为buy_threshold，sell_threshold）：

量价因子：factor = factor_constructor.get_price_factor(data,factor_function)

基本面因子：factor=factor_constructor.get_finstat_factor(fin_stat,info_name,pctdf)

其中，指定时间区间请用可选参数startdate，enddate指定，详见test.ipynb的例子

returns = factor_test.single_factor_cta_backtest(pctdf,factor,cta=True,sell_threshold=...,buy_threshold=...)

factor_test.show(returns,cta = True)

factor_test.submit(factor,returns,'因子名','因子说明')

如果需要详细的结果，请使用factor_test.show(returns,detailed=True)

## 因子库管理

清空因子库（不可撤销）：managing.delete_all_factors() 需要输入y/n确认

展示所有因子及其收益相关性：managing.view_all_factors()

修改因子入库标准：managing.set_threshold() 该函数会改写mysytem/config.ini

打回因子：managing.rebute('因子名','打回理由') 该函数会把因子加上DEPRECATED前缀，并且留下一条提示，因子被打回后，研究员启动系统时会收到提示

## 组合回测

### 组合构建

加载因子数据：features, ret = portfolio_construct.load_features() 该函数默认忽略已被打回的因子，可以通过可选参数ignore_deprecated=False调整

初始化投资组合：portfolio_construct.Portfolio(pctdf, features, ret)

因子预处理：

PCA：my_portfolio.feature_preproc(method='pca', n_components = n)

标准化：my_portfolio.feature_preproc(method='standardize')

构建投资组合：my_portfolio.construct_portfolio(method)，其中equal_weight/effecient_frontier/ml，分别代表有效前沿/等权组合/机器学习构建的组合

### 组合评价

一站式函数：

wrapped_portfolio_test(portfolio)

可选参数 require_return 控制是否给出中间值，默认False

可选参数 detailed 控制是否输出图表，默认False

# 数据来源

手动下载的rice quant数据，包含了每个个股每日的风格敞口和行业，手动用mysytem/preproc/preproc.ipynb整理成风格收益和行业收益，存储在newdata文件夹
