from __future__ import (absolute_import, division, print_function, unicode_literals)  # 向前兼容python2

import backtrader as bt
import datetime
import pandas as pd



class half_half_balance(bt.Strategy):  # 继承bt.Strategy类
    def __init__(self):
        pass;




    def start(self):
        print("start")

    def prenext(self):  # 目前暂时没有
        print("prenext")

    def next(self):
        today = self.data.datetime.date()
        year, month = today.year, today.month
        if month == 12:
            # 获取本月有多少天
            this_month_length = (datetime.datetime(year + 1, 1, 1) - datetime.datetime(year, month, 1)).days
        else:
            this_month_length = (datetime.datetime(year, month + 1, 1) - datetime.datetime(year, month, 1)).days

        if today.day == this_month_length:  # 今天是月末最后一天
            #self.order_target_percent(target=0.45, data='SZZS')  # 把资产买卖到target的百分比
            self.order_target_percent(target=0.45, data='NASDAQ') #不能把仓位打满，留一些做流动性，扣费用之类的
            self.order_target_percent(target=0.45, data='SZQZ')

    def stop(self):
        print("stop")


if __name__ == '__main__':
    cerebro = bt.Cerebro()  # 关闭默认的observer，即取消默认的cash，value,买卖点的图

    data0 = pd.read_hdf(r'processed_data.h5', key = 'data')

    # create data feed
    for col_name in data0.columns:
        dataframe = data0[[col_name]]#读取h5数据格式的方式，不同于csv data0['NASDAQ'], 用data0[['NASDAQ']]
        for col in ['open', 'high', 'low', 'close']:#open,high,low,close,全部看成当天的净值
            dataframe[col] = dataframe[col_name]#整列赋值
        dataframe['volume'] = 1000000000#整列赋值
        datafeed = bt.feeds.PandasData(dataname = dataframe)#add4个datafeed，分别是nasdaq，nikkei，szzs，。。。
        cerebro.adddata(datafeed, name=col_name)

    # add strategy
    cerebro.addstrategy(half_half_balance)  # 设置初始资金20000


    # run

    cerebro.run()  # 会返回分析结果,如果有两个策略，则分开分析
    print('value', cerebro.broker.get_value())


    # plot
    # cerebro.plot()
    cerebro.plot(style='candle', volume = False)  # 画成蜡烛图







