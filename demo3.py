from __future__ import (absolute_import, division, print_function, unicode_literals)#向前兼容python2

import backtrader as bt
import datetime
import pandas as pd


class MyStrategy(bt.Strategy):#继承bt.Strategy类
    def __init__(self):
        self.bt_sma = bt.indicators.MovingAverageSimple(self.data) #赋值给this.bt_sma(随便起名字),plot()函数会自动标出移动平均线
        #默认画30days均线

    def start(self):
        print("start")

    def prenext(self):#目前暂时没有
        print("prenext")

    def next(self):#next的策略核心，如果是分钟线，每过1分钟调用一次，日线则每过一天调用一次，取决于数据间隔
        pass


    def stop(self):
        print("stop")




cerebro = bt.Cerebro()

data0 = pd.read_csv(r'C:\Users\Admin\Documents\Programming\BacktraderTest\priceData.csv')

#create data feed
data0['tradeDate'] = pd.to_datetime(data0['tradeDate'])#必须转成时间戳格式
data0.set_index('tradeDate', inplace=True)
data0['openinterest'] = 0
data0.dropna()
data0 = data0.rename(columns={'turnoverVol' : 'volume'})#column重命名
data0 = data0.rename(columns={'openPrice' : 'open'})
data0 = data0.rename(columns={'highestPrice' : 'high'})
data0 = data0.rename(columns={'lowestPrice' : 'low'})
data0 = data0.rename(columns={'closePrice' : 'close'})
brf_daily = bt.feeds.PandasData(dataname = data0, fromdate = datetime.datetime(2020, 9, 16), todate = datetime.datetime(2021, 6, 25))
#fromdate回测起始时间

#add data feed to cerebro
cerebro.adddata(brf_daily)

#add strategy
cerebro.addstrategy(MyStrategy)

#run
cerebro.run()

#plot
#cerebro.plot()
cerebro.plot(style = 'candle')#画成蜡烛图

