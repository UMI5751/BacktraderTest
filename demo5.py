from __future__ import (absolute_import, division, print_function, unicode_literals)#向前兼容python2

import backtrader as bt
import datetime
import pandas as pd


class MyStrategy(bt.Strategy):#继承bt.Strategy类
    def __init__(self):
        self.bt_sma = bt.indicators.MovingAverageSimple(self.data, period = 24) #赋值给this.bt_sma(随便起名字),plot()函数会自动标出移动平均线
        #默认画30days均线, 可以指定period参数更改天数
        #在指标还不能计算，即未形成时（30天移动均线的前29天）会调用prenext
        self.buy_sell_signal = bt.indicators.CrossOver(self.data.close, self.bt_sma)#两个值如果上传，则return 1，下穿return -1，else return 0
        #self.buy_sell_signal本质上还是indicator，即一个line

    def start(self):
        print("start")

    def prenext(self):#目前暂时没有
        print("prenext")

    def next(self):#next的策略核心，如果是分钟线，每过1分钟调用一次，日线则每过一天调用一次，取决于数据间隔
        ma_value = self.bt_sma[0];#获取当日移动均线价格
        ma_value_yesterday = self.bt_sma[-1]#之前的判断代码有问题，修正

        # if self.data.close[0] > ma_value and self.data.close[-1] < ma_value_yesterday:#今天高于&昨天低于5日均价，则买入
        #     print('long', self.data.datetime.date(), self.data.close[0])#获取当日日期用.datetime
        #     self.order = self.buy(size = 100)#执行买入，买入10000手
        #
        # if self.data.close[0] < ma_value and self.data.close[-1] > ma_value_yesterday:#今天低于&昨天高于5日均价
        #     print('short', self.data.datetime.date(), self.data.close[0])#获取当日日期用.datetime
        #     self.order = self.sell(size = 100)

        #没必要用以上的代码
        if not self.position and self.buy_sell_signal[0] == 1:#如果没有仓位（空仓）且向上突破均线
            self.order = self.buy(size = 20)
        if not self.position and self.buy_sell_signal[0] == -1:
            self.order = self.sell(size = 20)

        if self.position and self.buy_sell_signal[0] == 1:#self.position 会返回bool值
            self.order = self.close()#上穿均线了，如果之前有仓位（必定是空仓），则把之前的仓位先平掉，再开仓做多
            self.order = self.buy(size = 20)

        if self.position and self.buy_sell_signal[0] == -1:
            self.order = self.close()
            self.order = self.sell(size = 20)



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

