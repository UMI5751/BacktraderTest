from __future__ import (absolute_import, division, print_function, unicode_literals)#向前兼容python2

import backtrader as bt
import datetime
import pandas as pd


class MyStrategy(bt.Strategy):#继承bt.Strategy类
    pass

cerebro = bt.Cerebro()

data0 = pd.read_csv('priceData.csv')

#create data feed
data0['tradeDate'] = pd.to_datetime(data0['tradeDate'])#必须转成时间戳格式
data0.set_index('tradeDate', inplace=True)
data0['openinterest'] = 0
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

